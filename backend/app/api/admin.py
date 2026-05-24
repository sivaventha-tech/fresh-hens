"""
Admin API — user management and analytics. Admin-only endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.models.user import User
from app.models.project import Project
from app.models.generation import GenerationLog
from app.schemas.user import UserResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    result = await db.execute(
        select(User).order_by(desc(User.created_at)).offset(skip).limit(limit)
    )
    return [UserResponse.model_validate(u) for u in result.scalars().all()]


@router.patch("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    await db.commit()
    return {"detail": f"User {user.email} deactivated"}


@router.patch("/users/{user_id}/tier")
async def update_user_tier(
    user_id: str,
    tier: str,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    valid_tiers = {"free", "student", "pro", "enterprise"}
    if tier not in valid_tiers:
        raise HTTPException(status_code=400, detail=f"Invalid tier. Choose from {valid_tiers}")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.tier = tier
    await db.commit()
    return {"detail": f"User {user.email} tier updated to {tier}"}


@router.get("/analytics")
async def get_analytics(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    total_users = await db.scalar(select(func.count(User.id)))
    total_projects = await db.scalar(select(func.count(Project.id)))
    done_projects = await db.scalar(
        select(func.count(Project.id)).where(Project.status == "done")
    )
    failed_projects = await db.scalar(
        select(func.count(Project.id)).where(Project.status == "failed")
    )
    tier_counts = {}
    for tier in ["free", "student", "pro", "enterprise"]:
        count = await db.scalar(
            select(func.count(User.id)).where(User.tier == tier)
        )
        tier_counts[tier] = count

    return {
        "users": {"total": total_users, "by_tier": tier_counts},
        "projects": {
            "total": total_projects,
            "done": done_projects,
            "failed": failed_projects,
            "success_rate": round((done_projects / total_projects * 100) if total_projects else 0, 1),
        },
    }
