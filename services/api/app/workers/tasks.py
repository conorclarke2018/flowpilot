import uuid

from app.db.session import SessionLocal
from app.services.runs import execute_run
from app.workers.celery_app import celery_app


@celery_app.task(name="workflows.execute_run")
def execute_run_task(run_id: str) -> str:
    db = SessionLocal()
    try:
        run = execute_run(db, run_id=uuid.UUID(run_id))
        return run.status
    finally:
        db.close()
