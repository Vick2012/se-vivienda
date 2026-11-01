"""Adaptador para las funciones de Python de Vercel.

Vercel convierte cada archivo de la carpeta api/ en una funcion serverless si
define una clase llamada `handler` que hereda de BaseHTTPRequestHandler. Esta
fabrica crea esa clase para una ruta del API, usando el mismo se_motor/api.py
que el servidor local: el comportamiento es identico en las dos partes.
"""
import json
from http.server import BaseHTTPRequestHandler

from .api import atender


def crear_manejador(ruta: str, metodo: str):
    class Manejador(BaseHTTPRequestHandler):
        def _enviar(self, codigo: int, cuerpo: dict):
            datos = json.dumps(cuerpo, ensure_ascii=False).encode()
            self.send_response(codigo)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(datos)

        def do_OPTIONS(self):
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Allow-Methods", f"{metodo}, OPTIONS")
            self.end_headers()

        def do_GET(self):
            if metodo != "GET":
                return self._enviar(405, {"error": f"Use {metodo} en {ruta}"})
            self._enviar(*atender("GET", ruta, None))

        def do_POST(self):
            if metodo != "POST":
                return self._enviar(405, {"error": f"Use {metodo} en {ruta}"})
            largo = int(self.headers.get("Content-Length") or 0)
            try:
                cuerpo = json.loads(self.rfile.read(largo) or b"{}")
            except json.JSONDecodeError:
                return self._enviar(400, {"error": "El cuerpo debe ser JSON."})
            self._enviar(*atender("POST", ruta, cuerpo))

    return Manejador
