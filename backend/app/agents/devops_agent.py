"""
DevOpsAgent — Generates Dockerfile, docker-compose.yml, CI/CD configs,
and deployment configuration files.
"""
from app.agents.base_agent import BaseAgent, AgentContext

SYSTEM_PROMPT = """
You are a senior DevOps engineer. Generate complete Docker and deployment configuration.

Return JSON:
{
  "files": {
    "Dockerfile": "...",
    "docker-compose.yml": "...",
    "docker-compose.prod.yml": "...",
    ".dockerignore": "...",
    ".github/workflows/ci.yml": "...",
    "render.yaml": "...",
    "railway.toml": "..."
  }
}

Rules: Use multi-stage Docker builds. Pin dependency versions. Include health checks. Add .dockerignore. Write production-ready compose with named volumes. Return ONLY valid JSON.
"""


class DevOpsAgent(BaseAgent):
    name = "DevOpsAgent"
    description = "Generates Dockerfile, docker-compose, CI/CD configs"

    async def execute(self, ctx: AgentContext) -> AgentContext:
        plan = ctx.agent_logs.get("planner_plan", {})
        db_type = plan.get("database_type", "SQLite")
        needs_frontend = plan.get("needs_frontend", False)

        user_prompt = f"""
Generate complete Docker and deployment config for this project.
{ctx.to_prompt_summary()}
Database: {db_type}
Has Frontend: {needs_frontend}
Architecture: {ctx.architecture or 'Standard app'}
Return ONLY valid JSON.
"""
        raw = await self.call_llm(SYSTEM_PROMPT, user_prompt, temperature=0.1, max_tokens=4000)
        result = self.extract_json(raw)
        if result:
            devops_files = result.get("files", {})
            ctx.files.update(devops_files)
            ctx.docker_files = {k: v for k, v in devops_files.items()
                                if "docker" in k.lower() or k == "Dockerfile"}
        return ctx
