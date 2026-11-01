"""Los dos sistemas expertos que se comparan, expuestos con el MISMO contrato.

Peticion (igual para ambos):
    {"categoria": "ELE",
     "respuestas": [{"pregunta": "olor_quemado", "valor": 1}, ...]}   # todas las dadas, en orden

Respuesta:
    {"motor": "se" | "gemini",
     "estado": "pregunta" | "diagnostico" | "sin_diagnostico" | "invalida",
     "pregunta": {"codigo", "texto"} | null,
     "diagnostico": {"codigo", "nombre", "urgencia", "certeza", "especialista", "accion", "probabilidad"} | null,
     "detalle": {...}}      # lo que cada sistema puede explicar (ranking, justificacion, tokens...)

ServicioSE      -> nuestro motor bayesiano (copia exacta de la aplicacion) sobre la base en JSON.
ServicioGemini  -> el modelo de IA generativa de Google (API de Gemini) con las MISMAS reglas
                   como base de conocimiento. Su salida se valida contra la base: si nombra una
                   pregunta o una regla que no existe, el turno queda como "invalida".

Ambos servicios son sin estado: el cliente envia en cada turno todas las respuestas dadas.
"""
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

from .inferencia_bayesiana import MotorBayesiano
from .modelos import Evidencia
from .repositorio_json import RepositorioJSON

ACCIONES_INMEDIATAS = {   # mismas de ServicioDiagnostico (CU04) en la aplicacion
    "GAS": ["Ventile: abra puertas y ventanas", "No encienda ni apague interruptores, ni use llamas",
            "Cierre la llave de paso del gas y salga de la vivienda",
            "Llame a la línea de emergencias de su empresa de gas"],
    "ELE": ["Baje el breaker de la zona o el principal", "No vuelva a conectar nada en esa zona",
            "Si ve humo o llama, salga y llame al 123"],
    "EST": ["Salga de la zona afectada y no vuelva a entrar", "Aleje a las personas de muros y columnas inclinados",
            "Llame al 123 si hay riesgo de colapso"],
}


class ErrorPeticion(ValueError):
    """La peticion no cumple el contrato (categoria o respuestas invalidas)."""


def leer_peticion(cuerpo: dict, categorias: set[str]) -> tuple[str, list[Evidencia], None]:
    categoria = str(cuerpo.get("categoria", "")).upper()
    if categoria not in categorias:
        raise ErrorPeticion(f"Categoría desconocida: {categoria!r}. Use una de {sorted(categorias)}.")
    respuestas = cuerpo.get("respuestas") or []
    if not isinstance(respuestas, list):
        raise ErrorPeticion("'respuestas' debe ser una lista de {pregunta, valor}.")
    try:
        evidencias = [Evidencia(str(r["pregunta"]), 1 if int(r["valor"]) else 0) for r in respuestas]
    except (KeyError, TypeError, ValueError):
        raise ErrorPeticion("Cada respuesta debe tener 'pregunta' (código) y 'valor' (1 = Sí, 0 = No).")
    return categoria, evidencias, None


# ====================================================================== nuestro sistema experto

class ServicioSE:
    HIPOTESIS_REPORTADAS = 5

    def __init__(self, ruta_kb: str | Path):
        self.repo = RepositorioJSON(ruta_kb)
        self.motor = MotorBayesiano(self.repo)

    def categorias(self) -> list[dict]:
        return self.repo.categorias()

    def diagnosticar(self, cuerpo: dict) -> dict:
        categoria, evidencias, _ = leer_peticion(cuerpo, {c["codigo"] for c in self.repo.categorias()})
        validas = {p.codigo for p in self.repo.preguntas_de_categoria(categoria)}
        if any(e.pregunta not in validas for e in evidencias):
            raise ErrorPeticion("Hay respuestas a preguntas que no son de esta categoría.")
        consultas_antes = self.repo.consultas
        decision = self.motor.decidir(categoria, evidencias)
        dist = decision.distribucion
        reglas = [hp for hp in dist.ranking() if not hp.hipotesis.es_h0][:self.HIPOTESIS_REPORTADAS]
        ranking = sorted(reglas + [hp for hp in dist.ranking() if hp.hipotesis.es_h0], key=lambda hp: -hp.probabilidad)
        detalle = {
            "ranking": [{"codigo": hp.hipotesis.codigo, "nombre": hp.hipotesis.diagnostico,
                         "probabilidad": round(hp.probabilidad, 4)} for hp in ranking],
            "entropia_bits": round(dist.entropia(), 4),
            "consultas_granulares": self.repo.consultas - consultas_antes,
        }
        base = {"motor": "se", "pregunta": None, "diagnostico": None, "detalle": detalle}
        if not decision.concluye:
            p = decision.pregunta
            detalle["ganancia_bits"] = round(decision.ganancia, 4)
            return {**base, "estado": "pregunta", "pregunta": {"codigo": p.codigo, "texto": p.texto}}

        lider = decision.conclusion
        trayectoria = self.motor.traza(categoria, evidencias)
        preguntas = {p.codigo: p for p in self.repo.preguntas_de_categoria(categoria)}
        detalle["explicacion"] = [
            {**f, "texto": preguntas[f["pregunta"]].enunciado(f["valor"]),
             "antes": round(f["antes"], 4), "despues": round(f["despues"], 4)}
            for f in self.motor.aportes(evidencias, trayectoria, lider.codigo)]
        if lider.es_h0:
            return {**base, "estado": "sin_diagnostico"}
        detalle["acciones_inmediatas"] = ACCIONES_INMEDIATAS.get(categoria, []) if lider.urgencia == "Critica" else []
        return {**base, "estado": "diagnostico", "diagnostico": {
            "codigo": lider.codigo, "nombre": lider.diagnostico, "urgencia": lider.urgencia,
            "certeza": lider.certeza, "especialista": lider.especialista, "accion": lider.accion,
            "probabilidad": round(dist.probabilidad(lider.codigo), 4)}}


# ====================================================================== servicio de IA: Gemini

ESQUEMA_RESPUESTA = {   # salida estructurada que se exige al modelo (generationConfig.responseSchema)
    "type": "OBJECT",
    "properties": {
        "accion": {"type": "STRING", "enum": ["preguntar", "diagnosticar", "sin_diagnostico"]},
        "pregunta": {"type": "STRING", "description": "Código de la pregunta, si accion = preguntar"},
        "hipotesis": {"type": "STRING", "description": "Código de la regla, si accion = diagnosticar"},
        "justificacion": {"type": "STRING", "description": "Por qué, en una o dos frases"},
        "confianza": {"type": "INTEGER", "description": "0 a 100"},
    },
    "required": ["accion", "justificacion", "confianza"],
}

INSTRUCCIONES = """Eres un sistema experto de diagnóstico de fallas en viviendas.
Tu ÚNICA fuente de conocimiento es la base de reglas que aparece al final. No uses conocimiento externo.

Procedimiento, en cada turno:
1. El usuario eligió una categoría y respondió algunas preguntas (Sí o No).
2. Si las respuestas ya cumplen TODAS las condiciones de una regla de esa categoría, responde
   accion = "diagnosticar" con el código de esa regla en "hipotesis".
3. Si ninguna regla de la categoría puede cumplirse ya con las respuestas dadas, responde
   accion = "sin_diagnostico".
4. Si no, responde accion = "preguntar" con el código de UNA pregunta de esa categoría que aún
   no se haya respondido y que ayude a decidir entre las reglas posibles.
Usa solo códigos que existan en la base. No inventes reglas, preguntas ni diagnósticos.
Responde únicamente con el JSON pedido.

"""


class ClienteGemini:
    """Cliente REST de la API de Gemini (Google AI Studio)."""
    URL = "https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
    ESPERAS = (4, 10, 20)     # segundos entre reintentos cuando el servicio responde 500/503 (saturacion)

    def __init__(self, clave: str, modelo: str, reglas: str, razonamiento: str | None = None):
        self.clave, self.modelo = clave, modelo
        self.razonamiento = razonamiento          # "low" / "medium" / "high" en los modelos Gemini 3 que lo admiten
        self.instrucciones = INSTRUCCIONES + reglas
        self.reintentos = 0

    def generar(self, mensaje: str) -> dict:
        config = {"temperature": 0, "responseMimeType": "application/json", "responseSchema": ESQUEMA_RESPUESTA}
        if self.razonamiento:
            config["thinkingConfig"] = {"thinkingLevel": self.razonamiento}
        cuerpo = {
            "systemInstruction": {"parts": [{"text": self.instrucciones}]},
            "contents": [{"role": "user", "parts": [{"text": mensaje}]}],
            "generationConfig": config,
        }
        self.reintentos = 0
        for intento in range(len(self.ESPERAS) + 1):
            req = urllib.request.Request(self.URL.format(modelo=self.modelo), data=json.dumps(cuerpo).encode(),
                                         method="POST", headers={"x-goog-api-key": self.clave,
                                                                 "Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    return json.loads(r.read())
            except urllib.error.HTTPError as e:
                detalle = e.read().decode(errors="replace")[:400]
                if e.code in (500, 503) and intento < len(self.ESPERAS):
                    # Saturacion temporal del servicio: se reintenta y se cuenta (metrica de disponibilidad).
                    self.reintentos += 1
                    time.sleep(self.ESPERAS[intento])
                    continue
                if e.code == 429:
                    raise LimiteAlcanzado(f"Gemini: límite del nivel gratuito alcanzado (429). {detalle}") from e
                raise RuntimeError(f"Gemini respondió {e.code}: {detalle}") from e


class LimiteAlcanzado(RuntimeError):
    """El servicio de IA rechazo la peticion por cuota (HTTP 429)."""


class ServicioGemini:
    """Mismo contrato que ServicioSE, pero la decision la toma un modelo de IA generativa
    que recibe las mismas reglas como base de conocimiento."""

    def __init__(self, cliente: ClienteGemini | None, kb: RepositorioJSON):
        self.cliente = cliente
        self.kb = kb

    def diagnosticar(self, cuerpo: dict) -> dict:
        categoria, evidencias, _ = leer_peticion(cuerpo, {c["codigo"] for c in self.kb.categorias()})
        if self.cliente is None:
            raise ServicioNoConfigurado("Falta GEMINI_CLAVE: el servicio de IA no está configurado.")
        preguntas = {p.codigo: p for p in self.kb.preguntas_de_categoria(categoria)}
        nombre = next(c["nombre"] for c in self.kb.categorias() if c["codigo"] == categoria)
        dadas = "; ".join(f"{e.pregunta} = {'Sí' if e.valor else 'No'}" for e in evidencias) or "ninguna todavía"
        mensaje = f"Categoría elegida: {categoria} ({nombre}).\nRespuestas dadas: {dadas}."

        t0 = time.perf_counter()
        crudo = self.cliente.generar(mensaje)
        ms = round((time.perf_counter() - t0) * 1000, 1)
        uso = crudo.get("usageMetadata", {})
        texto = "".join(p.get("text", "") for p in
                        (crudo.get("candidates") or [{}])[0].get("content", {}).get("parts", []))
        detalle = {"modelo": self.cliente.modelo, "latencia_servicio_ms": ms,
                   "reintentos": self.cliente.reintentos, "tokens_entrada": uso.get("promptTokenCount"), "tokens_salida": uso.get("candidatesTokenCount"),
                   "salida_modelo": texto}
        base = {"motor": "gemini", "pregunta": None, "diagnostico": None, "detalle": detalle}
        try:
            salida = json.loads(texto)
        except json.JSONDecodeError:
            return {**base, "estado": "invalida", "detalle": {**detalle, "validacion": "La salida no es JSON válido"}}
        detalle.update(justificacion=salida.get("justificacion"), confianza=salida.get("confianza"))

        # Validacion contra la base de conocimiento: lo que el modelo diga debe existir en ella.
        accion = salida.get("accion")
        respondidas = {e.pregunta for e in evidencias}
        if accion == "preguntar":
            codigo = salida.get("pregunta")
            if codigo not in preguntas:
                motivo = f"Pidió una pregunta que no existe en la categoría: {codigo!r}"
            elif codigo in respondidas:
                motivo = f"Repitió una pregunta ya respondida: {codigo!r}"
            else:
                return {**base, "estado": "pregunta", "pregunta": {"codigo": codigo, "texto": preguntas[codigo].texto}}
            return {**base, "estado": "invalida", "detalle": {**detalle, "validacion": motivo}}
        if accion == "diagnosticar":
            h = self.kb.hipotesis(str(salida.get("hipotesis", "")).upper())
            if h is None or h.categoria != categoria:
                return {**base, "estado": "invalida", "detalle": {
                    **detalle, "validacion": f"Diagnosticó una regla inexistente en la categoría: {salida.get('hipotesis')!r}"}}
            detalle["acciones_inmediatas"] = ACCIONES_INMEDIATAS.get(categoria, []) if h.urgencia == "Critica" else []
            return {**base, "estado": "diagnostico", "diagnostico": {
                "codigo": h.codigo, "nombre": h.diagnostico, "urgencia": h.urgencia, "certeza": h.certeza,
                "especialista": h.especialista, "accion": h.accion, "probabilidad": None}}
        if accion == "sin_diagnostico":
            return {**base, "estado": "sin_diagnostico"}
        return {**base, "estado": "invalida", "detalle": {**detalle, "validacion": f"Acción desconocida: {accion!r}"}}


class ServicioNoConfigurado(RuntimeError):
    """Falta la clave del servicio de IA."""
