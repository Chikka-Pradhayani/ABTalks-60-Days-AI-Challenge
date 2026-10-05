"""Root production server entrypoint for Railway and Docker containers.

Imports the production FastAPI application from day-53/backend/main.py
and runs with uvicorn respecting dynamic PORT allocation.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "day-53", "backend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from main import app  # noqa: F401

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8001"))
    host = os.environ.get("HOST", "0.0.0.0")
    uvicorn.run("server:app", host=host, port=port)
