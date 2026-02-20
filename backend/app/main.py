from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.simulation import router as simulation_router
from app.simulation.config import ConfigValidationError

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(simulation_router)

@app.exception_handler(ConfigValidationError)
async def config_validation_handler(request: Request, exc: ConfigValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": str(exc),
                "details": {
                    "field": getattr(exc, "field", None)
                },
            }
        },
    )
