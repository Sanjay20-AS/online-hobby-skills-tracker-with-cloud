# Database Schema — Online Hobby & Skills Tracker

## Overview

The database uses Supabase PostgreSQL with Row Level Security (RLS) for access control and auth.users references for user identity.

**Key principles:**
- UUID primary keys across all tables
- User ownership enforced via `auth.uid()` in RLS policies
- **Ownership integrity enforced via database triggers** (validate related records belong to same user)
- Timestamps use TIMESTAMPTZ for consistency
- Public/private visibility controlled per post and profile
- Enum fields (TEXT with CHECK constraints) standardize state values
- **Errors during profile creation are raised, not silently ignored**

---

## Tables and Relationships

### 1. **profiles**
Extended user profile information linked to `auth.users`.

| Column | Type | Constraints | Purpose |
|---|---|---|---|
| `id` | UUID | PK → auth.users(id) ON DELETE CASCADE | User reference |
| `username` | TEXT | UNIQUE, NOT NULL | Unique user identifier |
| `display_name` | TEXT | | Public display name |
| `bio` | TEXT | | User biography |
| `avatar_url` | TEXT | | Profile avatar URL |
| `visibility` | TEXT | DEFAULT 'private', CHECK IN ('public', 'private') | Profile discoverability |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | Last update timestamp |

**Indexes:**
- `username` (UNIQUE, LOWER for case-insensitive)
- `visibility`

**RLS:**
- Users manage own profile
- Public profiles visible to authenticated users
- Private profiles visible only to owner

**Triggers:**
- Automatic trigger `create_profile_on_signup` on auth.users INSERT
- `updated_at` auto-updated on profile edits

**Notes:**
- Profile visibility defaults to 'private'; users must opt-in to public discovery
- Username collisions handled via counter-based suffix generation (up to 100 attempts) or UUID fallback
- **Profile creation RAISES exception on error** (not silent)
- Uses `raw_user_meta_data` from Supabase Auth and schema-qualified references

---

### 2. **hobbies**
Hobbies owned by individual users.

| Column | Type | Constraints | Purpose |
|---|---|---|---|
| `id` | UUID | PK DEFAULT uuid_generate_v4() | Hobby ID |
| `user_id` | UUID | FK → auth.users ON DELETE CASCADE | Owner |
| `name` | TEXT | NOT NULL, CHECK len > 0 | Hobby name |
| `description` | TEXT | | Hobby description |
| `category` | TEXT | | Optional category |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | Last update timestamp |

**Indexes:**
- `user_id`
- `created_at` DESC

**RLS:**
- Owners manage own hobbies
- Public users' hobbies visible to authenticated users

**Referenced by:**
- `goals.hobby_id` (via trigger `validate_goal_ownership`)
- `practice_sessions.hobby_id` (via trigger `validate_practice_session_ownership`)
- `posts.hobby_id` (via trigger `validate_post_ownership`)
- `uploads.hobby_id` (via trigger `validate_upload_ownership`)

---

### 3. **skills**
Skills owned by individual users (proficiency tracking).

| Column | Type | Constraints | Purpose |
|---|---|---|---|
| `id` | UUID | PK DEFAULT uuid_generate_v4() | Skill ID |
| `user_id` | UUID | FK → auth.users ON DELETE CASCADE | Owner |
| `hobby_id` | UUID | FK → hobbies ON DELETE SET NULL | Associated hobby (optional) |
| `name` | TEXT | NOT NULL, CHECK len > 0 | Skill name |
| `description` | TEXT | | Skill description |
| `proficiency_level` | TEXT | CHECK IN ('beginner', 'intermediate', 'advanced', 'expert') | Proficiency enum |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | Last update timestamp |

**Indexes:**
- `user_id`
- `proficiency_level`

**RLS:**
- Owners manage own skills
- Public users' skills visible to authenticated users

**Referenced by:**
- `practice_sessions.skill_id` (via trigger `validate_practice_session_ownership`)

---

### 4. **goals**
Learning or achievement goals associated with hobbies.

| Column | Type | Constraints | Purpose |
|---|---|---|---|
| `id` | UUID | PK DEFAULT uuid_generate_v4() | Goal ID |
| `user_id` | UUID | FK → auth.users ON DELETE CASCADE | Owner |
| `hobby_id` | UUID | FK → hobbies ON DELETE SET NULL | Associated hobby |
| `title` | TEXT | NOT NULL, CHECK len > 0 | Goal title |
| `description` | TEXT | | Goal description |
| `target_date` | DATE | | Target completion date |
| `target_hours` | INTEGER | CHECK > 0 or NULL | Target hours to invest (optional) |
| `status` | TEXT | DEFAULT 'pending', CHECK IN ('pending', 'in_progress', 'completed', 'cancelled') | Goal status enum |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | Last update timestamp |

**Indexes:**
- `user_id`
- `hobby_id`
- `status`

**RLS:**
- Owners manage own goals only

**Ownership Validation:**
- Trigger `validate_goal_ownership` ensures goal.hobby_id references hobby owned by goal.user_id

**Referenced by:**
- `milestones.goal_id` (via trigger `validate_milestone_ownership`)

**Notes:**
- `status` replaces the deprecated `is_completed` boolean
- `target_hours` optional field for measurable goal planning

---

### 5. **practice_sessions**
Activity logs tracking practice/progress for hobbies and skills.

| Column | Type | Constraints | Purpose |
|---|---|---|---|
| `id` | UUID | PK DEFAULT uuid_generate_v4() | Session ID |
| `user_id` | UUID | FK → auth.users ON DELETE CASCADE | Session owner |
| `hobby_id` | UUID | FK → hobbies ON DELETE CASCADE | Required hobby |
| `skill_id` | UUID | FK → skills ON DELETE SET NULL | Optional skill |
| `duration_minutes` | INTEGER | NOT NULL, CHECK > 0 | Session duration |
| `notes` | TEXT | | Session notes |
| `session_date` | TIMESTAMPTZ | DEFAULT NOW() | Session timestamp |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Record creation timestamp |

**Indexes:**
- `user_id`
- `hobby_id`
- `skill_id`
- `session_date` DESC

**RLS:**
- Owners manage own sessions only

**Ownership Validation:**
- Trigger `validate_practice_session_ownership` ensures:
  - `practice_sessions.hobby_id` references hobby owned by `practice_sessions.user_id`
  - `practice_sessions.skill_id` references skill owned by `practice_sessions.user_id` (if provided)

---

### 6. **milestones**
Progress milestones within goals.

| Column | Type | Constraints | Purpose |
|---|---|---|---|
| `id` | UUID | PK DEFAULT uuid_generate_v4() | Milestone ID |
| `user_id` | UUID | FK → auth.users ON DELETE CASCADE | Milestone owner |
| `goal_id` | UUID | FK → goals ON DELETE CASCADE | Parent goal |
| `title` | TEXT | NOT NULL, CHECK len > 0 | Milestone title |
| `description` | TEXT | | Milestone description |
| `achieved_at` | TIMESTAMPTZ | | Achievement timestamp |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Creation timestamp |

**Indexes:**
- `user_id`
- `goal_id`
- `achieved_at`

**RLS:**
- Owners manage own milestones only

**Ownership Validation:**
- Trigger `validate_milestone_ownership` ensures milestone.goal_id references goal owned by milestone.user_id

---

### 7. **uploads**
File upload metadata (actual files stored in Supabase Storage).

| Column | Type | Constraints | Purpose |
|---|---|---|---|
| `id` | UUID | PK DEFAULT uuid_generate_v4() | Upload record ID |
| `user_id` | UUID | FK → auth.users ON DELETE CASCADE | File owner |
| `hobby_id` | UUID | FK → hobbies ON DELETE SET NULL | Associated hobby (optional) |
| `original_filename` | TEXT | NOT NULL, CHECK len > 0 | Original filename provided by user |
| `storage_path` | TEXT | NOT NULL, CHECK len > 0 | Storage path in Supabase Storage |
| `file_size` | INTEGER | NOT NULL, CHECK > 0 | File size in bytes |
| `mime_type` | TEXT | | File MIME type |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Upload timestamp |

**Indexes:**
- `user_id`
- `created_at` DESC

**RLS:**
- Owners manage own uploads only

**Ownership Validation:**
- Trigger `validate_upload_ownership` ensures upload.hobby_id references hobby owned by upload.user_id (if provided)

**Storage strategy:**
- Files stored in private Supabase Storage bucket under `users/{user_id}/` paths
- Metadata tracked in this table for queries and cleanup

---

### 8. **posts**
Community posts (achievements, hobby updates, etc.) with public/private visibility.

| Column | Type | Constraints | Purpose |
|---|---|---|---|
| `id` | UUID | PK DEFAULT uuid_generate_v4() | Post ID |
| `user_id` | UUID | FK → auth.users ON DELETE CASCADE | Post author |
| `hobby_id` | UUID | FK → hobbies ON DELETE SET NULL | Associated hobby |
| `title` | TEXT | NOT NULL, CHECK len > 0 | Post title |
| `content` | TEXT | NOT NULL, CHECK len > 0 | Post content |
| `visibility` | TEXT | DEFAULT 'public', CHECK IN ('public', 'private') | Post visibility enum |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | Last update timestamp |

**Indexes:**
- `user_id`
- `hobby_id`
- `visibility`
- `created_at` DESC

**RLS:**
- Owners manage own posts
- Owners see own posts (public or private)
- Other users see only public posts

**Ownership Validation:**
- Trigger `validate_post_ownership` ensures post.hobby_id references hobby owned by post.user_id (if provided)

**Referenced by:**
- `likes.post_id`
- `comments.post_id`

**Notes:**
- `visibility` enum: 'public' (all authenticated users), 'private' (owner only)

---

### 9. **likes**
Post interactions (likes) with duplicate prevention and self-like prevention.

| Column | Type | Constraints | Purpose |
|---|---|---|---|
| `id` | UUID | PK DEFAULT uuid_generate_v4() | Like ID |
| `user_id` | UUID | FK → auth.users ON DELETE CASCADE | User who liked |
| `post_id` | UUID | FK → posts ON DELETE CASCADE | Liked post |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Like timestamp |

**Constraints:**
- UNIQUE(user_id, post_id) — prevents duplicate likes

**Indexes:**
- `user_id`
- `post_id`

**RLS:**
- Users create own likes only
- Users see likes on posts they can view

**Data Integrity Triggers:**
- `prevent_self_like`: prevents users from liking their own posts (INSERT)
- `prevent_unauthorized_like`: prevents likes on private posts by unauthorized users (INSERT)

---

### 10. **comments**
Post comments with visibility respect.

| Column | Type | Constraints | Purpose |
|---|---|---|---|
| `id` | UUID | PK DEFAULT uuid_generate_v4() | Comment ID |
| `user_id` | UUID | FK → auth.users ON DELETE CASCADE | Comment author |
| `post_id` | UUID | FK → posts ON DELETE CASCADE | Commented post |
| `content` | TEXT | NOT NULL, CHECK len > 0 | Comment content |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | Last update timestamp |

**Indexes:**
- `user_id`
- `post_id`
- `created_at` DESC

**RLS:**
- Users manage own comments only
- Users see comments on posts they can view

**Data Integrity Triggers:**
- `prevent_unauthorized_comment`: prevents comments on private posts by non-owners (INSERT)
- `validate_comment_visibility_on_update`: prevents comment UPDATE on private posts by non-owners (UPDATE)

---

### 11. **follows**
User follow relationships with duplicate prevention and self-follow prevention.

| Column | Type | Constraints | Purpose |
|---|---|---|---|
| `id` | UUID | PK DEFAULT uuid_generate_v4() | Follow ID |
| `follower_id` | UUID | FK → auth.users ON DELETE CASCADE | User following |
| `following_id` | UUID | FK → auth.users ON DELETE CASCADE | User being followed |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Follow timestamp |

**Constraints:**
- UNIQUE(follower_id, following_id) — prevents duplicate follows
- CHECK — user cannot follow themselves

**Indexes:**
- `follower_id`
- `following_id`

**RLS:**
- Users create follow relationships as followers only
- Authenticated users can see follow relationships

---

## Row Level Security (RLS) Summary

| Table | SELECT | INSERT | UPDATE | DELETE |
|---|---|---|---|---|
| **profiles** | Self \| Public | Self | Self | Self |
| **hobbies** | Owner \| Public users' | Owner | Owner | Owner |
| **skills** | Owner \| Public users' | Owner | Owner | Owner |
| **goals** | Owner | Owner | Owner | Owner |
| **practice_sessions** | Owner | Owner | Owner | Owner |
| **milestones** | Owner | Owner | Owner | Owner |
| **uploads** | Owner | Owner | Owner | Owner |
| **posts** | Owner \| Public | Owner | Owner | Owner |
| **likes** | Public/own posts | Self | — | Self |
| **comments** | Public/own posts | Self | Self | Self |
| **follows** | Authenticated | Self as follower | — | Self |

---

## Data Integrity Triggers (14 total)

### Profile Creation
- `create_profile_on_signup`: Auto-creates profile on auth.users INSERT

### Timestamps (6 triggers)
Auto-update `updated_at` on table modifications:
- `trigger_profiles_updated_at`
- `trigger_hobbies_updated_at`
- `trigger_skills_updated_at`
- `trigger_goals_updated_at`
- `trigger_posts_updated_at`
- `trigger_comments_updated_at`

### Ownership Validation (5 triggers)
Ensure related records belong to same user:
- `validate_practice_session_ownership`: Ensures hobby and skill belong to session user (INSERT/UPDATE)
- `validate_goal_ownership`: Ensures hobby belongs to goal user (INSERT/UPDATE)
- `validate_milestone_ownership`: Ensures goal belongs to milestone user (INSERT/UPDATE)
- `validate_post_ownership`: Ensures hobby belongs to post user (INSERT/UPDATE)
- `validate_upload_ownership`: Ensures hobby belongs to upload user (INSERT/UPDATE)

### Business Logic & Security (3 triggers)
- `prevent_self_like`: Prevents users from liking their own posts (INSERT)
- `prevent_unauthorized_comment`: Prevents comments on private posts by non-owners (INSERT)
- `prevent_unauthorized_like`: Prevents likes on private posts by non-owners (INSERT)

### Comment Visibility (1 trigger)
- `validate_comment_visibility_on_update`: Ensures comment UPDATE respects post visibility (UPDATE)

---

## Authentication Integration

**Supabase Auth Profile Creation:**
- Automatic trigger `create_profile_on_signup` creates profile on `auth.users` INSERT
- **Username Generation:**
  - Primary: username from user metadata
  - Secondary: email prefix
  - Fallback: UUID substring
- **Collision Handling:**
  - Counter-based suffix (1-100)
  - UUID fallback after 100 attempts
- **Username Validation:**
  - Alphanumeric + underscore only
  - 3–30 characters enforced
  - Invalid characters replaced with underscores
- **Initial Visibility:** Profile defaults to 'private'
- **Error Handling:** Exception is RAISED on error (not silently ignored)
- **Security:** `SECURITY DEFINER SET search_path = 'public'` with schema-qualified references

---

## Migration Instructions

### Prerequisites
- Supabase project `online-hobby-skills-tracker` created
- Supabase credentials available

### Apply Migration

**Via Supabase Dashboard SQL Editor:**
1. Copy contents of `0001_initial_schema.sql`
2. Paste into new query
3. Execute

**Via Supabase CLI:**
```bash
supabase migration up
```

### Verification
```sql
-- Check tables
SELECT COUNT(*) FROM information_schema.tables 
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
-- Expected: 11

-- Check RLS enabled
SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public' AND rowsecurity;
-- Expected: 11

-- Check ownership triggers
SELECT COUNT(*) FROM information_schema.triggers 
WHERE trigger_schema = 'public' AND trigger_name LIKE 'trigger_validate_%';
-- Expected: 5

-- Test ownership validation (should raise error):
-- INSERT INTO goals (id, user_id, hobby_id, title)
-- VALUES (uuid_generate_v4(), user_a_id, hobby_owned_by_user_b, 'Test');
```

---

## Security Summary

### Three-Layer Protection
1. **Structural Constraints** — CHECK constraints for enums, positive integers, non-empty strings
2. **Access Control** — 20 RLS policies enforce user isolation
3. **Business Logic** — 14 database triggers for profile creation, timestamps, ownership, and security

### Ownership Integrity
All cross-user record references validated by triggers on INSERT and UPDATE. This approach is necessary because PostgreSQL does not support self-referential subqueries in CHECK constraints.

### Community Security
- **Private posts**: Owner only (RLS + triggers)
- **Public profiles/hobbies/skills**: Authenticated users only
- **Follow relationships**: Authenticated users only
- **Comments/likes on private posts**: Owner only (triggers on INSERT and UPDATE)

---

## Status: Ready for Review and Application

✅ Schema designed with comprehensive ownership validation  
✅ All ownership constraints enforced via triggers (not invalid CHECK constraints)  
✅ Comment UPDATE path secured  
✅ Follow visibility restricted to authenticated users  
✅ Auth profile creation hardened  
✅ Ready for review and application to Supabase
