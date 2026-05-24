"""
DocumentationAgent — Generates README.md, API docs, and .env.example.
"""
import json
from app.agents.base_agent import BaseAgent, AgentContext

SYSTEM_PROMPT = """
You are a technical writer. Generate complete project documentation.

Return JSON:
{
  "readme": "# Full README.md content in markdown",
  "env_example": "# .env.example content\\nDATABASE_URL=\\nSECRET_KEY=",
  "api_docs": "# API Documentation in markdown"
}

README must include: Project overview, Features, Tech stack, Folder structure, Installation guide (step-by-step), API docs, Docker setup, Deployment guide, Environment variables, Contributing, License. Return ONLY valid JSON.
"""


class DocumentationAgent(BaseAgent):
    name = "DocumentationAgent"
    description = "Generates README, API docs, and .env.example"

    async def execute(self, ctx: AgentContext) -> AgentContext:
        plan = ctx.agent_logs.get("planner_plan", {})
        user_prompt = f"""
Generate complete documentation for this project.
{ctx.to_prompt_summary()}
Architecture: {ctx.architecture or 'Standard app'}
API Endpoints: {json.dumps(ctx.api_routes or [], indent=2)}
DB Schema: {ctx.db_schema or 'Not applicable'}
Has ML: {plan.get('needs_ml', False)}
Packages: {json.dumps(plan.get('recommended_packages', []))}
Return ONLY valid JSON.
"""
        raw = await self.call_llm(SYSTEM_PROMPT, user_prompt, temperature=0.3, max_tokens=6000)
        result = self.extract_json(raw)
        if result:
            ctx.readme = result.get("readme", "")
            ctx.env_example = result.get("env_example", "")
            if ctx.readme:
                ctx.files["README.md"] = ctx.readme
            if ctx.env_example:
                ctx.files[".env.example"] = ctx.env_example
            if result.get("api_docs"):
                ctx.files["docs/API.md"] = result["api_docs"]
        return ctx
