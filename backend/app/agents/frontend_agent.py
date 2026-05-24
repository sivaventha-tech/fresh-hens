"""
FrontendAgent — Generates frontend code (React / Next.js / plain HTML).
Only runs if the planner determined a frontend is needed.
"""
import json
from app.agents.base_agent import BaseAgent, AgentContext

SYSTEM_PROMPT = """
You are a senior frontend developer. Generate complete, production-ready frontend code.

Return a JSON object where keys are file paths and values are the full file contents:
{
  "frontend/src/app/page.tsx": "// full file content",
  "frontend/package.json": "{ ... }",
  "frontend/tailwind.config.ts": "// full config"
}

Rules:
- Write COMPLETE files — no truncation, no placeholders
- Use TypeScript for React/Next.js projects
- Add proper types and interfaces
- Include responsive design with Tailwind CSS
- Add loading states and error handling
- Follow React best practices (hooks, components)
- Include package.json with all dependencies
"""


class FrontendAgent(BaseAgent):
    name = "FrontendAgent"
    description = "Generates frontend source code files"

    async def execute(self, ctx: AgentContext) -> AgentContext:
        plan = ctx.agent_logs.get("planner_plan", {})
        needs_frontend = plan.get("needs_frontend", False)

        # Skip if no frontend needed
        tech_lower = [t.lower() for t in ctx.technologies]
        has_frontend_tech = any(
            t in tech_lower
            for t in ["react", "next.js", "nextjs", "vue", "angular", "html", "tailwind"]
        )

        if not needs_frontend and not has_frontend_tech:
            ctx.agent_logs["FrontendAgent"] = {"status": "skipped", "reason": "No frontend needed"}
            return ctx

        arch = ctx.agent_logs.get("architecture_result", {})
        user_prompt = f"""
Generate complete frontend code for this project.

Project Summary:
{ctx.to_prompt_summary()}

Technologies: {', '.join(ctx.technologies)}

Architecture:
{ctx.architecture or 'Standard frontend app'}

API Endpoints to consume:
{json.dumps(ctx.api_routes or [], indent=2)}

Generate ALL frontend files as a single JSON object.
Include: pages, components, API client, state management, package.json, config files.
Return ONLY valid JSON, no markdown.
"""
        raw = await self.call_llm(SYSTEM_PROMPT, user_prompt, temperature=0.25, max_tokens=8192)
        files = self.extract_json(raw)
        if files and isinstance(files, dict):
            ctx.files.update(files)
        return ctx
