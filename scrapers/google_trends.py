from pytrends.request import TrendReq
from typing import List, Dict, Any
import pandas as pd

class GoogleTrendsScraper:
    """
    Scrapes daily search trends and related queries using pytrends.
    """
    def __init__(self, hl='en-US', tz=360):
        self.pytrends = TrendReq(hl=hl, tz=tz, timeout=(10, 25))

    def fetch_daily_trends(self, country: str = 'united_states') -> List[Dict[str, Any]]:
        """
        Fetches daily search trends for a specific country.
        """
        try:
            df = self.pytrends.trending_searches(pn=country)
            trends = df[0].tolist()
            return [{"title": trend, "source": "google_trends", "country": country} for trend in trends]
        except Exception as e:
            print(f"Error fetching daily trends: {e}")
            return []

    def fetch_related_queries(self, keywords: List[str]) -> Dict[str, Any]:
        """
        Fetches related queries for a list of keywords to identify rising topics.
        """
        try:
            self.pytrends.build_payload(keywords, timeframe='now 1-d')
            related = self.pytrends.related_queries()
            return related
        except Exception as e:
            print(f"Error fetching related queries: {e}")
            return {}

if __name__ == "__main__":
    scraper = GoogleTrendsScraper()
    print("GoogleTrendsScraper initialized.")
    # trends = scraper.fetch_daily_trends()
    # print(trends[:5])
