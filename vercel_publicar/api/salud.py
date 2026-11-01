"""Funcion de Vercel: GET /api/salud (ver se_motor/api.py)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from se_motor.vercel import crear_manejador  # noqa: E402

handler = crear_manejador("/api/salud", "GET")
