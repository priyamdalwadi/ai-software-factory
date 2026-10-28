"""HTTP entry point. Workers and release authority will be separate components."""

from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: Literal["ai-software-factory"] = "ai-software-factory"


def create_app() -> FastAPI:
    application = FastAPI(title="AI Software Factory", version="0.1.0")

    @application.get("/healthz", response_model=HealthResponse, tags=["operations"])
    def health() -> HealthResponse:
        """Liveness only; does not claim worker or database readiness."""
        return HealthResponse()

    return application


app = create_app()
