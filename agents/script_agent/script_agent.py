"""
Script Agent for Viral Content Machine V2

This module generates full video scripts from hooks using the AIDA/PAS frameworks.
It expands the content pipeline from hooks to executable scripts.
"""

import json
import os

from crewai import Agent, Crew, Task
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, ValidationError
from typing import Optional
from uuid import UUID

from schemas.models import Hook, TrendData, Script

DEFAULT_GEMINI_MODEL = "gemini-2.5-flash-lite"


# Script model is now imported from schemas.models


def create_gemini_chat_llm(temperature: float = 0.7) -> ChatOpenAI:
    """Create a ChatOpenAI LLM instance."""
    load_dotenv()
    return ChatOpenAI(
        model="gpt-4o",
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_API_BASE"),
        temperature=temperature,
    )


class ScriptAgent:
    """
    Generates video scripts from hooks using proven frameworks.
    
    Implements Phase 3 of the roadmap: The Full Content Pipeline.
    - Expands hooks into full scripts using AIDA (Attention, Interest, Desire, Action) or PAS (Problem, Agitate, Solve) frameworks.
    - Adapts scripts for different platforms (TikTok, YouTube Shorts, Facebook, Instagram Reels).
    - Provides scene breakdowns and timing guidance.
    """

    def __init__(self, llm: ChatOpenAI | None = None):
        """Initialize the script agent with an LLM."""
        self.llm = llm or create_gemini_chat_llm(temperature=0.7)

    def create_script_agent(self) -> Agent:
        """Create a CrewAI Agent for script generation."""
        from crewai import LLM
        crew_llm = LLM(
            model="openai/gpt-4o",
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE")
        )
        return Agent(
            role="Script Writer",
            goal="Generate compelling video scripts that expand hooks into full narratives, using proven frameworks like AIDA and PAS.",
            backstory=(
                "You are an award-winning screenwriter and content strategist with expertise in short-form video. "
                "You understand how to structure narratives for maximum engagement, using psychological triggers and storytelling techniques. "
                "You can adapt scripts for different platforms and audiences, ensuring each scene serves a purpose. "
                "You provide detailed scene breakdowns with timing and visual cues."
            ),
            llm=crew_llm,
            allow_delegation=False,
            verbose=True,
        )

    def generate_script(
        self,
        hook: Hook,
        trend: TrendData,
        framework: str = "AIDA",
        platform: str = "tiktok",
        duration_seconds: int = 30,
    ) -> Script:
        agent = self.create_script_agent()
        
        task_description = (
            f"Generate a compelling video script for the following:\n\n"
            f"Hook: {hook.hook_text}\n"
            f"Trend: {trend.trend_title}\n"
            f"Emotion: {hook.emotion}\n"
            f"Pattern: {hook.pattern}\n\n"
            f"Framework: {framework}\n"
            f"Platform: {platform}\n\n"
            f"Create a detailed script with:\n"
            f"1. Scene-by-scene breakdown\n"
            f"2. Dialogue or voiceover\n"
            f"3. Visual cues and transitions\n"
            f"4. Timing for each scene\n"
            f"5. Call-to-action at the end\n\n"
            f"Output the result strictly in the following JSON format:\n"
            f"{{'script_text': '...', 'framework': '{framework}', 'platform': '{platform}', 'duration_seconds': {duration_seconds}, 'scene_count': <number>, 'reasoning': '...', 'model_used': 'gpt-4o'}}"
        )

        task = Task(
            description=task_description,
            agent=agent,
            expected_output="A JSON object following the Script model.",
        )
        crew = Crew(agents=[agent], tasks=[task])
        
        try:
            result = crew.kickoff()
            result_str = str(result)
            if "```json" in result_str:
                result_str = result_str.split("```json")[1].split("```")[0].strip()
            elif "```" in result_str:
                result_str = result_str.split("```")[1].split("```")[0].strip()
            parsed_result = json.loads(result_str)
            return Script(
                hook_id=hook.id,
                trend_id=trend.id,
                **parsed_result
            )
        except Exception as e:
            print(f"Script generation failed, using fallback: {e}")
            return Script(
                hook_id=hook.id,
                trend_id=trend.id,
                script_text="Scene 1: [0-3s] Hook - The secret to viral AI videos is finally out...",
                framework=framework,
                platform=platform,
                duration_seconds=duration_seconds,
                scene_count=5,
                reasoning="Fallback script due to generation error.",
                model_used="fallback-v3"
            )

    def _get_framework_description(self, framework: str) -> str:
        """Get a description of the framework to use."""
        if framework.upper() == "AIDA":
            return (
                "AIDA Framework:\n"
                "- Attention: Hook the viewer immediately (0-3 seconds)\n"
                "- Interest: Build curiosity and maintain engagement (3-15 seconds)\n"
                "- Desire: Show the benefit or emotional payoff (15-25 seconds)\n"
                "- Action: Call-to-action (25-30 seconds)"
            )
        elif framework.upper() == "PAS":
            return (
                "PAS Framework:\n"
                "- Problem: Identify a pain point or challenge (0-5 seconds)\n"
                "- Agitate: Amplify the problem and its consequences (5-20 seconds)\n"
                "- Solve: Present the solution or resolution (20-30 seconds)"
            )
        else:
            return "Use a narrative framework that best fits the trend and emotion."

    def _get_platform_guidance(self, platform: str, duration_seconds: int) -> str:
        """Get platform-specific guidance."""
        guidance = {
            "tiktok": (
                "TikTok Guidance:\n"
                "- Fast-paced editing with quick cuts\n"
                "- Trending sounds and music integration\n"
                "- Text overlays for emphasis\n"
                "- Vertical video (9:16 aspect ratio)\n"
                "- Hook in the first 1-2 seconds"
            ),
            "youtube_shorts": (
                "YouTube Shorts Guidance:\n"
                "- Vertical video (9:16 aspect ratio)\n"
                "- Engaging intro to prevent scroll-away\n"
                "- Clear visual storytelling\n"
                "- End screen with subscribe CTA\n"
                "- 15-60 seconds optimal"
            ),
            "facebook": (
                "Facebook Guidance:\n"
                "- Can be horizontal or vertical\n"
                "- Captions for sound-off viewing\n"
                "- Community engagement focus\n"
                "- Longer-form storytelling (30-90 seconds)\n"
                "- Include share-worthy moments"
            ),
            "instagram_reels": (
                "Instagram Reels Guidance:\n"
                "- Vertical video (9:16 aspect ratio)\n"
                "- Trending audio and effects\n"
                "- Quick, punchy pacing\n"
                "- 15-90 seconds optimal\n"
                "- Strong hook in first frame"
            ),
        }
        return guidance.get(platform, "Adapt the script for the target platform.")


def generate_script_from_hook(
    hook: Hook,
    trend: TrendData,
    framework: str = "AIDA",
    platform: str = "tiktok",
) -> Script:
    """
    Convenience function to generate a script from a hook.
    
    Args:
        hook: The Hook object.
        trend: The TrendData object.
        framework: The framework to use.
        platform: The target platform.
    
    Returns:
        A Script object.
    """
    agent = ScriptAgent()
    return agent.generate_script(hook, trend, framework, platform)


if __name__ == "__main__":
    # Example usage (requires valid API keys)
    from schemas.models import Hook, TrendData, Script
    from uuid import uuid4

    # Create mock objects for testing
    trend = TrendData(
        trend_title="The Rise of AI-Generated Content",
        trend_summary="AI tools are revolutionizing how creators produce content.",
        niche="Technology",
        velocity=85,
        opportunity=90,
    )

    hook = Hook(
        trend_id=trend.id,
        hook_text="This AI tool just changed everything about how I create videos.",
        emotion="excitement",
        pattern="the_secret",
    )

    try:
        script = generate_script_from_hook(hook, trend, framework="AIDA", platform="tiktok")
        print(f"Generated Script:\n{script.script_text}")
    except Exception as e:
        print(f"Error generating script: {e}")
