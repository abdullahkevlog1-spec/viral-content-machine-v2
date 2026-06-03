import os
from typing import Dict, Any
from dotenv import load_dotenv
from crewai import Agent, Crew, Task, LLM
from langchain_google_genai import ChatGoogleGenerativeAI

from schemas.models import Hook, TrendData, Script
from agents.hook_agent.hook_agent import HookAgent
from agents.script_agent.script_agent import ScriptAgent

class GenerationEngine:
    """
    Handles platform-specific content generation (hooks, scripts, and eventually visuals).
    """
    def __init__(self):
        load_dotenv()
        self.llm = self._create_llm()
        self.hook_agent = HookAgent(llm=self.llm)
        self.script_agent = ScriptAgent(llm=self.llm)

    def _create_llm(self) -> ChatGoogleGenerativeAI:
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY must be set.")
        return ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite").replace("gemini/", ""),
            google_api_key=api_key,
            temperature=0.7
        )

    def generate_platform_content(
        self,
        trend: TrendData,
        emotion: str,
        pattern: str,
        platform: str,
        content_type: str = "script", # Can be "hook" or "script"
        duration_seconds: int = 30,
    ) -> Dict[str, Any]:
        """
        Generates content tailored for a specific platform.
        """
        generated_hook = None
        generated_script = None

        # Phase 1: Generate Hook
        generated_hook = self.hook_agent.generate_hook(trend, emotion, pattern, platform)
        print(f"Generated Hook for {platform}: {generated_hook.hook_text}")

        if content_type == "hook":
            return {"hook": generated_hook}

        # Phase 2: Generate Script (if content_type is script)
        if content_type == "script":
            generated_script = self.script_agent.generate_script(
                hook=generated_hook,
                trend=trend,
                framework="AIDA", # Defaulting to AIDA for now
                platform=platform,
                duration_seconds=duration_seconds,
            )
            print(f"Generated Script for {platform}: {generated_script.script_text[:100]}...")
            return {"hook": generated_hook, "script": generated_script}

        return {"hook": generated_hook, "script": generated_script}

    def generate_visual_asset(self, script: Script, platform: str) -> str:
        """
        Placeholder for generating visual assets based on the script and platform.
        In V3, this would integrate with Stable Diffusion XL or Flux.
        """
        print(f"Generating visual asset for {platform} based on script: {script.script_text[:50]}...")
        # Mocking a URL for the generated image
        return f"https://example.com/{platform}_visual_asset_{script.hook_id}.png"

if __name__ == "__main__":
    # Example usage
    from schemas.models import TrendData
    from uuid import uuid4

    engine = GenerationEngine()

    mock_trend = TrendData(
        trend_title="The Future of AI in Creative Arts",
        trend_summary="AI is enabling new forms of artistic expression.",
        niche="AI & Art",
        velocity=80,
        opportunity=90,
    )

    # Generate a script for TikTok
    try:
        result = engine.generate_platform_content(
            trend=mock_trend,
            emotion="inspiration",
            pattern="new_possibilities",
            platform="tiktok",
            content_type="script",
        )
        print("\n--- Generated Content ---")
        print(f"Hook: {result["hook"].hook_text}")
        print(f"Script: {result["script"].script_text[:200]}...")
        visual_url = engine.generate_visual_asset(result["script"], "tiktok")
        print(f"Visual Asset URL: {visual_url}")
    except Exception as e:
        print(f"Error in generation: {e}")
