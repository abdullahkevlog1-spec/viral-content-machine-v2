# Gap Analysis: Viral Content Machine V2

This document outlines the discrepancies between the **Architecture Analysis Report** and the current state of the `viral-content-machine-v2` repository.

## 1. Component Gaps

| Component | Status in Report | Status in Repository | Gap / Action Item |
| :--- | :--- | :--- | :--- |
| **Trend Discovery** | "Weak Link": random fallback trends. | `engine.py` uses CrewAI but lacks real API tools. | Integrate Google Search/Trends or Reddit APIs. |
| **Social Listener** | "Placeholder": hardcoded signals. | **Missing**: No `social_listener.py` found. | Implement social listening logic or placeholder for V3. |
| **Memory & Learning** | "Incomplete": lacks logic to update strategy. | **Missing**: No `self_improve.py` found. Schemas exist but are unused. | Implement `self_improve.py` to update `strategy_memory`. |
| **Content Pipeline** | Stops at Hook Generation. | `main.py` only runs Trend -> Hook -> Critic. | Add Script and Storyboard agents as per Phase 3. |

## 2. Technical Inconsistencies

*   **Schema Mismatch:**
    *   `models.py`: `Reflection` uses `viral_score`.
    *   `main.py`: Tries to access `reflection.performance_score`.
    *   `supabase_schema.sql`: `reflections` table uses `performance_score`.
*   **Missing Files:** The report mentions `social_listener.py` and `self_improve.py`, but these are not in the repository.
*   **Static Trends:** `TrendDiscoveryTask` description mentions specific niches but doesn't provide tools for real-time discovery.

## 3. Implementation Plan for V3 (Manus-led)

1.  **Fix Inconsistencies:** Align `models.py`, `main.py`, and `supabase_schema.sql` to use consistent field names (standardizing on `viral_score`).
2.  **Enhance Trend Discovery:** Add a search tool to the `TrendAgent` to move beyond "AI imagination".
3.  **Implement Missing Agents:** Create `ScriptAgent` to expand the pipeline.
4.  **Bootstrap Self-Improvement:** Implement a basic version of `self_improve.py` that utilizes the `StrategyMemory` schema.
5.  **Refine Critic:** Update the `CriticAgent` prompt to include the scoring formula mentioned in the report.
