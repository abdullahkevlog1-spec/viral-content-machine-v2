import os
import uuid
from dotenv import load_dotenv

from agents.hook_agent.hook_agent import HookAgent
from agents.critic_agent.critic_agent import CriticAgent
from memory.database import SupabaseManager
from schemas.models import TrendData

def main():
    load_dotenv()
    
    # 1. Initialize Managers and Agents
    db_manager = SupabaseManager()
    hook_agent = HookAgent()
    critic_agent = CriticAgent()

    # 2. Mock Trend Data (In a real scenario, this would come from the database)
    mock_trend = TrendData(
        id=uuid.uuid4(),
        trend_title="The Rise of Autonomous AI Agents",
        trend_summary="AI agents are moving from simple chatbots to autonomous systems capable of complex task execution.",
        source="TechCrunch",
        source_url="https://techcrunch.com/ai-agents",
        niche="Technology"
    )

    print(f"--- Starting Actor-Critic Loop for Trend: {mock_trend.trend_title} ---")

    # 3. Actor: Generate Hook
    emotion = "fear"
    pattern = "hard_truth"
    
    print(f"\n[Actor] Generating hook with emotion '{emotion}' and pattern '{pattern}'...")
    try:
        hook = hook_agent.generate_hook(mock_trend, emotion, pattern)
        print(f"Generated Hook: {hook.hook_text}")
        print(f"Reasoning: {hook.reasoning}")
    except Exception as e:
        print(f"Actor failed: {e}")
        return

    # 4. Critic: Evaluate Hook
    print("\n[Critic] Evaluating hook...")
    try:
        reflection = critic_agent.criticize_hook(hook)
        print(f"Viral Score: {reflection.performance_score}")
        print(f"Lesson: {reflection.lesson}")
    except Exception as e:
        print(f"Critic failed: {e}")
        return

    # 5. Refinement Loop (Simplified for Sprint 2)
    if reflection.performance_score < 85:
        print("\n[Refinement] Score below 85. In a full pipeline, we would retry here.")
    else:
        print("\n[Success] Hook passed the critic's standards!")

    # 6. Database: Save results (Only if DB is configured)
    if db_manager.client:
        print("\n[Database] Saving trend, hook, and reflection to Supabase...")
        try:
            db_manager.save_trend(mock_trend)
            db_manager.save_hook(hook)
            db_manager.save_reflection(reflection)
            print("Data saved successfully!")
        except Exception as e:
            print(f"Database save failed: {e}")
    else:
        print("\n[Database] Skipping save: Supabase client not initialized.")

if __name__ == "__main__":
    main()
