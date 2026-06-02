import os
from dotenv import load_dotenv

from agents.trend_agent.engine import run_trend_agent
from agents.hook_agent.hook_agent import HookAgent
from agents.critic_agent.critic_agent import CriticAgent
from memory.database import SupabaseManager

def main():
    load_dotenv()
    
    # 1. Initialize Database Manager
    db_manager = SupabaseManager()
    
    print("--- Phase 1: Trend Discovery ---")
    try:
        trend = run_trend_agent()
        print(f"Discovered Trend: {trend.trend_title}")
        
        # Save trend to database
        if db_manager.client:
            db_manager.save_trend(trend)
            print("Trend saved to Supabase.")
    except Exception as e:
        print(f"Trend Discovery failed: {e}")
        return

    print("\n--- Phase 2: Hook Generation (Actor) ---")
    hook_agent = HookAgent()
    # In a full system, these would come from the Strategy Agent
    emotion = "curiosity"
    pattern = "the_secret"
    
    try:
        hook = hook_agent.generate_hook(trend, emotion, pattern)
        print(f"Generated Hook: {hook.hook_text}")
    except Exception as e:
        print(f"Hook Generation failed: {e}")
        return

    print("\n--- Phase 3: Hook Critique (Critic) ---")
    critic_agent = CriticAgent()
    try:
        reflection = critic_agent.criticize_hook(hook)
        print(f"Critic Score: {reflection.performance_score}/100")
        print(f"Critic Lesson: {reflection.lesson}")
        
        # Save hook and reflection to database
        if db_manager.client:
            db_manager.save_hook(hook)
            db_manager.save_reflection(reflection)
            print("Hook and Reflection saved to Supabase.")
    except Exception as e:
        print(f"Hook Critique failed: {e}")
        return

    print("\n--- Pipeline Execution Complete ---")

if __name__ == "__main__":
    main()
