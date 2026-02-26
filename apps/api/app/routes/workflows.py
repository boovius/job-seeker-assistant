from fastapi import APIRouter

from app.workers.runner import run_once

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("/run-once")
def run_workflow_once():
    run_once()
    return {"status": "ok"}
