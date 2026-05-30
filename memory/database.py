import os
from typing import Any

from dotenv import load_dotenv
from supabase import Client, create_client

from schemas.models import TrendData


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

    def save_trend(self, data: TrendData) -> Any:
        try:
            response = self.client.table("trends").insert(data.model_dump()).execute()
            return response.data
        except Exception as exc:
            raise RuntimeError("Failed to save trend data to Supabase.") from exc

    def get_latest_trends(self) -> Any:
        try:
            response = self.client.table("trends").select("*").order("created_at", desc=True).execute()
            return response.data
        except Exception as exc:
            raise RuntimeError("Failed to fetch latest trends from Supabase.") from exc
