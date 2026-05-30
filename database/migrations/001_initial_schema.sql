create extension if not exists "pgcrypto";

create table if not exists public.users (
  id uuid primary key references auth.users(id) on delete cascade,
  email text not null,
  display_name text,
  role text not null default 'reader' check (role in ('reader', 'admin')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.articles (
  id uuid primary key default gen_random_uuid(),
  external_id text unique,
  source_name text not null,
  author text,
  title text not null,
  description text,
  content text,
  url text not null unique,
  image_url text,
  category text not null default 'general',
  country text not null default 'us',
  published_at timestamptz not null,
  cached_at timestamptz not null default now(),
  created_at timestamptz not null default now()
);

create table if not exists public.glosses (
  id uuid primary key default gen_random_uuid(),
  article_id uuid not null references public.articles(id) on delete cascade,
  summary text not null,
  simple_english text not null,
  asl_gloss text not null,
  model_name text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(article_id)
);

create table if not exists public.sign_dictionary (
  id uuid primary key default gen_random_uuid(),
  gloss text not null unique,
  video_url text not null,
  thumbnail_url text,
  created_by uuid references public.users(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.watch_history (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.users(id) on delete cascade,
  article_id uuid not null references public.articles(id) on delete cascade,
  completed boolean not null default false,
  duration_seconds integer not null default 0,
  watched_at timestamptz not null default now()
);

create table if not exists public.saved_articles (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.users(id) on delete cascade,
  article_id uuid not null references public.articles(id) on delete cascade,
  bookmarked boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(user_id, article_id)
);

create table if not exists public.user_preferences (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null unique references public.users(id) on delete cascade,
  favorite_categories text not null default '[]',
  preferred_language text not null default 'en',
  captions_enabled boolean not null default true,
  playback_speed text not null default '1',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.search_events (
  id uuid primary key default gen_random_uuid(),
  query text not null,
  user_id uuid references public.users(id) on delete set null,
  created_at timestamptz not null default now()
);

create table if not exists public.feedback (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references public.users(id) on delete set null,
  article_id uuid references public.articles(id) on delete set null,
  feedback_type text not null,
  message text not null,
  status text not null default 'open',
  created_at timestamptz not null default now()
);

create table if not exists public.translation_ratings (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references public.users(id) on delete set null,
  article_id uuid references public.articles(id) on delete set null,
  translation_quality integer not null check (translation_quality between 1 and 5),
  video_quality integer not null check (video_quality between 1 and 5),
  comment text,
  created_at timestamptz not null default now()
);

create table if not exists public.bug_reports (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references public.users(id) on delete set null,
  article_id uuid references public.articles(id) on delete set null,
  category text not null,
  description text not null,
  status text not null default 'open',
  created_at timestamptz not null default now()
);

create table if not exists public.sign_sequence_jobs (
  id uuid primary key default gen_random_uuid(),
  sequence_hash text not null unique,
  gloss_tokens text not null,
  status text not null default 'queued',
  progress integer not null default 0,
  output_url text,
  error_message text,
  attempts integer not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  completed_at timestamptz
);

create index if not exists sign_sequence_jobs_sequence_hash_idx
  on public.sign_sequence_jobs(sequence_hash);

create index if not exists articles_category_published_idx
  on public.articles(category, published_at desc);

create index if not exists watch_history_user_watched_idx
  on public.watch_history(user_id, watched_at desc);

create index if not exists saved_articles_user_created_idx
  on public.saved_articles(user_id, created_at desc);

create index if not exists search_events_query_created_idx
  on public.search_events(query, created_at desc);

alter table public.users enable row level security;
alter table public.articles enable row level security;
alter table public.glosses enable row level security;
alter table public.sign_dictionary enable row level security;
alter table public.watch_history enable row level security;
alter table public.saved_articles enable row level security;
alter table public.user_preferences enable row level security;
alter table public.search_events enable row level security;
alter table public.feedback enable row level security;
alter table public.translation_ratings enable row level security;
alter table public.bug_reports enable row level security;
alter table public.sign_sequence_jobs enable row level security;

create policy "users can read self" on public.users
  for select using (auth.uid() = id);

create policy "users can update self" on public.users
  for update using (auth.uid() = id);

create policy "articles are readable" on public.articles
  for select using (true);

create policy "glosses are readable" on public.glosses
  for select using (true);

create policy "sign dictionary is readable" on public.sign_dictionary
  for select using (true);

create policy "admins manage sign dictionary" on public.sign_dictionary
  for all using (
    exists (
      select 1 from public.users
      where users.id = auth.uid()
      and users.role = 'admin'
    )
  );

create policy "users manage own watch history" on public.watch_history
  for all using (auth.uid() = user_id);

create policy "users manage own saved articles" on public.saved_articles
  for all using (auth.uid() = user_id);

create policy "users manage own preferences" on public.user_preferences
  for all using (auth.uid() = user_id);

create policy "users manage own feedback" on public.feedback
  for all using (auth.uid() = user_id);

create policy "users manage own ratings" on public.translation_ratings
  for all using (auth.uid() = user_id);

create policy "users manage own bug reports" on public.bug_reports
  for all using (auth.uid() = user_id);

create policy "search events insertable" on public.search_events
  for insert with check (true);

create policy "sequence jobs are readable" on public.sign_sequence_jobs
  for select using (true);

create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.users (id, email, display_name)
  values (new.id, new.email, new.raw_user_meta_data->>'display_name')
  on conflict (id) do nothing;
  return new;
end;
$$ language plpgsql security definer;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();
