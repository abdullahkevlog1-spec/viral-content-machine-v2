import json
import os

from crewai import Agent, Crew, Task
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from schemas.models import Hook, TrendData

DEFAULT_GEMINI_MODEL = "gemini-2.5-flash-lite"


def create_gemini_chat_llm(temperature: float = 0.7) -> ChatOpenAI:
    load_dotenv()
    return ChatOpenAI(
        model="gpt-4o",
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_API_BASE"),
        temperature=temperature,
    )


class HookAgent:
    def __init__(self, llm: ChatOpenAI | None = None):
        self.llm = llm or create_gemini_chat_llm(temperature=0.7)

    def create_hook_agent(self) -> Agent:
        # CrewAI 0.14+ prefers LLM objects or specific strings. 
        # Since we are using a proxy, we'll wrap it in a CrewAI LLM if it's not already.
        from crewai import LLM
        crew_llm = LLM(
            model="openai/gpt-4o",
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE")
        )
        return Agent(
            role="Hook Creator",
            goal="Generate compelling and viral social media hooks based on current trends and strategic guidance.",
            backstory=(
                "You are a master of viral content creation, skilled in crafting hooks that grab attention, "
                "evoke strong emotions, and drive engagement. You understand the nuances of different "
                "social media platforms and can tailor hooks to maximize their impact. You strictly adhere "
                "to the provided emotion and pattern, and ensure your output is always in the specified JSON format."
            ),
            llm=crew_llm,
            allow_delegation=False,
            verbose=True,
        )

    def generate_hook(self, trend: TrendData, emotion: str, pattern: str, platform: str = "general") -> Hook:
        agent = self.create_hook_agent()
        task_description = (
            f"Create a viral social media hook for the trend: '{trend.trend_title}'. "
            f"The hook should evoke the emotion: '{emotion}' and follow the pattern: '{pattern}'. "
            f"The hook must be highly engaging and designed to go viral. "
            f"Consider the target platform: {platform}. "\
            f"Provide your reasoning for why this hook will be viral. "
            f"Output the result strictly in the following JSON format, adhering to the Hook Pydantic model:\n"
            f"{{'hook_text': '...', 'emotion': '{emotion}', 'pattern': '{pattern}', 'reasoning': '...', 'model_used': 'gpt-4o'}}"
        )

        task = Task(
            description=task_description,
            agent=agent,
            expected_output="A JSON object following the Hook Pydantic model.",
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
            return Hook(trend_id=trend.id, **parsed_result)
        except Exception as e:
            print(f"Hook generation failed, using fallback: {e}")
            return Hook(
                trend_id=trend.id,
                hook_text="The secret to viral AI videos is finally out, and it's not what you think.",
                emotion=emotion,
                pattern=pattern,
                reasoning="This hook uses curiosity and a 'secret' pattern to drive clicks.",
                model_used="fallback-v3"
            )
