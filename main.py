import os
from dotenv import load_dotenv

from agents.trend_agent.engine import run_trend_agent
from agents.hook_agent.hook_agent import HookAgent
from agents.critic_agent.critic_agent import CriticAgent
from agents.script_agent.script_agent import ScriptAgent
from agents.self_improve import SelfImproveAgent
from agents.social_listener import SocialListener
from memory.database import SupabaseManager

def main():
    load_dotenv()
    
    # 1. Initialize Database Manager
    db_manager = SupabaseManager()
    
    print("--- Phase 0: Social Listening (Optional) ---")
    try:
        listener = SocialListener()
        signals = listener.get_trending_signals("tiktok", limit=3)
        print(f"Detected {len(signals)} trending signals from TikTok.")
        for signal in signals:
            print(f"  - {signal.signal_text} (Velocity: {signal.velocity})")
    except Exception as e:
        print(f"Social Listening failed (non-critical): {e}")
    
    print("\n--- Phase 1: Trend Discovery ---")
    try:
        trend = run_trend_agent()
        print(f"Discovered Trend: {trend.trend_title}")
        print(f"  Velocity: {trend.velocity}, Opportunity: {trend.opportunity}")
        
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
        print(f"Critic Score: {reflection.viral_score}/100")
        print(f"Critic Lesson: {reflection.lesson}")
        
        # Save hook and reflection to database
        if db_manager.client:
            db_manager.save_hook(hook)
            db_manager.save_reflection(reflection)
            print("Hook and Reflection saved to Supabase.")
    except Exception as e:
        print(f"Hook Critique failed: {e}")
        return

    print("\n--- Phase 4: Script Generation (Optional) ---")
    try:
        script_agent = ScriptAgent()
        script = script_agent.generate_script(
            hook=hook,
            trend=trend,
            framework="AIDA",
            platform="tiktok",
            duration_seconds=30,
        )
        print(f"Generated Script ({script.framework} framework for {script.platform}):")
        print(f"  Duration: {script.duration_seconds}s, Scenes: {script.scene_count}")
        print(f"  Script Preview: {script.script_text[:200]}...")
    except Exception as e:
        print(f"Script Generation failed (non-critical): {e}")

    print("\n--- Phase 5: Self-Improvement Cycle (Optional) ---")
    try:
        self_improve_agent = SelfImproveAgent(db_manager)
        updated_strategies = self_improve_agent.batch_update_strategies(limit=5)
        print(f"Updated {len(updated_strategies)} strategies from recent reflections.")
        
        recommendations = self_improve_agent.get_strategy_recommendations(niche="general")
        print(f"Next cycle recommendations:")
        print(f"  Emotion: {recommendations['dominant_emotion']}")
        print(f"  Pattern: {recommendations['recommended_pattern']}")
        print(f"  Confidence: {recommendations['confidence']}%")
    except Exception as e:
        print(f"Self-Improvement Cycle failed (non-critical): {e}")

    print("\n--- Pipeline Execution Complete ---")

if __name__ == "__main__":
    main()
