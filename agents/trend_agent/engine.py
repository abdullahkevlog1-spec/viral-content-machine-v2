import os
from typing import Any

from crewai import Agent, Crew, LLM, Process, Task
from dotenv import load_dotenv
from pydantic import ValidationError

from agents.trend_agent.tasks import TrendDiscoveryTask
from schemas.models import TrendData

DEFAULT_GEMINI_MODEL = "gemini/gemini-2.0-flash"


def create_gemini_llm() -> LLM:
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY must be set before running the Trend Agent.")

    return LLM(
        model=os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL),
        api_key=api_key,
        temperature=0.35,
        max_output_tokens=1024,
        timeout=120,
        max_retries=2,
    )


def create_trend_agent(llm: LLM | None = None) -> Agent:
    return Agent(
        role="Viral Trend Analyst",
        goal=(
            "Find high-velocity trends specifically in Mechanical Toys, "
            "Biomechanical Creatures, and Dark Aesthetic ASMR."
        ),
        backstory=(
            "You are a sharp cultural analyst for short-form video channels. You track visual, "
            "tactile, eerie, mechanical, and sensory signals, then turn them into structured "
            "trend intelligence that creators can act on quickly."
        ),
        llm=llm or create_gemini_llm(),
        verbose=True,
        allow_delegation=False,
    )


def create_trend_crew() -> tuple[Crew, Task]:
    agent = create_trend_agent()
    task = TrendDiscoveryTask(agent).build()
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )
    return crew, task


def _try_validate(candidate: Any) -> TrendData | None:
    if candidate is None:
        return None
    if isinstance(candidate, TrendData):
        return candidate
    try:
        return TrendData.model_validate(candidate)
    except ValidationError:
        return None


def _coerce_trend_data(result: Any, task: Task) -> TrendData:
    task_output = getattr(task, "output", None)
    candidates = (
        getattr(result, "pydantic", None),
        getattr(task_output, "pydantic", None) if task_output else None,
    )

    for candidate in candidates:
        trend_data = _try_validate(candidate)
        if trend_data:
            return trend_data

    to_dict = getattr(result, "to_dict", None)
    if callable(to_dict):
        trend_data = _try_validate(to_dict())
        if trend_data:
            return trend_data

    raw = getattr(result, "raw", None)
    if raw:
        try:
            return TrendData.model_validate_json(raw)
        except ValidationError as exc:
            raise ValueError("Trend Agent returned raw output that was not valid TrendData JSON.") from exc

    raise ValueError("Trend Agent did not return a valid TrendData payload.")


def run_trend_agent() -> TrendData:
    crew, task = create_trend_crew()
    result = crew.kickoff()
    return _coerce_trend_data(result, task)
