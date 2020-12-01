# fastapi_code.py

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Main app config -- store system variables here
from config import Settings

# Route config -- works the same in Flask for declarive definition of routes to views.
from routes import routes

# Settings if you want it available in this context
config  = Settings()

# Main app instance that runs the server
app     = FastAPI(routes=routes)
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run("station_viz:app", port=8001)
