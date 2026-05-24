"""
MLAgent — Generates ML/AI pipeline code when the project requires it.
Skipped for non-ML projects.
"""
from app.agents.base_agent import BaseAgent, AgentContext

SYSTEM_PROMPT = """
You are a senior ML engineer. Generate complete ML pipeline code.

Return JSON: { "files": { "ml/train.py": "...", "ml/predict.py": "...", "ml/preprocessing.py": "...", "ml/model.py": "...", "ml/evaluate.py": "...", "ml/config.yaml": "..." }, "model_description": "...", "metrics_to_track": ["accuracy"] }

Rules: Write complete runnable scripts. Include train/val/test splits, model saving, evaluation metrics. Use appropriate frameworks (scikit-learn, PyTorch, TensorFlow, HuggingFace). Return ONLY valid JSON.
"""

ML_CATEGORIES = {"machine learning", "deep learning", "data science", "ai agent", "ieee research-based"}


class MLAgent(BaseAgent):
    name = "MLAgent"
    description = "Generates ML/AI pipeline code"

    async def execute(self, ctx: AgentContext) -> AgentContext:
        plan = ctx.agent_logs.get("planner_plan", {})
        needs_ml = plan.get("needs_ml", False)
        category_lower = ctx.category.lower()
        is_ml_project = needs_ml or any(c in category_lower for c in ML_CATEGORIES)
        tech_lower = [t.lower() for t in ctx.technologies]
        has_ml_tech = any(t in tech_lower for t in [
            "pytorch", "tensorflow", "sklearn", "scikit-learn",
            "keras", "huggingface", "transformers", "xgboost", "lightgbm"
        ])

        if not is_ml_project and not has_ml_tech:
            ctx.agent_logs["MLAgent"] = {"status": "skipped", "reason": "Not an ML project"}
            return ctx

        user_prompt = f"""
Generate complete ML pipeline code for this project.
{ctx.to_prompt_summary()}
Dataset info: {ctx.dataset_info}
Generate training, inference, preprocessing, and evaluation scripts.
Return ONLY valid JSON.
"""
        raw = await self.call_llm(SYSTEM_PROMPT, user_prompt, temperature=0.2, max_tokens=6000)
        result = self.extract_json(raw)
        if result:
            ctx.files.update(result.get("files", {}))
            ctx.agent_logs["ml_result"] = {
                "model_description": result.get("model_description", ""),
                "metrics": result.get("metrics_to_track", []),
            }
        return ctx
