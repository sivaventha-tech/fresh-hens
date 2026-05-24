"""
TestingAgent — Generates unit tests, integration tests, and test configuration.
"""
from app.agents.base_agent import BaseAgent, AgentContext

SYSTEM_PROMPT = """
You are a senior QA engineer. Generate complete test suites for the project.

Return JSON:
{
  "files": {
    "tests/test_main.py": "# pytest tests",
    "tests/test_api.py": "# API endpoint tests",
    "tests/conftest.py": "# pytest fixtures",
    "pytest.ini": "[pytest]\\nasyncio_mode = auto"
  }
}

Rules: Use pytest and pytest-asyncio. Test happy path and error cases. Mock external dependencies. Include fixtures for DB and auth. Return ONLY valid JSON.
"""


class TestingAgent(BaseAgent):
    name = "TestingAgent"
    description = "Generates unit and integration test files"

    async def execute(self, ctx: AgentContext) -> AgentContext:
        import json
        user_prompt = f"""
Generate complete test suite for this project.
{ctx.to_prompt_summary()}
API Endpoints: {json.dumps(ctx.api_routes or [], indent=2)}
Return ONLY valid JSON.
"""
        raw = await self.call_llm(SYSTEM_PROMPT, user_prompt, temperature=0.2, max_tokens=4000)
        result = self.extract_json(raw)
        if result:
            test_files = result.get("files", {})
            ctx.test_files = test_files
            ctx.files.update(test_files)
        return ctx
