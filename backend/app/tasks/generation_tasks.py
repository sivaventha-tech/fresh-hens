"""
Celery background tasks for project generation.
Runs the full agent pipeline asynchronously.
"""
from celery import Celery
from loguru import logger
from app.core.config import settings

celery_app = Celery(
    "ai_project_gen",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


@celery_app.task(bind=True, name="tasks.generate_project", max_retries=1)
def generate_project_task(self, project_id: str, project_data: dict):
    """
    Celery task: runs the agent orchestrator for a project.
    Called from the /generate/project API endpoint.
    """
    import asyncio
    from app.agents.orchestrator import ProjectOrchestrator
    from app.core.database import AsyncSessionLocal
    from app.services.zip_service import zip_service

    logger.info(f"[Celery] Starting generation task for project {project_id}")

    async def _run():
        async with AsyncSessionLocal() as db:
            orchestrator = ProjectOrchestrator()
            ctx = await orchestrator.run(
                project_id=project_id,
                title=project_data["title"],
                category=project_data["category"],
                technologies=project_data["technologies"],
                features=project_data["features"],
                complexity=project_data["complexity"],
                db=db,
            )
            # Save ZIP to disk
            if ctx.files:
                zip_path = zip_service.save_zip_to_disk(project_id, ctx.files)
                from sqlalchemy import select
                from app.models.project import Project
                result = await db.execute(select(Project).where(Project.id == project_id))
                project = result.scalar_one_or_none()
                if project:
                    project.zip_path = zip_path
                    await db.commit()
            return {"status": "done", "files_count": len(ctx.files)}

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_run())
        loop.close()
        logger.success(f"[Celery] Project {project_id} done: {result}")
        return result
    except Exception as exc:
        logger.error(f"[Celery] Task failed for {project_id}: {exc}")
        raise self.retry(exc=exc, countdown=5)
