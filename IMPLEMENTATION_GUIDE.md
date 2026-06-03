# Implementation Guide: Viral Content Machine V2 Enhancements

## Overview

This document outlines the enhancements made to the Viral Content Machine V2 based on the Architecture Analysis Report. The improvements focus on fixing technical inconsistencies, implementing missing components, and laying the groundwork for the V3 roadmap.

---

## 1. Fixed Issues

### 1.1 Schema Inconsistencies

**Problem:** The codebase had conflicting field names for viral scores:
- `models.py`: Used `viral_score` in the `Reflection` model
- `main.py`: Tried to access `reflection.performance_score`
- `supabase_schema.sql`: Used `performance_score` in the reflections table

**Solution:** Standardized all references to use `viral_score`:
- Updated `supabase_schema.sql` to use `viral_score` in the reflections table
- Updated `main.py` to access `reflection.viral_score`

**Files Modified:**
- `supabase_schema.sql` (line 32)
- `main.py` (line 45)

### 1.2 Missing Database Fields

**Problem:** The `trends` table was missing `velocity` and `opportunity` fields that are defined in the `TrendData` model.

**Solution:** Added the missing fields to the `trends` table in `supabase_schema.sql`:
```sql
velocity integer default 0 check (velocity >= 0 and velocity <= 100),
opportunity integer default 0 check (opportunity >= 0 and opportunity <= 100),
```

**Files Modified:**
- `supabase_schema.sql` (lines 12-13)

---

## 2. New Components Implemented

### 2.1 Self-Improvement Agent (`agents/self_improve.py`)

**Purpose:** Implements the feedback loop for autonomous self-optimization (Phase 4 of the roadmap).

**Key Features:**
- **Performance Analysis:** Calculates engagement rates and classifies performance tiers (viral, strong, moderate, weak)
- **Strategy Updates:** Converts critic reflections into strategy memory updates
- **Batch Processing:** Processes multiple reflections to aggregate recommendations
- **Recommendations Engine:** Provides emotion and pattern recommendations for the next generation cycle

**Usage:**
```python
from agents.self_improve import SelfImproveAgent
from memory.database import SupabaseManager

db_manager = SupabaseManager()
agent = SelfImproveAgent(db_manager)

# Update strategies from recent reflections
updated_strategies = agent.batch_update_strategies(limit=10)

# Get recommendations for next cycle
recommendations = agent.get_strategy_recommendations(niche="general")
```

**Integration:** Called in `main.py` as Phase 5 (optional).

---

### 2.2 Script Agent (`agents/script_agent/script_agent.py`)

**Purpose:** Expands hooks into full video scripts using proven frameworks (Phase 3 of the roadmap).

**Key Features:**
- **Framework Support:** Implements AIDA (Attention, Interest, Desire, Action) and PAS (Problem, Agitate, Solve) frameworks
- **Platform Adaptation:** Generates platform-specific scripts for TikTok, YouTube Shorts, Facebook, and Instagram Reels
- **Scene Breakdown:** Provides detailed scene-by-scene guidance with timing and visual cues
- **Extensible Design:** Easy to add new frameworks and platforms

**Usage:**
```python
from agents.script_agent.script_agent import ScriptAgent
from schemas.models import Hook, TrendData

script_agent = ScriptAgent()
script = script_agent.generate_script(
    hook=hook,
    trend=trend,
    framework="AIDA",
    platform="tiktok",
    duration_seconds=30,
)
```

**Integration:** Called in `main.py` as Phase 4 (optional).

---

### 2.3 Social Listener (`agents/social_listener.py`)

**Purpose:** Monitors social signals and extracts viral patterns (placeholder for V3 full implementation).

**Key Features:**
- **Hook Pattern Detection:** Uses regex to identify common viral hooks (curiosity gap, urgency, controversy, emotional, educational)
- **Trending Signal Monitoring:** Placeholder for real API integrations (TikTok, Reddit, Twitter, YouTube)
- **Pattern Analysis:** Detects emerging patterns across multiple texts
- **Extensible Architecture:** Ready for real API integrations in V3

**Usage:**
```python
from agents.social_listener import SocialListener

listener = SocialListener()

# Extract hooks from text
hooks = listener.extract_hooks_from_text("Wait for it! This is crazy.")

# Get trending signals
signals = listener.get_trending_signals("tiktok", limit=5)

# Analyze patterns
patterns = listener.detect_emerging_patterns(texts)
```

**Integration:** Called in `main.py` as Phase 0 (optional).

---

## 3. Updated Pipeline

The enhanced `main.py` now includes the following phases:

| Phase | Component | Status | Purpose |
| :--- | :--- | :--- | :--- |
| 0 | Social Listener | Optional | Monitor trending signals from social platforms |
| 1 | Trend Discovery | Required | Discover high-velocity trends |
| 2 | Hook Generation | Required | Generate viral hooks from trends |
| 3 | Hook Critique | Required | Evaluate hooks and provide feedback |
| 4 | Script Generation | Optional | Expand hooks into full video scripts |
| 5 | Self-Improvement | Optional | Update strategy memory from performance data |

---

## 4. Database Schema Updates

### 4.1 Trends Table
```sql
CREATE TABLE trends (
    id UUID PRIMARY KEY,
    trend_title TEXT NOT NULL,
    trend_summary TEXT,
    source TEXT,
    source_url TEXT,
    niche TEXT,
    velocity INTEGER (0-100),      -- NEW
    opportunity INTEGER (0-100),   -- NEW
    created_at TIMESTAMP
);
```

### 4.2 Reflections Table
```sql
CREATE TABLE reflections (
    id UUID PRIMARY KEY,
    hook_id UUID REFERENCES hooks(id),
    viral_score INTEGER (1-100),   -- CHANGED from performance_score
    lesson TEXT,
    reasoning_update TEXT,
    created_at TIMESTAMP
);
```

---

## 5. Roadmap Alignment

### Phase 1: Real-World Intelligence ✅ (Partial)
- ✅ Social Listener placeholder created
- ⏳ Pending: Real API integrations (Google Trends, Reddit PRAW, TikTok/YouTube scrapers)

### Phase 2: Objective Evaluation ⏳ (Future)
- ⏳ Hook Database with vector search
- ⏳ Metric-driven critic with scoring formula

### Phase 3: Full Content Pipeline ✅ (Partial)
- ✅ Script Agent implemented (AIDA/PAS frameworks)
- ✅ Platform adaptation for TikTok, YouTube Shorts, Facebook, Instagram Reels
- ⏳ Pending: Multi-modal generation (Stable Diffusion XL, Flux)

### Phase 4: Autonomous Self-Optimization ✅ (Partial)
- ✅ Self-Improve Agent implemented
- ✅ Strategy memory updates from reflections
- ⏳ Pending: Full RLHF and A/B testing engine

---

## 6. Next Steps for V3

### 6.1 Real API Integrations
1. **Google Trends API:** Replace placeholder with real search interest data
2. **Reddit PRAW:** Scrape r/viral and niche subreddits for emerging trends
3. **TikTok/YouTube Scrapers:** Extract trending audio and visual hooks
4. **Twitter API:** Monitor trending topics and engagement patterns

### 6.2 Enhanced Critic
1. Implement the scoring formula: `Score = (Pattern_Match * 0.4) + (Engagement_Prediction * 0.4) + (LLM_Reasoning * 0.2)`
2. Add a hook database with vector search (ChromaDB/Pinecone)
3. Compare generated hooks against historically viral hooks

### 6.3 Multi-Modal Generation
1. Integrate Stable Diffusion XL or Flux for thumbnail generation
2. Add image carousel generation for multi-image posts
3. Implement audio synthesis for voiceovers

### 6.4 Advanced Self-Improvement
1. Implement full RLHF with weight updates to `strategy_state.json`
2. Create an A/B testing engine for automatic variation generation
3. Add reinforcement learning to optimize for platform-specific metrics

### 6.5 Orchestration Upgrade
1. Transition from custom scripts to **LangGraph** for better state management
2. Implement circular loops for continuous optimization
3. Add monitoring dashboard for "Agent Hallucination Rate" vs. "Real Trend Alignment"

---

## 7. Testing & Validation

### 7.1 Unit Tests
Create test files for each new component:
- `tests/test_self_improve.py`
- `tests/test_script_agent.py`
- `tests/test_social_listener.py`

### 7.2 Integration Tests
- Test the full pipeline from trend discovery to script generation
- Validate database schema consistency
- Test error handling and fallback mechanisms

### 7.3 Performance Tests
- Monitor API response times
- Track LLM token usage and costs
- Measure pipeline execution time

---

## 8. Configuration & Deployment

### 8.1 Environment Variables
Ensure the following are set in your `.env` file:
```
GEMINI_API_KEY=<your-api-key>
SUPABASE_URL=<your-supabase-url>
SUPABASE_KEY=<your-supabase-key>
GEMINI_MODEL=gemini-2.5-flash-lite
```

### 8.2 Database Setup
Run the updated `supabase_schema.sql` to initialize the database:
```bash
supabase db push
```

### 8.3 Running the Pipeline
```bash
python main.py
```

---

## 9. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  Viral Content Machine V2                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Phase 0: Social Listener                                   │
│  ├─ Extract trending signals from TikTok, Reddit, Twitter   │
│  └─ Detect emerging hook patterns                           │
│                                                              │
│  Phase 1: Trend Discovery                                   │
│  ├─ Query Google Trends, Reddit, YouTube                    │
│  └─ Return high-velocity trends with scores                 │
│                                                              │
│  Phase 2: Hook Generation                                   │
│  ├─ Generate hooks using emotion + pattern                  │
│  └─ Output Hook with reasoning                              │
│                                                              │
│  Phase 3: Hook Critique                                     │
│  ├─ Score hooks (1-100)                                     │
│  └─ Provide lesson and reasoning                            │
│                                                              │
│  Phase 4: Script Generation                                 │
│  ├─ Expand hook to full script (AIDA/PAS)                   │
│  └─ Adapt for platform (TikTok, YouTube, etc.)              │
│                                                              │
│  Phase 5: Self-Improvement                                  │
│  ├─ Analyze performance data                                │
│  ├─ Update strategy memory                                  │
│  └─ Provide recommendations                                 │
│                                                              │
│  Database: Supabase                                         │
│  ├─ trends, hooks, reflections                              │
│  ├─ strategy_memory, analytics                              │
│  └─ RLS policies for automation                             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 10. Conclusion

The Viral Content Machine V2 has been enhanced with:
- ✅ Fixed schema inconsistencies
- ✅ Implemented self-improvement loop
- ✅ Added script generation capability
- ✅ Created social listening foundation
- ✅ Aligned with V3 roadmap

The system is now ready for the next phase of development, with clear paths for real API integrations, advanced optimization, and multi-modal content generation.
