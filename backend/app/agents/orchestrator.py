"""
Orchestrator — coordinates all agents in sequence and manages the
shared AgentContext through the full pipeline.
"""
import asyncio
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.agents.base_agent import AgentContext
from app.agents.planner_agent import PlannerAgent
from app.agents.architecture_agent import ArchitectureAgent
from app.agents.backend_agent import BackendAgent
from app.agents.frontend_agent import FrontendAgent
from app.agents.database_agent import DatabaseAgent
from app.agents.ml_agent import MLAgent
from app.agents.devops_agent import DevOpsAgent
from app.agents.documentation_agent import DocumentationAgent
from app.agents.testing_agent import TestingAgent
from app.models.project import Project
from app.models.generation import GenerationLog


# Ordered agent pipeline
AGENT_PIPELINE = [
    PlannerAgent,
    ArchitectureAgent,
    BackendAgent,
    FrontendAgent,
    DatabaseAgent,
    MLAgent,
    DevOpsAgent,
    DocumentationAgent,
    TestingAgent,
]

# Progress milestones (percent complete after each agent)
PROGRESS_MAP = {
    "PlannerAgent": 10,
    "ArchitectureAgent": 20,
    "BackendAgent": 40,
    "FrontendAgent": 55,
    "DatabaseAgent": 65,
    "MLAgent": 72,
    "DevOpsAgent": 80,
    "DocumentationAgent": 90,
    "TestingAgent": 100,
}


class ProjectOrchestrator:
    """Runs the full agent pipeline for a project generation job."""

    async def run(
        self,
        project_id: str,
        title: str,
        category: str,
        technologies: list,
        features: list,
        complexity: str,
        db: AsyncSession,
    ) -> AgentContext:
        # Build shared context
        ctx = AgentContext(
            title=title,
            category=category,
            technologies=technologies,
            features=features,
            complexity=complexity,
            project_id=project_id,
        )

        # Mark project as generating
        await self._update_project_status(db, project_id, "generating")

        try:
            for AgentClass in AGENT_PIPELINE:
                agent = AgentClass()
                ctx = await agent.run(ctx)

                # Log each agent's result to DB
                agent_status = ctx.agent_logs.get(agent.name, {}).get("status", "done")
                log = GenerationLog(
                    project_id=project_id,
                    agent_name=agent.name,
                    status=agent_status,
                    output=str(ctx.agent_logs.get(agent.name, "")),
                    duration_ms=ctx.agent_logs.get(agent.name, {}).get("duration_ms"),
                )
                db.add(log)
                await db.commit()

                logger.info(
                    f"Pipeline progress: {PROGRESS_MAP.get(agent.name, 0)}% "
                    f"[{agent.name}={agent_status}]"
                )

            # Save generated output to project
            await self._save_project_output(db, project_id, ctx)
            await self._update_project_status(db, project_id, "done")
            logger.success(f"✅ Project {project_id} generation complete. "
                           f"Files: {len(ctx.files)}")

        except Exception as e:
            logger.error(f"Orchestrator failed for project {project_id}: {e}")
            await self._update_project_status(db, project_id, "failed", error=str(e))
            raise

        return ctx

    async def _update_project_status(
        self, db: AsyncSession, project_id: str,
        status: str, error: str = None
    ):
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        if project:
            project.status = status
            if error:
                project.error_message = error
            await db.commit()

    async def _save_project_output(
        self, db: AsyncSession, project_id: str, ctx: AgentContext
    ):
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        if project:
            project.architecture = ctx.architecture
            project.folder_structure = ctx.folder_structure
            project.files = ctx.files
            project.readme = ctx.readme
            project.env_example = ctx.env_example
            project.tokens_used = ctx.total_tokens
            await db.commit()
