from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.health import router as health_router
from app.routes.jobs import router as jobs_router
from app.routes.jobs_list import router as jobs_list_router
from app.routes.manual_submissions import router as manual_submissions_router
from app.routes.queue import router as queue_router
from app.routes.source_config import router as source_config_router
from app.routes.sources import router as sources_router
from app.routes.sources_list import router as sources_list_router
from app.routes.workflows import router as workflows_router


def create_app() -> FastAPI:
    app = FastAPI(title="Job Intelligence Agent API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:5174"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    app.include_router(health_router)
    app.include_router(jobs_router)
    app.include_router(jobs_list_router)
    app.include_router(manual_submissions_router)
    app.include_router(queue_router)
    app.include_router(source_config_router)
    app.include_router(sources_router)
    app.include_router(sources_list_router)
    app.include_router(workflows_router)

    return app


app = create_app()
