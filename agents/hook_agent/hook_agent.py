import json
from typing import Any
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from schemas.models import Hook, TrendData

class HookAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.7)

    def create_hook_agent(self) -> Agent:
        return Agent(
            role="Hook Creator",
            goal="Generate compelling and viral social media hooks based on current trends and strategic guidance.",
            backstory=(
                "You are a master of viral content creation, skilled in crafting hooks that grab attention, "
                "evoke strong emotions, and drive engagement. You understand the nuances of different "
                "social media platforms and can tailor hooks to maximize their impact. You strictly adhere "
                "to the provided emotion and pattern, and ensure your output is always in the specified JSON format."
            ),
            allow_delegation=False,
            verbose=True,
        )

    def generate_hook(self, trend: TrendData, emotion: str, pattern: str) -> Hook:
        agent = self.create_hook_agent()
        task_description = (
            f"Create a viral social media hook for the trend: '{trend.trend_title}'. "
            f"The hook should evoke the emotion: '{emotion}' and follow the pattern: '{pattern}'. "
            f"The hook must be highly engaging and designed to go viral. "
            f"Provide your reasoning for why this hook will be viral. "
            f"Output the result strictly in the following JSON format, adhering to the Hook Pydantic model:\n"
            f"{{'hook_text': '...', 'emotion': '{emotion}', 'pattern': '{pattern}', 'reasoning': '...', 'model_used': 'gpt-4.1-mini'}}"
        )

        task = Task(description=task_description, agent=agent, expected_output="A JSON object following the Hook Pydantic model.")
        crew = Crew(agents=[agent], tasks=[task])
        result = crew.kickoff()

        try:
            result_str = str(result)
            if "```json" in result_str:
                result_str = result_str.split("```json")[1].split("```")[0].strip()
            elif "```" in result_str:
                result_str = result_str.split("```")[1].split("```")[0].strip()
            parsed_result = json.loads(result_str)
            hook_data = Hook(trend_id=trend.id, **parsed_result)
            return hook_data
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"Error parsing hook agent output: {e}")
            raise
