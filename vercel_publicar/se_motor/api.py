"""Enrutador del API, independiente del servidor HTTP.

Lo usa servidor.py, tanto en el equipo local como en Hugging Face Spaces, para
que el comportamiento sea identico en las dos partes.

Rutas:
  GET  /api/salud                 -> estado, version de la base y modelo de IA configurado
  GET  /api/categorias            -> categorias de diagnostico
  POST /api/se/diagnostico        -> un turno con NUESTRO sistema experto
  POST /api/gemini/diagnostico    -> un turno con el servicio de IA (Gemini)

Configuracion (variables de entorno; en Hugging Face se definen como "Secrets"):
  GEMINI_CLAVE    clave de la API de Gemini (Google AI Studio). Sin ella, /api/gemini responde 503.
  GEMINI_MODELO   modelo a usar (por defecto gemini-3.5-flash-lite)
  GEMINI_RAZONAMIENTO  nivel de razonamiento ("low", "medium", "high") para los modelos que lo admiten
  KB_RUTA         ruta de kb_se_vivienda.json   (por defecto, en la carpeta del servicio)
  REGLAS_RUTA     ruta de reglas_para_gemini.md (por defecto, en la carpeta del servicio)
"""
import os
import time
from pathlib import Path

from .servicios import (ClienteGemini, ErrorPeticion, LimiteAlcanzado, ServicioGemini, ServicioNoConfigurado,
                        ServicioSE)

RAIZ = Path(__file__).resolve().parents[1]
MODELO_POR_DEFECTO = "gemini-3.5-flash-lite"
_servicios = {}


def servicios() -> dict:
    if not _servicios:
        se = ServicioSE(os.environ.get("KB_RUTA") or RAIZ / "kb_se_vivienda.json")
        cliente = None
        if os.environ.get("GEMINI_CLAVE"):
            reglas = Path(os.environ.get("REGLAS_RUTA") or RAIZ / "reglas_para_gemini.md").read_text(encoding="utf8")
            cliente = ClienteGemini(os.environ["GEMINI_CLAVE"], os.environ.get("GEMINI_MODELO", MODELO_POR_DEFECTO),
                                    reglas, os.environ.get("GEMINI_RAZONAMIENTO") or None)
        _servicios.update(se=se, gemini=ServicioGemini(cliente, se.repo))
    return _servicios


def atender(metodo: str, ruta: str, cuerpo: dict | None) -> tuple[int, dict]:
    """Devuelve (codigo HTTP, cuerpo JSON). Nunca lanza excepciones hacia el servidor."""
    t0 = time.perf_counter()
    try:
        s = servicios()
        if metodo == "GET" and ruta == "/api/salud":
            repo, cliente = s["se"].repo, s["gemini"].cliente
            r = {"estado": "ok", "base_exportada": repo.exportado, "huella_base": repo.huella[:16],
                 "categorias": len(repo.categorias()), "modelo_ia": cliente.modelo if cliente else None}
        elif metodo == "GET" and ruta == "/api/categorias":
            r = {"categorias": s["se"].categorias()}
        elif metodo == "POST" and ruta in ("/api/se/diagnostico", "/api/gemini/diagnostico"):
            r = s["se" if "/se/" in ruta else "gemini"].diagnosticar(cuerpo or {})
        else:
            return 404, {"error": f"Ruta no encontrada: {metodo} {ruta}"}
        r["tiempo_ms"] = round((time.perf_counter() - t0) * 1000, 1)
        return 200, r
    except ErrorPeticion as e:
        return 400, {"error": str(e)}
    except ServicioNoConfigurado as e:
        return 503, {"error": str(e)}
    except LimiteAlcanzado as e:
        return 429, {"error": str(e)}
    except Exception as e:  # el cliente recibe el error en JSON; el detalle queda en los registros
        return 500, {"error": f"{type(e).__name__}: {e}"}
