import os
from typing import Any, List, Optional

from dotenv import load_dotenv
from supabase import Client, create_client

from schemas.models import Analytics, Hook, Reflection, StrategyMemory, TrendData


class Tables:
    TRENDS = "trends"
    HOOKS = "hooks"
    REFLECTIONS = "reflections"
    STRATEGY_MEMORY = "strategy_memory"
    ANALYTICS = "analytics"


class SupabaseManager:
    def __init__(self) -> None:
        load_dotenv()

        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in the environment.")

        try:
            self.client: Client = create_client(supabase_url, supabase_key)
        except Exception as exc:
            raise RuntimeError("Failed to initialize Supabase client.") from exc

    def _execute_insert(self, table_name: str, data: dict) -> Any:
        try:
            clean_data = {key: value for key, value in data.items() if value is not None}
            for key, value in clean_data.items():
                if hasattr(value, "hex"):
                    clean_data[key] = str(value)
                elif hasattr(value, "isoformat"):
                    clean_data[key] = value.isoformat()

            response = self.client.table(table_name).insert(clean_data).execute()
            return response.data
        except Exception as exc:
            raise RuntimeError(f"Failed to insert into {table_name}: {exc}") from exc

    def save_trend(self, data: TrendData) -> Any:
        return self._execute_insert(Tables.TRENDS, data.model_dump())

    def save_hook(self, data: Hook) -> Any:
        return self._execute_insert(Tables.HOOKS, data.model_dump())

    def save_reflection(self, data: Reflection) -> Any:
        return self._execute_insert(Tables.REFLECTIONS, data.model_dump())

    def save_strategy(self, data: StrategyMemory) -> Any:
        return self._execute_insert(Tables.STRATEGY_MEMORY, data.model_dump())

    def save_analytics(self, data: Analytics) -> Any:
        return self._execute_insert(Tables.ANALYTICS, data.model_dump())

    def get_latest_trends(self, limit: int = 10) -> List[dict]:
        try:
            response = (
                self.client.table(Tables.TRENDS)
                .select("*")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return response.data
        except Exception as exc:
            raise RuntimeError(f"Failed to fetch latest trends: {exc}") from exc

    def get_reflections(self, limit: int = 5) -> List[dict]:
        try:
            response = (
                self.client.table(Tables.REFLECTIONS)
                .select("*")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return response.data
        except Exception as exc:
            raise RuntimeError(f"Failed to fetch reflections: {exc}") from exc

    def get_strategy_memory(self, niche: Optional[str] = None, limit: Optional[int] = None) -> List[dict]:
        try:
            query = self.client.table(Tables.STRATEGY_MEMORY).select("*").order("created_at", desc=True)
            if niche:
                query = query.eq("niche", niche)
            if limit is not None:
                query = query.limit(limit)
            response = query.execute()
            return response.data
        except Exception as exc:
            raise RuntimeError(f"Failed to fetch strategy memory: {exc}") from exc
