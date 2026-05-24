"""
AI Service — unified wrapper for Gemini, OpenAI, and Anthropic.
Switch providers via LLM_PROVIDER env var.
"""
import json
import re
from typing import Optional
from loguru import logger
from app.core.config import settings


class AIService:
    """Single interface to call any supported LLM provider."""

    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        self._client = None
        self._init_client()

    def _init_client(self):
        if self.provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self._client = genai.GenerativeModel(settings.LLM_MODEL)
            logger.info(f"AI Service: Gemini ({settings.LLM_MODEL})")

        elif self.provider == "openai":
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info(f"AI Service: OpenAI ({settings.OPENAI_MODEL})")

        elif self.provider == "anthropic":
            import anthropic
            self._client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            logger.info(f"AI Service: Anthropic ({settings.ANTHROPIC_MODEL})")

        else:
            raise ValueError(f"Unsupported LLM_PROVIDER: {self.provider}")

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 8192,
    ) -> str:
        """Generate text from the configured LLM."""
        try:
            if self.provider == "gemini":
                return await self._gemini_generate(system_prompt, user_prompt)
            elif self.provider == "openai":
                return await self._openai_generate(system_prompt, user_prompt, temperature, max_tokens)
            elif self.provider == "anthropic":
                return await self._anthropic_generate(system_prompt, user_prompt, temperature, max_tokens)
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise

    async def _gemini_generate(self, system_prompt: str, user_prompt: str) -> str:
        import asyncio
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        response = await asyncio.to_thread(self._client.generate_content, full_prompt)
        return response.text

    async def _openai_generate(
        self, system_prompt: str, user_prompt: str,
        temperature: float, max_tokens: int
    ) -> str:
        response = await self._client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    async def _anthropic_generate(
        self, system_prompt: str, user_prompt: str,
        temperature: float, max_tokens: int
    ) -> str:
        response = await self._client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return response.content[0].text

    def extract_json(self, text: str) -> Optional[dict]:
        """
        Safely extract JSON from an LLM response that may include
        markdown fences or extra commentary.
        """
        # Try raw parse first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Strip markdown fences
        patterns = [
            r"```json\s*(.*?)\s*```",
            r"```\s*(.*?)\s*```",
            r"\{.*\}",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1) if "```" in pattern else match.group(0))
                except json.JSONDecodeError:
                    continue

        logger.warning("Could not extract JSON from LLM response")
        return None


# Singleton instance
ai_service = AIService()
