import random
from typing import Dict, Any
from schemas.models import Analytics
from uuid import UUID

class InsightsFetcher:
    """
    Fetches performance metrics from social platforms.
    In V3, this would integrate with Facebook Graph API, TikTok API, etc.
    """
    def fetch_metrics(self, hook_id: UUID, platform: str = "tiktok") -> Analytics:
        """
        Fetches metrics for a specific hook on a specific platform.
        Currently returns mock data for V3 demonstration.
        """
        # Simulate varying performance
        views = random.randint(1000, 50000)
        likes = int(views * random.uniform(0.01, 0.15))
        shares = int(likes * random.uniform(0.05, 0.2))
        comments = int(likes * random.uniform(0.02, 0.1))
        
        engagement_rate = (likes + shares + comments) / views if views > 0 else 0.0
        
        return Analytics(
            hook_id=hook_id,
            views=views,
            likes=likes,
            shares=shares,
            comments=comments,
            engagement_rate=engagement_rate
        )

if __name__ == "__main__":
    from uuid import uuid4
    fetcher = InsightsFetcher()
    metrics = fetcher.fetch_metrics(uuid4())
    print(f"Mock Metrics: {metrics.model_dump()}")
