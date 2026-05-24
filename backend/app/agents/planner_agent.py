"""
PlannerAgent — Analyzes the user's project request and produces a
structured project plan that all downstream agents will use.
"""
from app.agents.base_agent import BaseAgent, AgentContext

SYSTEM_PROMPT = """
You are a senior software architect and project planner.
Your job is to analyze a project request and produce a detailed project plan.

Return a JSON object with this exact structure:
{
  "project_type": "string (e.g. REST API, Full Stack Web App, ML Pipeline)",
  "primary_language": "Python | TypeScript | JavaScript",
  "architecture_pattern": "MVC | Clean Architecture | Microservices | Monolith",
  "needs_database": true,
  "database_type": "PostgreSQL | SQLite | MongoDB | None",
  "needs_auth": true,
  "needs_ml": false,
  "needs_docker": true,
  "needs_frontend": false,
  "dataset_required": false,
  "dataset_keywords": [],
  "recommended_packages": ["list", "of", "packages"],
  "project_overview": "2-3 sentence description of the project",
  "key_components": ["Component 1", "Component 2"],
  "estimated_files": 10,
  "complexity_notes": "Why this complexity level was chosen"
}
"""


class PlannerAgent(BaseAgent):
    name = "PlannerAgent"
    description = "Analyzes request, produces structured project plan"

    async def execute(self, ctx: AgentContext) -> AgentContext:
        user_prompt = f"""
Analyze this project request and return a structured JSON plan.

{ctx.to_prompt_summary()}

Return ONLY valid JSON, no markdown, no extra text.
"""
        raw = await self.call_llm(SYSTEM_PROMPT, user_prompt, temperature=0.2)
        plan = self.extract_json(raw)
        if plan:
            ctx.agent_logs["planner_plan"] = plan
            # Store dataset intent on context
            ctx.dataset_info = {
                "required": plan.get("dataset_required", False),
                "keywords": plan.get("dataset_keywords", []),
            }
        return ctx
