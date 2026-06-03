import os
from dotenv import load_dotenv

from agents.trend_agent.trend_engine import run_v3_trend_discovery as run_trend_agent
from agents.critic_agent.critic_agent_v3 import CriticAgentV3 as CriticAgent
from orchestrator.generation_engine import GenerationEngine
from agents.self_improve import SelfImproveAgent
from agents.social_listener import SocialListener
from agents.insights_fetcher import InsightsFetcher
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

    print("\n--- Phase 2: Content Generation (Hook & Script) ---")
    generation_engine = GenerationEngine()
    # For now, we'll hardcode these, but they would come from a strategy agent in a full system.
    emotion = "curiosity"
    pattern = "the_secret"
    platform = "tiktok"

    try:
        generated_content = generation_engine.generate_platform_content(
            trend=trend,
            emotion=emotion,
            pattern=pattern,
            platform=platform,
            content_type="script",
        )
        hook = generated_content["hook"]
        script = generated_content["script"]
        print(f"Generated Hook: {hook.hook_text}")
        print(f"Generated Script: {script.script_text[:100]}...")
    except Exception as e:
        print(f"Content Generation failed: {e}")
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

    print("\n--- Phase 4: Visual Asset Generation (Optional) ---")
    try:
        visual_asset_url = generation_engine.generate_visual_asset(script, platform)
        print(f"Generated Visual Asset URL: {visual_asset_url}")
    except Exception as e:
        print(f"Visual Asset Generation failed (non-critical): {e}")
        print(f"Note: Full visual asset generation requires a subscription upgrade. Currently using a placeholder.")

    print("\n--- Phase 5: Evolution & Learning Loop ---")
    try:
        # 1. Fetch Performance Metrics
        fetcher = InsightsFetcher()
        analytics = fetcher.fetch_metrics(hook.id, platform)
        print(f"Fetched Metrics for {platform}:")
        print(f"  Views: {analytics.views}, Engagement Rate: {analytics.engagement_rate:.2%}")
        
        # 2. Update Strategy from Performance
        self_improve_agent = SelfImproveAgent(db_manager)
        perf_strategy = self_improve_agent.update_strategy_from_performance(hook.id, analytics)
        if perf_strategy:
            db_manager.save_strategy(perf_strategy)
            print(f"Strategy reinforced by performance: {perf_strategy.reasoning}")

        # 3. Batch Update from Reflections (Critic feedback)
        updated_strategies = self_improve_agent.batch_update_strategies(limit=5)
        print(f"Updated {len(updated_strategies)} strategies from recent reflections.")
        
        # 4. Get Recommendations for Next Cycle
        recommendations = self_improve_agent.get_strategy_recommendations(niche="general")
        print(f"Next cycle recommendations:")
        print(f"  Emotion: {recommendations['dominant_emotion']}")
        print(f"  Pattern: {recommendations['recommended_pattern']}")
        print(f"  Confidence: {recommendations['confidence']}%")
    except Exception as e:
        print(f"Evolution Cycle failed (non-critical): {e}")

    print("\n--- Pipeline Execution Complete ---")

if __name__ == "__main__":
    main()
