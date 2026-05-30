from agents.trend_agent.engine import run_trend_agent
from memory.database import SupabaseManager


def main() -> None:
    try:
        supabase = SupabaseManager()
        trend = run_trend_agent()
        saved_trend = supabase.save_trend(trend)
        print("Trend saved successfully:")
        print(saved_trend)
    except Exception as exc:
        print(f"Trend pipeline failed: {exc}")
        raise


if __name__ == "__main__":
    main()
