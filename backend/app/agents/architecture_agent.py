"""
ArchitectureAgent — Generates the full folder structure and high-level
architecture description based on the planner's output.
"""
from app.agents.base_agent import BaseAgent, AgentContext

SYSTEM_PROMPT = """
You are a senior software architect.
Generate the complete folder structure and architecture description for a software project.

Return a JSON object with this exact structure:
{
  "architecture_description": "Detailed paragraph describing the architecture",
  "folder_structure": {
    "root": {
      "backend": {
        "app": {
          "api": {},
          "models": {},
          "services": {}
        },
        "requirements.txt": null,
        "Dockerfile": null
      },
      "frontend": {
        "src": {
          "components": {},
          "pages": {}
        },
        "package.json": null
      },
      "docker-compose.yml": null,
      "README.md": null
    }
  },
  "key_files": [
    {"path": "backend/main.py", "purpose": "FastAPI app entry point"},
    {"path": "backend/app/models/user.py", "purpose": "User database model"}
  ],
  "design_patterns": ["Repository Pattern", "Dependency Injection"],
  "api_endpoints": [
    {"method": "POST", "path": "/api/v1/items", "description": "Create item"}
  ]
}
"""


class ArchitectureAgent(BaseAgent):
    name = "ArchitectureAgent"
    description = "Designs folder structure and architecture"

    async def execute(self, ctx: AgentContext) -> AgentContext:
        plan = ctx.agent_logs.get("planner_plan", {})
        user_prompt = f"""
Design the complete architecture for this project.

{ctx.to_prompt_summary()}

Planner output: {plan}

Generate a realistic, production-ready folder structure.
Return ONLY valid JSON.
"""
        raw = await self.call_llm(SYSTEM_PROMPT, user_prompt, temperature=0.2)
        result = self.extract_json(raw)
        if result:
            ctx.architecture = result.get("architecture_description", "")
            ctx.folder_structure = result.get("folder_structure", {})
            ctx.api_routes = result.get("api_endpoints", [])
            ctx.agent_logs["architecture_result"] = result
        return ctx
