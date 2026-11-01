"""Funcion de Vercel: GET /api/categorias (ver se_motor/api.py)."""
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from se_motor.vercel import responder_get, responder_opciones  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        responder_get(self, "/api/categorias")

    def do_OPTIONS(self):
        responder_opciones(self, "GET")
