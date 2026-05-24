"""
BaseAgent — abstract base class for all AI agents.
Each agent receives the shared project context and returns structured output.
"""
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from loguru import logger
from app.services.ai_service import ai_service


class AgentContext:
    """Shared context object passed through the agent pipeline."""

    def __init__(
        self,
        title: str,
        category: str,
        technologies: list,
        features: list,
        complexity: str,
        project_id: str,
    ):
        self.title = title
        self.category = category
        self.technologies = technologies
        self.features = features
        self.complexity = complexity
        self.project_id = project_id

        # Outputs populated by each agent
        self.architecture: Optional[str] = None
        self.folder_structure: Optional[Dict] = None
        self.files: Dict[str, str] = {}
        self.readme: Optional[str] = None
        self.env_example: Optional[str] = None
        self.db_schema: Optional[str] = None
        self.api_routes: Optional[Dict] = None
        self.docker_files: Dict[str, str] = {}
        self.test_files: Dict[str, str] = {}
        self.agent_logs: Dict[str, Any] = {}
        self.total_tokens: int = 0
        self.errors: Dict[str, str] = {}
        self.dataset_info: Optional[Dict] = None

    def to_prompt_summary(self) -> str:
        """Compact summary injected into each agent's prompt for context."""
        return f"""
Project: {self.title}
Category: {self.category}
Tech Stack: {', '.join(self.technologies)}
Features: {', '.join(self.features)}
Complexity: {self.complexity}
""".strip()


class BaseAgent(ABC):
    """Abstract base for all project generation agents."""

    name: str = "BaseAgent"
    description: str = ""

    async def run(self, ctx: AgentContext) -> AgentContext:
        """Execute the agent. Logs timing and errors automatically."""
        logger.info(f"▶ [{self.name}] Starting...")
        start = time.time()
        try:
            ctx = await self.execute(ctx)
            duration_ms = int((time.time() - start) * 1000)
            ctx.agent_logs[self.name] = {"status": "done", "duration_ms": duration_ms}
            logger.success(f"✓ [{self.name}] Completed in {duration_ms}ms")
        except Exception as e:
            duration_ms = int((time.time() - start) * 1000)
            ctx.agent_logs[self.name] = {"status": "failed", "error": str(e), "duration_ms": duration_ms}
            ctx.errors[self.name] = str(e)
            logger.error(f"✗ [{self.name}] Failed: {e}")
        return ctx

    @abstractmethod
    async def execute(self, ctx: AgentContext) -> AgentContext:
        """Agent-specific logic — implemented by each subclass."""
        ...

    async def call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 8192,
    ) -> str:
        return await ai_service.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def extract_json(self, text: str):
        return ai_service.extract_json(text)
