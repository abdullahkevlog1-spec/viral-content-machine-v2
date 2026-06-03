import json
import os
from typing import Dict, Any
from crewai import Agent, Crew, Task
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import ValidationError
from database.hook_library import HookLibrary
from schemas.models import Hook, Reflection

class CriticAgentV3:
    """
    V3 Critic Agent that uses a composite scoring function:
    - Pattern Match Score (Similarity to successful hooks)
    - Constraint Check (Generic Filter)
    - LLM Reasoning (Nuance & Readability)
    """
    def __init__(self, llm: ChatGoogleGenerativeAI | None = None):
        load_dotenv()
        self.llm = llm or self._create_llm()
        self.hook_library = HookLibrary()
        self.generic_filters = ["Unlock", "Revolutionize", "Game-changer", "Mastering", "The ultimate guide"]

    def _create_llm(self) -> ChatGoogleGenerativeAI:
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        return ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite").replace("gemini/", ""),
            google_api_key=api_key,
            temperature=0.3
        )

    def _calculate_pattern_match(self, hook_text: str) -> float:
        """Calculates similarity to successful hooks in the database."""
        results = self.hook_library.search_hooks(hook_text, n_results=1)
        if not results:
            return 50.0
        # Distance is usually 0-2 for L2, where 0 is identical.
        # We'll normalize it to a 0-100 score.
        distance = results[0]['distance']
        score = max(0, 100 - (distance * 50)) 
        return score

    def _check_generic_filters(self, hook_text: str) -> float:
        """Checks for generic AI-slop words."""
        penalty = 0
        for word in self.generic_filters:
            if word.lower() in hook_text.lower():
                penalty += 20
        return max(0, 100 - penalty)

    def criticize_hook(self, hook: Hook) -> Reflection:
        # 1. Pattern Match Score
        pattern_score = self._calculate_pattern_match(hook.hook_text)
        
        # 2. Constraint Check
        constraint_score = self._check_generic_filters(hook.hook_text)
        
        # 3. LLM Reasoning for Nuance
        agent = Agent(
            role="Nuance & Readability Critic",
            goal="Evaluate the emotional impact and readability of a social media hook.",
            backstory="You are a linguistic expert who understands human psychology and how words evoke feelings.",
            llm=self.llm,
            verbose=True
        )

        task = Task(
            description=(
                f"Evaluate this hook for emotional impact and readability:\n\n"
                f"Hook: {hook.hook_text}\n"
                f"Emotion: {hook.emotion}\n"
                f"Pattern: {hook.pattern}\n\n"
                "Provide a score from 0-100 and a brief lesson on why it works or fails."
            ),
            expected_output="A JSON object with 'nuance_score' and 'lesson'.",
            agent=agent
        )

        crew = Crew(agents=[agent], tasks=[task])
        result = crew.kickoff()
        
        # Parse LLM result
        try:
            result_str = str(result)
            if "```json" in result_str:
                result_str = result_str.split("```json")[1].split("```")[0].strip()
            parsed = json.loads(result_str)
            nuance_score = float(parsed.get('nuance_score', 70))
            lesson = parsed.get('lesson', "No specific lesson provided.")
        except:
            nuance_score = 70.0
            lesson = "Failed to parse LLM nuance check."

        # Composite Score Calculation
        # Formula: (Pattern_Match * 0.4) + (Constraint_Check * 0.4) + (LLM_Reasoning * 0.2)
        final_score = int((pattern_score * 0.4) + (constraint_score * 0.4) + (nuance_score * 0.2))

        return Reflection(
            hook_id=hook.id,
            viral_score=final_score,
            lesson=lesson,
            reasoning_update=f"Pattern Match: {pattern_score:.1f}, Constraint: {constraint_score:.1f}, Nuance: {nuance_score:.1f}"
        )

if __name__ == "__main__":
    critic = CriticAgentV3()
    mock_hook = Hook(trend_id=None, hook_text="Unlock the secret to AI revolutionizing your business today!", emotion="curiosity", pattern="the_secret")
    reflection = critic.criticize_hook(mock_hook)
    print(f"V3 Final Score: {reflection.viral_score}")
    print(f"Reasoning: {reflection.reasoning_update}")
