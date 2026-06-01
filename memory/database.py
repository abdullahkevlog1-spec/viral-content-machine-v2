import os
from typing import Any, List, Optional

from dotenv import load_dotenv
from supabase import Client, create_client

from schemas.models import Analytics, Hook, Reflection, StrategyMemory, TrendData


class SupabaseManager:
    def __init__(self) -> None:
        load_dotenv()

        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            # Fallback for local development if env vars are missing
            supabase_url = "https://your-project-id.supabase.co"
            supabase_key = "your-anon-key"

        try:
            self.client: Client = create_client(supabase_url, supabase_key)
        except Exception as exc:
            print(f"Warning: Failed to initialize Supabase client: {exc}")
            self.client = None

    def _execute_insert(self, table_name: str, data: dict) -> Any:
        if not self.client:
            raise RuntimeError("Supabase client not initialized.")
        try:
            # Filter out None values to let DB defaults kick in
            clean_data = {k: v for k, v in data.items() if v is not None}
            # Convert UUID and datetime to string for JSON serialization
            for k, v in clean_data.items():
                if hasattr(v, "hex"):  # UUID
                    clean_data[k] = str(v)
                elif hasattr(v, "isoformat"):  # datetime
                    clean_data[k] = v.isoformat()
            
            response = self.client.table(table_name).insert(clean_data).execute()
            return response.data
        except Exception as exc:
            raise RuntimeError(f"Failed to insert into {table_name}: {exc}") from exc

    def save_trend(self, data: TrendData) -> Any:
        return self._execute_insert("trends", data.model_dump())

    def save_hook(self, data: Hook) -> Any:
        return self._execute_insert("hooks", data.model_dump())

    def save_reflection(self, data: Reflection) -> Any:
        return self._execute_insert("reflections", data.model_dump())

    def save_strategy(self, data: StrategyMemory) -> Any:
        return self._execute_insert("strategy_memory", data.model_dump())

    def save_analytics(self, data: Analytics) -> Any:
        return self._execute_insert("analytics", data.model_dump())

    def get_latest_trends(self, limit: int = 10) -> List[dict]:
        if not self.client:
            return []
        try:
            response = self.client.table("trends").select("*").order("created_at", desc=True).limit(limit).execute()
            return response.data
        except Exception as exc:
            raise RuntimeError(f"Failed to fetch latest trends: {exc}") from exc

    def get_reflections(self, limit: int = 5) -> List[dict]:
        if not self.client:
            return []
        try:
            response = self.client.table("reflections").select("*").order("created_at", desc=True).limit(limit).execute()
            return response.data
        except Exception as exc:
            raise RuntimeError(f"Failed to fetch reflections: {exc}") from exc

    def get_strategy_memory(self, niche: Optional[str] = None) -> List[dict]:
        if not self.client:
            return []
        try:
            query = self.client.table("strategy_memory").select("*").order("created_at", desc=True)
            if niche:
                query = query.eq("niche", niche)
            response = query.limit(1).execute()
            return response.data
        except Exception as exc:
            raise RuntimeError(f"Failed to fetch strategy memory: {exc}") from exc
