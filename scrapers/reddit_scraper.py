import os
from typing import List, Dict, Any
import praw
from dotenv import load_dotenv

class RedditScraper:
    """
    Scrapes trending posts from Reddit using PRAW.
    """
    def __init__(self):
        load_dotenv()
        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT", "ViralContentMachineV3/0.1"),
        )

    def fetch_trending_posts(self, subreddits: List[str], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Fetches hot and rising posts from specified subreddits.
        """
        trending_data = []
        for sub_name in subreddits:
            try:
                subreddit = self.reddit.subreddit(sub_name)
                # Combine hot and rising
                posts = list(subreddit.hot(limit=limit)) + list(subreddit.rising(limit=limit))
                
                for post in posts:
                    # Basic velocity metric: score / (time_since_creation)
                    # For simplicity, we just take the score and upvote ratio
                    trending_data.append({
                        "title": post.title,
                        "url": post.url,
                        "score": post.score,
                        "upvote_ratio": post.upvote_ratio,
                        "num_comments": post.num_comments,
                        "subreddit": sub_name,
                        "created_utc": post.created_utc,
                        "content": post.selftext[:500] if post.is_self else "",
                        "source": "reddit"
                    })
            except Exception as e:
                print(f"Error scraping r/{sub_name}: {e}")
        
        # Sort by score as a simple ranking
        return sorted(trending_data, key=lambda x: x['score'], reverse=True)

if __name__ == "__main__":
    # Example usage (requires credentials)
    scraper = RedditScraper()
    # Mocking for now since we don't have real credentials in the environment yet
    print("RedditScraper initialized. Ready for API credentials.")
