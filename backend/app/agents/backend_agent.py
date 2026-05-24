"""
BackendAgent — Generates all backend source code files.
Produces complete, runnable code based on the architecture plan.
"""
import json
from app.agents.base_agent import BaseAgent, AgentContext

SYSTEM_PROMPT = """
You are a senior backend developer. Generate complete, production-ready backend code.

Return a JSON object where keys are file paths and values are the complete file contents:
{
  "backend/main.py": "# full file content here\\nfrom fastapi import FastAPI\\n...",
  "backend/app/models/user.py": "# full file content...",
  "backend/requirements.txt": "fastapi\\nuvicorn\\n..."
}

Rules:
- Write COMPLETE files, not snippets or placeholders
- Include all imports
- Add docstrings and comments
- Follow PEP 8 for Python
- Make code production-ready
- Use async/await where appropriate
- Include error handling
"""


class BackendAgent(BaseAgent):
    name = "BackendAgent"
    description = "Generates backend source code files"

    async def execute(self, ctx: AgentContext) -> AgentContext:
        plan = ctx.agent_logs.get("planner_plan", {})
        arch = ctx.agent_logs.get("architecture_result", {})

        user_prompt = f"""
Generate complete backend code for this project.

Project Summary:
{ctx.to_prompt_summary()}

Architecture:
{ctx.architecture or 'Standard REST API'}

Key files to generate:
{json.dumps(arch.get('key_files', []), indent=2)}

API Endpoints:
{json.dumps(ctx.api_routes or [], indent=2)}

Needs Auth: {plan.get('needs_auth', True)}
Needs Database: {plan.get('needs_database', True)}
Database Type: {plan.get('database_type', 'SQLite')}
Primary Language: {plan.get('primary_language', 'Python')}
Architecture Pattern: {plan.get('architecture_pattern', 'Clean Architecture')}

Generate ALL backend files as a single JSON object.
Include: main entry point, models, routes/controllers, services, config, requirements.txt
Return ONLY valid JSON, no markdown.
"""
        raw = await self.call_llm(SYSTEM_PROMPT, user_prompt, temperature=0.25, max_tokens=8192)
        files = self.extract_json(raw)
        if files and isinstance(files, dict):
            ctx.files.update(files)
        return ctx
