### Dependencies ###
from fastapi import FastAPI

### Imports ###
from routers import customers, gyms, goals, progress

# API Initialisation
app = FastAPI()

@app.get("/")
def read_root():
    text = "the server is up and running"
    version = "V1.3.2"
    return text + " " + version
app.include_router(customers.router)
app.include_router(gyms.router)
app.include_router(goals.router)
app.include_router(progress.router)
