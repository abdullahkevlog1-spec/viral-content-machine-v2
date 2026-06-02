from crewai import Agent, Task

from schemas.models import TrendData


class TrendDiscoveryTask:
    """Builds the structured task for discovering one high-opportunity trend."""

    def __init__(self, agent: Agent) -> None:
        self.agent = agent

    def build(self) -> Task:
        return Task(
            description=(
                "Identify one high-velocity trend with strong content potential inside these "
                "niches: Mechanical Toys, Biomechanical Creatures, and Dark Aesthetic ASMR. "
                "Focus on trends that can become short-form visual content. Score velocity and "
                "opportunity from 0 to 100. Return one concise trend only."
            ),
            expected_output=(
                "A structured TrendData object with trend_title, trend_summary, source, "
                "source_url, and niche fields."
            ),
            agent=self.agent,
            output_pydantic=TrendData,
        )
