"""
DatabaseAgent — Generates database schema, migrations, and seed data.
"""
from app.agents.base_agent import BaseAgent, AgentContext

SYSTEM_PROMPT = """
You are a database architect. Generate complete database schema and related files.

Return a JSON object:
{
  "schema_sql": "-- Complete SQL schema with CREATE TABLE statements",
  "files": {
    "backend/app/models/user.py": "# SQLAlchemy model",
    "backend/alembic/versions/001_initial.py": "# Alembic migration",
    "backend/seed_data.py": "# Optional seed data script"
  },
  "er_diagram_description": "Text description of tables and relationships"
}

Rules:
- Use UUID primary keys
- Add created_at, updated_at timestamps
- Add proper indexes on foreign keys
- Write complete SQLAlchemy models (not snippets)
- Include Alembic migration if applicable
"""


class DatabaseAgent(BaseAgent):
    name = "DatabaseAgent"
    description = "Generates database schema and ORM models"

    async def execute(self, ctx: AgentContext) -> AgentContext:
        plan = ctx.agent_logs.get("planner_plan", {})
        needs_db = plan.get("needs_database", True)
        db_type = plan.get("database_type", "SQLite")

        if not needs_db:
            ctx.agent_logs["DatabaseAgent"] = {"status": "skipped", "reason": "No DB needed"}
            return ctx

        user_prompt = f"""
Generate database schema for this project.

{ctx.to_prompt_summary()}

Database type: {db_type}
Architecture: {ctx.architecture or 'Standard'}

Based on the features and project type, design appropriate tables.
Return ONLY valid JSON.
"""
        raw = await self.call_llm(SYSTEM_PROMPT, user_prompt, temperature=0.2)
        result = self.extract_json(raw)
        if result:
            ctx.db_schema = result.get("schema_sql", "")
            db_files = result.get("files", {})
            if db_files:
                ctx.files.update(db_files)
            ctx.agent_logs["database_result"] = {
                "er_diagram": result.get("er_diagram_description", ""),
                "db_type": db_type,
            }
        return ctx
