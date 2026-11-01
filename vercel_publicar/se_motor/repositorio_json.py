"""Capa de datos para la nube: la base de conocimiento leida desde un JSON.

Implementa las mismas consultas granulares que RepositorioConocimiento
(aplicacion/se_app/datos/repositorio_conocimiento.py), pero sobre el archivo
kb_se_vivienda.json exportado de MySQL. Asi el motor bayesiano corre en una
funcion serverless sin base de datos, y sin cambiar una linea de su logica.
"""
import json
from pathlib import Path

from .modelos import Antecedente, Hipotesis, Pregunta


class RepositorioJSON:
    def __init__(self, ruta: str | Path):
        base = json.loads(Path(ruta).read_text(encoding="utf8"))
        self.huella = base.get("huella_sha256", "")
        self.exportado = base.get("exportado", "")
        self._categorias = base["categorias"]
        self._preguntas = [Pregunta(p["codigo"], p["categoria"], p["texto_pregunta"], p["enunciado_positivo"],
                                    p["enunciado_negativo"]) for p in base["preguntas"]]
        self._hipotesis = {h["codigo"]: Hipotesis(h["codigo"], h["categoria"], h["diagnostico"], h["nivel_urgencia"],
                                                  int(h["factor_certeza"]), h["especialista"], h["accion_recomendada"],
                                                  bool(h["validada"]), h.get("fuente"))
                           for h in base["hipotesis"]}
        self._condiciones = sorted(base["condiciones"], key=lambda c: (c["hipotesis"], c["orden"]))
        self.consultas = 0          # consultas granulares atendidas (para el analisis comparativo)

    # ------------------------------------------------------------ misma interfaz que RepositorioConocimiento

    def categorias(self) -> list[dict]:
        return list(self._categorias)

    def preguntas_de_categoria(self, categoria: str) -> list[Pregunta]:
        return [p for p in self._preguntas if p.categoria == categoria]

    def hipotesis_activas(self, categoria: str) -> list[Hipotesis]:
        self.consultas += 1
        return sorted((h for h in self._hipotesis.values() if h.categoria == categoria), key=lambda h: h.codigo)

    def antecedentes_de_pregunta(self, pregunta: str) -> list[Antecedente]:
        self.consultas += 1
        return [Antecedente(c["hipotesis"], c["pregunta"], int(c["valor_respuesta"]))
                for c in self._condiciones if c["pregunta"] == pregunta]

    def antecedentes_de_hipotesis(self, hipotesis: str) -> list[Antecedente]:
        self.consultas += 1
        return [Antecedente(c["hipotesis"], c["pregunta"], int(c["valor_respuesta"]))
                for c in self._condiciones if c["hipotesis"] == hipotesis]

    def hipotesis(self, codigo: str) -> Hipotesis | None:
        return self._hipotesis.get(codigo)

    def pregunta(self, codigo: str) -> Pregunta | None:
        return next((p for p in self._preguntas if p.codigo == codigo), None)
