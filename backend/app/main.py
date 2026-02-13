from fastapi import FastAPI
from app.api.simulation import router as simulation_router

app = FastAPI()

app.include_router(simulation_router)
