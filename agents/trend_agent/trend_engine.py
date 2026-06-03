import os
from typing import List, Dict, Any
from scrapers.reddit_scraper import RedditScraper
from scrapers.google_trends import GoogleTrendsScraper
from crewai import Agent, Crew, Task, LLM
from schemas.models import TrendData
from dotenv import load_dotenv

class TrendEngineV3:
    """
    V3 Trend Engine that aggregates real-world data from Reddit and Google Trends,
    then uses a CrewAI agent to analyze and rank the trends.
    """
    def __init__(self):
        load_dotenv()
        self.reddit = RedditScraper()
        self.google = GoogleTrendsScraper()
        self.llm = self._create_llm()

    def _create_llm(self) -> LLM:
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        return LLM(
            model=os.getenv("GEMINI_MODEL", "gemini/gemini-2.5-flash-lite"),
            api_key=gemini_key,
            temperature=0.35
        )

    def fetch_raw_data(self, subreddits: List[str], keywords: List[str]) -> Dict[str, Any]:
        """Fetches raw data from Reddit and Google Trends."""
        reddit_data = self.reddit.fetch_trending_posts(subreddits)
        google_data = self.google.fetch_daily_trends()
        # Filter google trends by keywords if needed, or just provide them all
        return {
            "reddit": reddit_data,
            "google_trends": google_data
        }

    def analyze_trends(self, raw_data: Dict[str, Any]) -> TrendData:
        """Uses a CrewAI agent to analyze raw data and select the best trend."""
        
        # Format the raw data for the agent
        reddit_summary = "\n".join([f"- {p['title']} (Score: {p['score']}, Sub: {p['subreddit']})" for p in raw_data['reddit'][:10]])
        google_summary = "\n".join([f"- {t['title']}" for t in raw_data['google_trends'][:10]])

        analyst = Agent(
            role="Trend Intelligence Analyst",
            goal="Analyze real-world data from Reddit and Google Trends to identify the single most viral opportunity.",
            backstory="You are an expert in data-driven trend analysis. You look for high-velocity signals across platforms to find content that is about to explode.",
            llm=self.llm,
            verbose=True
        )

        analysis_task = Task(
            description=(
                f"Based on the following real-world data, identify the best trend to create content for.\n\n"
                f"Reddit Trending:\n{reddit_summary}\n\n"
                f"Google Trends:\n{google_summary}\n\n"
                "Evaluate the 'velocity' (how fast it's growing) and 'opportunity' (how well it fits short-form video). "
                "Return a structured TrendData object."
            ),
            expected_output="A TrendData object with trend_title, trend_summary, source, source_url, niche, velocity, and opportunity.",
            agent=analyst,
            output_pydantic=TrendData
        )

        crew = Crew(agents=[analyst], tasks=[analysis_task])
        result = crew.kickoff()
        
        # The result.pydantic should contain the TrendData
        if hasattr(result, 'pydantic') and result.pydantic:
            return result.pydantic
        
        # Fallback if pydantic output fails
        return TrendData(
            trend_title="Data-Driven Trend",
            trend_summary="Analysis of current social signals.",
            source="Aggregated",
            velocity=70,
            opportunity=70
        )

def run_v3_trend_discovery() -> TrendData:
    engine = TrendEngineV3()
    # Default niches/keywords for V3
    subreddits = ["artificial", "technology", "futurism", "ascribe"]
    keywords = ["AI", "Automation", "Robotics"]
    
    raw_data = engine.fetch_raw_data(subreddits, keywords)
    return engine.analyze_trends(raw_data)

if __name__ == "__main__":
    trend = run_v3_trend_discovery()
    print(f"V3 Discovered Trend: {trend.trend_title}")
