"""Adaptador para las funciones de Python de Vercel.

Vercel convierte en funcion serverless cada archivo de api/ que defina, escrita
literalmente, una clase `handler` que hereda de BaseHTTPRequestHandler (la detecta
leyendo el codigo fuente, por eso no sirve generarla con una fabrica). Cada archivo
solo declara su ruta y delega aqui, en el mismo se_motor/api.py del servidor local.
"""
import json

from .api import atender


def _enviar(h, codigo: int, cuerpo: dict):
    datos = json.dumps(cuerpo, ensure_ascii=False).encode()
    h.send_response(codigo)
    h.send_header("Content-Type", "application/json; charset=utf-8")
    h.send_header("Access-Control-Allow-Origin", "*")
    h.send_header("Access-Control-Allow-Headers", "Content-Type")
    h.send_header("Cache-Control", "no-store")
    h.end_headers()
    h.wfile.write(datos)


def responder_get(h, ruta: str):
    _enviar(h, *atender("GET", ruta, None))


def responder_post(h, ruta: str):
    largo = int(h.headers.get("Content-Length") or 0)
    try:
        cuerpo = json.loads(h.rfile.read(largo) or b"{}")
    except json.JSONDecodeError:
        return _enviar(h, 400, {"error": "El cuerpo debe ser JSON."})
    _enviar(h, *atender("POST", ruta, cuerpo))


def responder_opciones(h, metodo: str):
    h.send_response(204)
    h.send_header("Access-Control-Allow-Origin", "*")
    h.send_header("Access-Control-Allow-Headers", "Content-Type")
    h.send_header("Access-Control-Allow-Methods", f"{metodo}, OPTIONS")
    h.end_headers()
