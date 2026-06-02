import json
import os

from crewai import Agent, Crew, Task
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import ValidationError

from schemas.models import Hook, Reflection

DEFAULT_GEMINI_MODEL = "gemini-2.5-flash-lite"


def create_gemini_chat_llm(temperature: float = 0.7) -> ChatGoogleGenerativeAI:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY must be set before running CriticAgent.")

    return ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).replace("gemini/", ""),
        google_api_key=api_key,
        temperature=temperature,
    )


class CriticAgent:
    def __init__(self, llm: ChatGoogleGenerativeAI | None = None):
        self.llm = llm or create_gemini_chat_llm(temperature=0.7)

    def create_critic_agent(self) -> Agent:
        return Agent(
            role="Hook Critic",
            goal="Evaluate social media hooks for virality, adherence to AGI standards, and provide constructive feedback.",
            backstory=(
                "You are a highly discerning critic with an unparalleled understanding of what makes content viral. "
                "You have a keen eye for 'AI slop' and generic phrasing, and you demand originality, impact, and emotional resonance. "
                "Your feedback is direct, actionable, and designed to elevate the quality of hooks to an AGI standard. "
                "You will assign a viral score (1-100) and provide a lesson on what worked or failed, along with reasoning for any score below 85."
            ),
            llm=self.llm,
            allow_delegation=False,
            verbose=True,
        )

    def criticize_hook(self, hook: Hook) -> Reflection:
        agent = self.create_critic_agent()
        task_description = (
            f"Critique the following social media hook for virality and adherence to AGI standards (no slop, no generic AI phrasing):\n\n"
            f"Hook Text: {hook.hook_text}\n"
            f"Emotion: {hook.emotion}\n"
            f"Pattern: {hook.pattern}\n\n"
            f"Assign a viral_score (1-100). If the score is below 85, provide a detailed 'lesson' on what worked/failed and 'reasoning_update' for why the score is low and how to improve it. "
            f"Output the result strictly in the following JSON format, adhering to the Reflection Pydantic model."
        )

        task = Task(
            description=task_description,
            agent=agent,
            expected_output="A JSON object following the Reflection Pydantic model.",
        )
        crew = Crew(agents=[agent], tasks=[task])
        result = crew.kickoff()

        try:
            result_str = str(result)
            if "```json" in result_str:
                result_str = result_str.split("```json")[1].split("```")[0].strip()
            elif "```" in result_str:
                result_str = result_str.split("```")[1].split("```")[0].strip()
            parsed_result = json.loads(result_str)
            reflection_data = Reflection(hook_id=hook.id, **parsed_result)
            return reflection_data
        except (json.JSONDecodeError, ValidationError) as exc:
            print(f"Error parsing critic agent output: {exc}")
            raise
