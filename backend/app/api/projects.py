"""
Projects API — generate, list, get, download, status polling.
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
import io

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.generation import GenerationLog
from app.schemas.project import (
    ProjectCreate, ProjectResponse, ProjectListItem,
    ProjectStatusResponse, GenerationLogResponse
)
from app.agents.orchestrator import ProjectOrchestrator
from app.services.zip_service import zip_service
from app.agents.base_agent import PROGRESS_MAP

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/generate", response_model=ProjectResponse, status_code=202)
async def generate_project(
    payload: ProjectCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start AI project generation. Returns immediately; runs in background."""
    if not current_user.can_generate:
        raise HTTPException(
            status_code=429,
            detail=f"Generation limit reached ({current_user.generation_limit}/mo). Upgrade your plan.",
        )

    project = Project(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        title=payload.title,
        category=payload.category.value,
        technologies=payload.technologies,
        features=payload.features,
        complexity=payload.complexity.value,
        status="pending",
    )
    db.add(project)
    current_user.generations_used += 1
    await db.commit()
    await db.refresh(project)

    # Run pipeline in background
    background_tasks.add_task(
        _run_generation_background,
        project_id=project.id,
        payload=payload,
        db_session_factory=db.__class__,
    )

    return ProjectResponse.model_validate(project)


async def _run_generation_background(project_id: str, payload, db_session_factory):
    """Background task: runs full agent pipeline."""
    from app.core.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        orchestrator = ProjectOrchestrator()
        ctx = await orchestrator.run(
            project_id=project_id,
            title=payload.title,
            category=payload.category.value,
            technologies=payload.technologies,
            features=payload.features,
            complexity=payload.complexity.value,
            db=db,
        )
        if ctx.files:
            zip_path = zip_service.save_zip_to_disk(project_id, ctx.files)
            result = await db.execute(select(Project).where(Project.id == project_id))
            project = result.scalar_one_or_none()
            if project:
                project.zip_path = zip_path
                await db.commit()


@router.get("/", response_model=List[ProjectListItem])
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 20,
):
    result = await db.execute(
        select(Project)
        .where(Project.user_id == current_user.id)
        .order_by(desc(Project.created_at))
        .offset(skip)
        .limit(limit)
    )
    return [ProjectListItem.model_validate(p) for p in result.scalars().all()]


@router.get("/{project_id}/status", response_model=ProjectStatusResponse)
async def get_project_status(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    logs_result = await db.execute(
        select(GenerationLog)
        .where(GenerationLog.project_id == project_id)
        .order_by(GenerationLog.created_at)
    )
    logs = logs_result.scalars().all()

    # Calculate progress from last completed agent
    progress = 0
    for log in logs:
        if log.status == "done":
            progress = PROGRESS_MAP.get(log.agent_name, progress)

    return ProjectStatusResponse(
        project_id=project_id,
        status=project.status,
        logs=[GenerationLogResponse.model_validate(l) for l in logs],
        progress_percent=progress,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse.model_validate(project)


@router.get("/{project_id}/download")
async def download_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Stream the generated ZIP file for download."""
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.status != "done":
        raise HTTPException(status_code=400, detail=f"Project status is '{project.status}', not done yet")
    if not project.files:
        raise HTTPException(status_code=404, detail="No generated files found")

    zip_bytes = zip_service.create_zip_bytes(project.files)
    safe_title = "".join(c if c.isalnum() or c in "-_" else "_" for c in project.title)

    return StreamingResponse(
        io.BytesIO(zip_bytes),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{safe_title}.zip"'},
    )
