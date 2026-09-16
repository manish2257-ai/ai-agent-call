"""
FastAPI Entrypoint for Render and ASGI Servers.
Allows starting the server with:
  uvicorn main:app --host 0.0.0.0 --port $PORT
"""
import os
import uvicorn
from app.main import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
