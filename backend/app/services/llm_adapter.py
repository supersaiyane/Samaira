import os
import httpx
from app.core.config import settings

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

try:
    import anthropic
except ImportError:
    anthropic = None


class LLMAdapter:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.model = settings.LLM_MODEL
        self.api_key = settings.LLM_API_KEY

    async def generate_sql(self, nl_query: str, db_schema: str) -> str:
        if not settings.USE_LLM_FALLBACK:
            return None  # feature turned off

        if self.provider == "openai":
            return await self._openai_call(nl_query, db_schema)
        elif self.provider == "anthropic":
            return await self._anthropic_call(nl_query, db_schema)
        elif self.provider == "ollama":
            return await self._ollama_call(nl_query, db_schema)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    async def _openai_call(self, nl_query: str, db_schema: str) -> str:
        client = AsyncOpenAI(api_key=self.api_key)
        prompt = self._build_prompt(nl_query, db_schema)
        resp = await client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.choices[0].message.content.strip()

    async def _anthropic_call(self, nl_query: str, db_schema: str) -> str:
        client = anthropic.AsyncAnthropic(api_key=self.api_key)
        prompt = self._build_prompt(nl_query, db_schema)
        resp = await client.messages.create(
            model=self.model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.content[0].text.strip()

    async def _ollama_call(self, nl_query: str, db_schema: str) -> str:
        prompt = self._build_prompt(nl_query, db_schema)
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "http://ollama:11434/api/generate",   # ✅ use service name instead of localhost
                json={"model": self.model, "prompt": prompt}
            )
            data = resp.json()
            return data.get("response", "").strip()

    def _build_prompt(self, nl_query: str, db_schema: str) -> str:
        return f"""
        Convert this natural language request into a SAFE SQL query.
        Schema:
        {db_schema}

        Rules:
        - Only SELECT queries are allowed.
        - Always include LIMIT 100 if not specified.
        - No DELETE, DROP, UPDATE, INSERT, or ALTER.

        Question: {nl_query}
        """
