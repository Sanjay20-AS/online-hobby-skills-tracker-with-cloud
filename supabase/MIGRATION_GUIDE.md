# Migration Application Guide

## Migration: 0001_initial_schema.sql

**Status:** Ready for review and application  
**Tables:** 11  
**RLS Policies:** 20  
**Triggers:** 14 (1 profile creation + 6 timestamps + 5 ownership validation + 3 business logic + 1 comment UPDATE)

### What This Migration Creates

#### Tables
1. **profiles** — Extended user data with public/private visibility enum
2. **hobbies** — User hobby collections
3. **skills** — User skill tracking with proficiency levels and optional hobby association
4. **goals** — Learning goals with target hours and status tracking
5. **practice_sessions** — Practice activity logs (hobby + optional skill)
6. **milestones** — Progress milestones within goals
7. **uploads** — File upload metadata with optional hobby association (storage in Supabase Storage)
8. **posts** — Community posts with public/private visibility enum
9. **likes** — Post interactions (duplicate-free, self-like prevention via trigger)
10. **comments** — Post comments with visibility respect via trigger
11. **follows** — User follow relationships (self-follow prevention)

#### Security
- **Row Level Security (RLS):** Enabled on all application tables
- **RLS Policies:** 20 least-privilege policies for user isolation
- **Data Integrity Triggers:** 3 triggers enforce business logic (self-like prevention, unauthorized comment/like prevention)
- **Triggers:**
  - Auto-create profile on auth.users signup (with collision handling)
  - Auto-update `updated_at` timestamp on table modifications
  - Prevent self-likes, prevent unauthorized comments, prevent unauthorized likes

#### Data Integrity
- UUID primary keys throughout
- Foreign key constraints with appropriate ON DELETE actions
- UNIQUE constraints on duplicate-prevention columns
- CHECK constraints for valid states (positive durations, non-empty content, enum values)
- RLS policies and database triggers enforce ownership and visibility constraints
- No invalid CHECK constraints with subqueries

---

## Applying the Migration

### Prerequisites
- Supabase project `online-hobby-skills-tracker` created
- Supabase credentials in `backend/.env` or available via environment

### Option 1: Supabase Dashboard (Recommended for first-time setup)

1. Log in to [Supabase Dashboard](https://app.supabase.com)
2. Select project `online-hobby-skills-tracker`
3. Navigate to **SQL Editor**
4. Click **New Query** → **New blank query**
5. Copy entire contents of `0001_initial_schema.sql`
6. Paste into editor
7. Click **Run** (or Ctrl+Enter)
8. Verify success — should see "Query success" and table count

**Expected output:** 11 tables created, 100+ objects total (including indexes, policies, triggers)

### Option 2: Supabase CLI

```bash
# Install (if not already installed)
# Windows: winget install Supabase.CLI
# macOS: brew install supabase/tap/supabase
# Linux: curl https://github.com/supabase/cli/releases/latest

# Navigate to project root
cd online-hobby-skills-tracker

# Apply migration
supabase migration up
```

---

## Verification After Application

### Via SQL Editor (Supabase Dashboard)

```sql
-- 1. Verify all tables exist
SELECT COUNT(*) as table_count FROM information_schema.tables 
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
-- Expected: 11

-- 2. Verify RLS enabled
SELECT tablename, rowsecurity FROM pg_tables 
WHERE schemaname = 'public' ORDER BY tablename;
-- Expected: All 11 tables should have rowsecurity = true

-- 3. Verify indexes
SELECT COUNT(*) as index_count FROM pg_indexes 
WHERE schemaname = 'public';
-- Expected: 20+

-- 4. Verify policies
SELECT COUNT(*) as policy_count FROM pg_policies 
WHERE schemaname = 'public';
-- Expected: 20

-- 5. Verify data integrity triggers
SELECT trigger_name FROM information_schema.triggers 
WHERE trigger_schema = 'public' 
AND trigger_name IN ('trigger_prevent_self_like', 'trigger_prevent_unauthorized_comment', 'trigger_prevent_unauthorized_like')
ORDER BY trigger_name;
-- Expected: 3 triggers

-- 6. Test ownership constraint (should fail)
INSERT INTO hobbies (user_id, name) 
VALUES ('00000000-0000-0000-0000-000000000000', 'Test');
-- Expected error: foreign key violation

-- 7. Test self-like prevention (after creating test users and posts)
-- INSERT INTO likes (user_id, post_id) 
-- VALUES (user_id_of_post_author, post_id_owned_by_same_user);
-- Expected error: "Users cannot like their own posts"

-- 8. Test RLS (requires auth context in Dashboard)
-- After creating test users via Auth > Users, verify they cannot see each other's data
```

---

## Schema Changes (Phase 4 Corrections)

### Removed
- Invalid CHECK constraints with subqueries (subqueries cannot be used in CHECK constraints)
  - `goals.goal_hobby_ownership` — now enforced via RLS
  - `practice_sessions.practice_hobby_ownership` — now enforced via RLS
  - `practice_sessions.practice_skill_ownership` — now enforced via RLS
  - `milestones.milestone_goal_ownership` — now enforced via RLS
  - `posts.post_hobby_ownership` — now enforced via RLS
  - `likes.like_not_self` — now enforced via trigger
  - `likes.like_respects_visibility` — now enforced via trigger
  - `comments.comment_respects_visibility` — now enforced via trigger
- Boolean `is_public` field on profiles and posts (replaced with TEXT enum)

### Added
- **profiles.visibility** — TEXT enum ('public'/'private') replaces `is_public` BOOLEAN
- **posts.visibility** — TEXT enum ('public'/'private') replaces `is_public` BOOLEAN
- **skills.hobby_id** — Optional FK to hobbies for skill-hobby association
- **uploads.hobby_id** — Optional FK to hobbies for upload-hobby association
- **uploads.original_filename** — Renamed from `filename` for clarity
- **goals.target_hours** — INTEGER for measurable goal planning
- **goals.status** — TEXT enum ('pending'/'in_progress'/'completed'/'cancelled') replaces `is_completed` BOOLEAN

### Added Data Integrity Triggers
- **prevent_self_like()** — Blocks users from liking their own posts
- **prevent_unauthorized_comment()** — Blocks comments on private posts by non-owners
- **prevent_unauthorized_like()** — Blocks likes on private posts by non-owners

### Improved Auth Profile Creation
- **Username Collision Handling:** Counter-based suffix (1-100) with UUID fallback
- **Username Validation:** Alphanumeric + underscore, 3-30 characters
- **Exception Handling:** Profile creation fails silently (warning logged); signup continues
- **Search Path Hardening:** `SECURITY DEFINER SET search_path = public, auth`

### Updated RLS Policies
All visibility checks updated from boolean to enum:
- `is_public = TRUE` → `visibility = 'public'`
- `is_public = FALSE` → `visibility = 'private'`

---

## Remote Safety Checklist

✅ **This migration:**
- Creates new tables only (no modifications to existing data)
- Enables security features (RLS, constraints)
- Does NOT modify existing tables
- Does NOT delete any data
- Is reversible (each table can be dropped individually)
- **Removes invalid PostgreSQL syntax** (invalid CHECK constraints)
- **Adds proper data integrity mechanisms** (triggers and RLS policies)

✅ **Applied to:** `online-hobby-skills-tracker` Supabase project  
✅ **Impact:** Read-only until application code uses these tables  
✅ **Data retention:** All data persists; no truncation or cleanup  

---

## Troubleshooting

| Error | Cause | Solution |
|---|---|---|
| "uuid-ossp already exists" | Extension already installed | Ignore; migration handles with IF NOT EXISTS |
| "Relation X already exists" | Table already created | Drop existing tables first (data loss!) or use clean database |
| "Policy already exists" | RLS policy already defined | Drop or recreate; check for name conflicts |
| "Foreign key violation" | Referenced record doesn't exist | Ensure parent records exist before inserting child records |
| "Trigger not created" | Function already exists | Check trigger name uniqueness |
| "Users cannot like their own posts" | Self-like attempt | Expected behavior; blocked by trigger |
| "Cannot comment on private posts" | Unauthorized comment attempt | Expected behavior; blocked by trigger |
| "Cannot like private posts" | Unauthorized like attempt | Expected behavior; blocked by trigger |

---

## Rollback (Destructive - Use With Caution)

If the migration must be reverted:

```sql
-- Drop all tables (WARNING: DELETES ALL DATA)
DROP TABLE IF EXISTS follows CASCADE;
DROP TABLE IF EXISTS comments CASCADE;
DROP TABLE IF EXISTS likes CASCADE;
DROP TABLE IF EXISTS posts CASCADE;
DROP TABLE IF EXISTS uploads CASCADE;
DROP TABLE IF EXISTS milestones CASCADE;
DROP TABLE IF EXISTS practice_sessions CASCADE;
DROP TABLE IF EXISTS goals CASCADE;
DROP TABLE IF EXISTS skills CASCADE;
DROP TABLE IF EXISTS hobbies CASCADE;
DROP TABLE IF EXISTS profiles CASCADE;

-- Drop functions
DROP FUNCTION IF EXISTS create_profile_on_signup CASCADE;
DROP FUNCTION IF EXISTS update_timestamp CASCADE;
DROP FUNCTION IF EXISTS prevent_self_like CASCADE;
DROP FUNCTION IF EXISTS prevent_unauthorized_comment CASCADE;
DROP FUNCTION IF EXISTS prevent_unauthorized_like CASCADE;

-- Drop extension (if no other tables use it)
DROP EXTENSION IF EXISTS "uuid-ossp";
```

---

## Next Steps

After migration is applied:
- Backend can initialize SQLAlchemy ORM models
- FastAPI endpoints can reference tables
- Frontend authentication can rely on profiles auto-creation
- Application features can begin implementation
- Verify data integrity triggers are working correctly with test inserts
