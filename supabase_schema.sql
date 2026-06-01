-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- 1. trends (Retain existing and expand)
create table if not exists public.trends (
    id uuid default uuid_generate_v4() primary key,
    trend_title text not null,
    trend_summary text,
    source text,
    source_url text,
    niche text,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 2. hooks (The Execution)
create table if not exists public.hooks (
    id uuid default uuid_generate_v4() primary key,
    trend_id uuid references public.trends(id) on delete cascade,
    hook_text text not null,
    emotion text, -- e.g., fear, sarcasm
    pattern text, -- e.g., hard_truth
    viral_score integer check (viral_score >= 1 and viral_score <= 100),
    reasoning text, -- Agent's chain of thought
    model_used text,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 3. reflections (The Self-Improvement)
create table if not exists public.reflections (
    id uuid default uuid_generate_v4() primary key,
    hook_id uuid references public.hooks(id) on delete cascade,
    performance_score integer check (performance_score >= 1 and performance_score <= 100),
    lesson text, -- What worked/failed
    reasoning_update text,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 4. strategy_memory (The Brain)
create table if not exists public.strategy_memory (
    id uuid default uuid_generate_v4() primary key,
    niche text,
    dominant_emotion text,
    recommended_pattern text,
    confidence integer check (confidence >= 1 and confidence <= 100),
    reasoning text,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 5. analytics (The Feedback)
create table if not exists public.analytics (
    id uuid default uuid_generate_v4() primary key,
    hook_id uuid references public.hooks(id) on delete cascade,
    views integer default 0,
    likes integer default 0,
    shares integer default 0,
    comments integer default 0,
    engagement_rate numeric,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- RLS Policies (Basic for automation)
alter table public.trends enable row level security;
alter table public.hooks enable row level security;
alter table public.reflections enable row level security;
alter table public.strategy_memory enable row level security;
alter table public.analytics enable row level security;

create policy "Allow all access for trends" on public.trends for all using (true) with check (true);
create policy "Allow all access for hooks" on public.hooks for all using (true) with check (true);
create policy "Allow all access for reflections" on public.reflections for all using (true) with check (true);
create policy "Allow all access for strategy_memory" on public.strategy_memory for all using (true) with check (true);
create policy "Allow all access for analytics" on public.analytics for all using (true) with check (true);
