"""
run.py
Starts the Uvicorn server for the Manufacturing AI Copilot FastAPI application.
"""
import uvicorn
from app.config import HOST, PORT

if __name__ == "__main__":
    print(f"Starting Manufacturing AI Copilot Server on http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop the server.")
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=False)