"""Funcion de Vercel: POST /api/se/diagnostico (ver se_motor/api.py)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from se_motor.vercel import crear_manejador  # noqa: E402

handler = crear_manejador("/api/se/diagnostico", "POST")
