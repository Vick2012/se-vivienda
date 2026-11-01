# Sistema experto de diagnóstico de vivienda, como servicio

Proyecto de Sistemas Expertos, Universidad Manuela Beltrán (2026). Lina María Briñez Rodríguez y Víctor Alfonso Alarcón Ospina.

Dos sistemas con la **misma base de conocimiento** (7 categorías, 36 preguntas, 49 reglas If / And / Then) y el mismo API:

| Ruta | Sistema |
|---|---|
| `POST /api/se/diagnostico` | Nuestro motor de inferencia bayesiano |
| `POST /api/gemini/diagnostico` | Gemini (IA generativa de Google) con las mismas reglas |
| `GET /api/categorias`, `GET /api/salud` | Consulta de categorías y estado |

La interfaz web (`public/`) consume el API. La clave de Gemini se define en Vercel como variable de entorno `GEMINI_CLAVE`.
