"""Funcion de Vercel: POST /api/se/diagnostico (ver se_motor/api.py)."""
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from se_motor.vercel import responder_post, responder_opciones  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        responder_post(self, "/api/se/diagnostico")

    def do_OPTIONS(self):
        responder_opciones(self, "POST")
