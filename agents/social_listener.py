"""
Social Listener Module for Viral Content Machine V2

This module monitors social signals and extracts viral patterns from real platforms.
Currently a placeholder; full implementation planned for V3 with real API integrations.
"""

import re
from typing import Optional
from dataclasses import dataclass


@dataclass
class SocialSignal:
    """Represents a viral signal detected from social media."""
    platform: str  # "tiktok", "reddit", "twitter", "youtube"
    content_type: str  # "hook", "trend", "sound", "format"
    signal_text: str
    engagement_count: int
    velocity: int  # 0-100 (how fast it's growing)
    source_url: Optional[str] = None


class SocialListener:
    """
    Monitors social media platforms for viral signals.
    
    Planned integrations for V3:
    - TikTok API: Extract trending sounds and hashtags
    - Reddit PRAW: Monitor r/viral and niche subreddits
    - Twitter API: Track trending topics and engagement patterns
    - YouTube API: Analyze top-performing shorts and thumbnails
    - Google Trends: Detect search velocity spikes
    
    Current implementation: Placeholder with regex-based hook extraction.
    """

    def __init__(self):
        """Initialize the social listener."""
        self.platforms = ["tiktok", "reddit", "twitter", "youtube"]
        self.hook_patterns = self._compile_hook_patterns()

    def _compile_hook_patterns(self) -> dict:
        """Compile regex patterns for common viral hooks."""
        return {
            "curiosity_gap": re.compile(r"(wait for it|you won't believe|this is crazy|hold on)", re.IGNORECASE),
            "urgency": re.compile(r"(limited time|only \d+|before it's gone|hurry)", re.IGNORECASE),
            "controversy": re.compile(r"(unpopular opinion|hot take|everyone's wrong|plot twist)", re.IGNORECASE),
            "emotional": re.compile(r"(made me cry|heartbreaking|beautiful|touching)", re.IGNORECASE),
            "educational": re.compile(r"(you didn't know|life hack|pro tip|secret)", re.IGNORECASE),
        }

    def extract_hooks_from_text(self, text: str) -> list[dict]:
        """
        Extract potential viral hooks from text using regex patterns.
        
        Args:
            text: The text to analyze.
        
        Returns:
            A list of detected hook patterns with their types.
        """
        detected_hooks = []
        
        for hook_type, pattern in self.hook_patterns.items():
            matches = pattern.findall(text)
            if matches:
                detected_hooks.append({
                    "type": hook_type,
                    "matches": matches,
                    "count": len(matches),
                })
        
        return detected_hooks

    def get_trending_signals(self, platform: str = "tiktok", limit: int = 10) -> list[SocialSignal]:
        """
        Get trending signals from a platform.
        
        Note: This is a placeholder. Real implementation will use platform APIs.
        
        Args:
            platform: The platform to monitor.
            limit: Number of signals to return.
        
        Returns:
            A list of SocialSignal objects.
        """
        # Placeholder: Return mock signals
        mock_signals = [
            SocialSignal(
                platform=platform,
                content_type="trend",
                signal_text="AI-generated content",
                engagement_count=1_500_000,
                velocity=95,
                source_url=f"https://{platform}.com/trend/ai-content",
            ),
            SocialSignal(
                platform=platform,
                content_type="sound",
                signal_text="Trending audio: 'Never Gonna Give You Up'",
                engagement_count=2_300_000,
                velocity=88,
                source_url=f"https://{platform}.com/sound/trending-audio",
            ),
            SocialSignal(
                platform=platform,
                content_type="hook",
                signal_text="Wait for it...",
                engagement_count=890_000,
                velocity=82,
                source_url=f"https://{platform}.com/hook/wait-for-it",
            ),
        ]
        
        return mock_signals[:limit]

    def analyze_platform_trends(self, platform: str) -> dict:
        """
        Analyze trends for a specific platform.
        
        Args:
            platform: The platform to analyze.
        
        Returns:
            A dictionary with trend analysis.
        """
        signals = self.get_trending_signals(platform, limit=5)
        
        return {
            "platform": platform,
            "signals_count": len(signals),
            "top_signal": signals[0] if signals else None,
            "average_velocity": sum(s.velocity for s in signals) / len(signals) if signals else 0,
            "signals": signals,
        }

    def detect_emerging_patterns(self, texts: list[str]) -> dict:
        """
        Detect emerging patterns across multiple texts.
        
        Args:
            texts: A list of texts to analyze.
        
        Returns:
            A dictionary with pattern analysis.
        """
        pattern_counts = {}
        
        for text in texts:
            hooks = self.extract_hooks_from_text(text)
            for hook in hooks:
                hook_type = hook["type"]
                pattern_counts[hook_type] = pattern_counts.get(hook_type, 0) + hook["count"]
        
        # Sort by frequency
        sorted_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "total_texts_analyzed": len(texts),
            "patterns_detected": dict(sorted_patterns),
            "dominant_pattern": sorted_patterns[0][0] if sorted_patterns else None,
        }


def monitor_social_signals(platform: str = "tiktok") -> dict:
    """
    Convenience function to monitor social signals.
    
    Args:
        platform: The platform to monitor.
    
    Returns:
        A dictionary with signal analysis.
    """
    listener = SocialListener()
    return listener.analyze_platform_trends(platform)


if __name__ == "__main__":
    # Example usage
    listener = SocialListener()
    
    # Extract hooks from sample text
    sample_text = "Wait for it! This life hack will blow your mind. You won't believe what happens next."
    hooks = listener.extract_hooks_from_text(sample_text)
    print(f"Detected hooks: {hooks}")
    
    # Get trending signals
    signals = listener.get_trending_signals("tiktok", limit=3)
    print(f"\nTrending signals: {signals}")
    
    # Analyze patterns
    texts = [
        "Wait for it! This is crazy.",
        "You won't believe this plot twist!",
        "Limited time offer before it's gone!",
    ]
    patterns = listener.detect_emerging_patterns(texts)
    print(f"\nPattern analysis: {patterns}")
