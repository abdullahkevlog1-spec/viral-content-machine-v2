import json
from typing import Any
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from schemas.models import Hook, Reflection

class CriticAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.7)

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

        task = Task(description=task_description, agent=agent, expected_output="A JSON object following the Reflection Pydantic model.")
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
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"Error parsing critic agent output: {e}")
            raise
