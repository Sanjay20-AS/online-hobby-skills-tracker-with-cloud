# Phase 4 Post-Migration Test Plan

**Date:** November 24, 2026  
**Status:** Ready for Behavioral Testing  
**Safety Level:** Synthetic accounts only; no production data modification

---

## Executive Summary

This document provides exact procedures to verify Phase 4 database implementation in production Supabase. All tests use synthetic test accounts and are non-destructive.

---

## Pre-Test Checklist

Before executing any tests:

- [ ] You have Supabase project admin credentials
- [ ] You can access Supabase Auth settings
- [ ] You can access Supabase SQL Editor
- [ ] You understand the test accounts will be temporary (can be deleted after testing)
- [ ] You have read this entire plan

---

## Test Accounts to Create

Create these synthetic accounts in Supabase Auth for testing. After testing, these accounts and their profiles can be deleted.

| Account ID | Email | Password | Purpose | Notes |
|---|---|---|---|---|
| USER_A | test.user.a@example.com | TestPass123! | Profile creation, ownership | Will verify auto-profile creation |
| USER_B | test.user.b@example.com | TestPass123! | RLS isolation, unauthorized access | Will verify RLS policies |
| USER_C | test.user.c@example.com | TestPass123! | Comment ownership test | Will verify comment security |

**Safety Note:** Use distinct test emails to avoid collisions. After testing, delete these accounts from Supabase Auth console; cascading DELETE will remove their profiles.

---

## Test 1: Automatic Profile Creation After Signup

**Purpose:** Verify profile is automatically created when user signs up

**Precondition:** None (new user)

**Steps:**

1. In Supabase Auth console, create new user: `test.user.a@example.com` with password `TestPass123!`
2. Wait 1-2 seconds for trigger to execute
3. Run SQL query:

```sql
-- Query deployed profiles table
SELECT id, username, visibility, created_at 
FROM public.profiles 
WHERE id = (SELECT user_id FROM auth.users WHERE email = 'test.user.a@example.com' LIMIT 1);
```

**Expected Result:**
- One row returned
- `username` is populated (auto-generated from email prefix: `test` or similar)
- `visibility` is `'private'`
- `created_at` is recent (within 2 seconds of account creation)

**Verification Code:**
```sql
SELECT 
    CASE 
        WHEN COUNT(*) = 1 THEN '✅ PASS: Profile auto-created'
        WHEN COUNT(*) = 0 THEN '❌ FAIL: No profile found'
        ELSE '❌ FAIL: Multiple profiles found (data corruption)'
    END as result
FROM public.profiles 
WHERE id = (SELECT id FROM auth.users WHERE email = 'test.user.a@example.com' LIMIT 1);
```

---

## Test 2: Username Uniqueness (UNIQUE Constraint)

**Purpose:** Verify UNIQUE constraint on username prevents duplicates

**Precondition:** USER_A profile exists (from Test 1)

**Steps:**

1. Get USER_A's generated username:

```sql
SELECT username FROM public.profiles 
WHERE id = (SELECT id FROM auth.users WHERE email = 'test.user.a@example.com' LIMIT 1);
```

2. Note the username (e.g., `test` or `test_user_a`)
3. Create USER_B account: `test.user.b@example.com`
4. Wait 1-2 seconds
5. Query USER_B's profile:

```sql
SELECT username FROM public.profiles 
WHERE id = (SELECT id FROM auth.users WHERE email = 'test.user.b@example.com' LIMIT 1);
```

**Expected Result:**
- USER_B's username is different from USER_A's
- If collision occurs, USER_B gets numeric suffix (e.g., `test1`, `test2`) or UUID fallback
- No constraint violation error in auth logs

**Verification Code:**
```sql
WITH user_a AS (
    SELECT username as a_username FROM public.profiles 
    WHERE id = (SELECT id FROM auth.users WHERE email = 'test.user.a@example.com' LIMIT 1)
),
user_b AS (
    SELECT username as b_username FROM public.profiles 
    WHERE id = (SELECT id FROM auth.users WHERE email = 'test.user.b@example.com' LIMIT 1)
)
SELECT 
    CASE 
        WHEN a_username != b_username THEN '✅ PASS: Usernames are unique'
        ELSE '❌ FAIL: Usernames are identical (constraint violated)'
    END as result
FROM user_a, user_b;
```

---

## Test 3: Cross-User Ownership Rejection

**Purpose:** Verify ownership triggers prevent cross-user record access

**Precondition:** USER_A and USER_B profiles exist

**Setup:**

1. Create a hobby as USER_A:

```bash
# Via backend API or direct DB insert (if you have direct access)
# Insert as USER_A (not recommended in production—for testing only)

INSERT INTO public.hobbies (id, user_id, name, description, category)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM auth.users WHERE email = 'test.user.a@example.com' LIMIT 1),
    'Photography',
    'Digital photography hobby',
    'art'
);
```

2. Query the hobby ID:

```sql
SELECT id FROM public.hobbies 
WHERE user_id = (SELECT id FROM auth.users WHERE email = 'test.user.a@example.com' LIMIT 1) 
LIMIT 1;
```

**Test: Attempt to Create Skill as USER_B Under USER_A's Hobby**

This requires the backend API or direct trigger test. For now, conceptual test:

```sql
-- ⚠️ THIS WILL FAIL (by design—ownership trigger prevents it)
-- Do NOT run this in production; it's shown for reference only

-- Simulated attempt: User B creates skill under User A's hobby
INSERT INTO public.skills (id, user_id, hobby_id, name, proficiency_level)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM auth.users WHERE email = 'test.user.b@example.com' LIMIT 1),  -- User B
    (SELECT id FROM public.hobbies WHERE user_id = (SELECT id FROM auth.users WHERE email = 'test.user.a@example.com' LIMIT 1) LIMIT 1),  -- User A's hobby
    'Canon EOS Proficiency',
    'intermediate'
);

-- Expected: ERROR — Ownership trigger prevents this
-- Error message: "Users can only create skills for their own hobbies"
```

**Expected Result:**
- Insert fails with ownership validation error
- Error message indicates cross-user validation
- No data is inserted

**Verification via Backend (Recommended):**

If you have the backend running, test via API:

```bash
# 1. Get USER_B auth token (login as USER_B)
# 2. Create hobby as USER_A (or use existing hobby)
# 3. Attempt to create skill as USER_B under USER_A's hobby

POST /api/v1/skills
Headers:
  Authorization: Bearer <USER_B_TOKEN>
Body:
{
  "hobby_id": "<USER_A_HOBBY_ID>",
  "name": "Test Skill",
  "proficiency_level": "beginner"
}

# Expected: 403 Forbidden or error
```

---

## Test 4: Unauthorized Private-Post Comment Operations

**Purpose:** Verify comment INSERT and UPDATE protection on private posts

**Precondition:** USER_A and USER_B profiles exist

**Setup:**

1. Create a private post as USER_A (via API or direct insert):

```sql
INSERT INTO public.posts (id, user_id, hobby_id, title, content, visibility)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM auth.users WHERE email = 'test.user.a@example.com' LIMIT 1),
    (SELECT id FROM public.hobbies WHERE user_id = (SELECT id FROM auth.users WHERE email = 'test.user.a@example.com' LIMIT 1) LIMIT 1),
    'Private Photography Thoughts',
    'My private thoughts about photography',
    'private'
);
```

2. Query the post ID:

```sql
SELECT id FROM public.posts 
WHERE user_id = (SELECT id FROM auth.users WHERE email = 'test.user.a@example.com' LIMIT 1)
    AND visibility = 'private'
LIMIT 1;
```

**Test A: Attempt INSERT Comment as USER_B on USER_A's Private Post**

```sql
-- ⚠️ THIS WILL FAIL (by design)
INSERT INTO public.comments (id, user_id, post_id, content)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM auth.users WHERE email = 'test.user.b@example.com' LIMIT 1),  -- User B
    (SELECT id FROM public.posts WHERE user_id = (SELECT id FROM auth.users WHERE email = 'test.user.a@example.com' LIMIT 1) AND visibility = 'private' LIMIT 1),
    'Nice post!'
);

-- Expected: ERROR — prevent_unauthorized_comment trigger blocks this
-- Error message: "Cannot comment on private posts of other users"
```

**Expected Result:**
- Insert fails with authorization error
- Error message: "Cannot comment on private posts of other users"
- No comment is created

**Test B: Verify USER_A Can Comment on Own Private Post**

```sql
-- ✅ THIS SHOULD SUCCEED
INSERT INTO public.comments (id, user_id, post_id, content)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM auth.users WHERE email = 'test.user.a@example.com' LIMIT 1),  -- User A (owner)
    (SELECT id FROM public.posts WHERE user_id = (SELECT id FROM auth.users WHERE email = 'test.user.a@example.com' LIMIT 1) AND visibility = 'private' LIMIT 1),
    'My thoughts on this'
);

-- Expected: Success — comment created
```

**Test C: UPDATE Comment Path on Private Post (Decision 2 Verification)**

```sql
-- Get a comment created by User A on their private post
SELECT id FROM public.comments 
WHERE user_id = (SELECT id FROM auth.users WHERE email = 'test.user.a@example.com' LIMIT 1)
LIMIT 1;

-- ⚠️ THIS WILL FAIL (by design—prevent_unauthorized_comment_update trigger)
-- Simulate User B attempting to modify the comment
UPDATE public.comments
SET content = 'Modified by User B'
WHERE id = <COMMENT_ID>;

-- Expected: ERROR — UPDATE trigger prevents this
```

**Expected Result:**
- UPDATE fails with authorization error
- Comment retains original content
- Error message indicates unauthorized update

---

## Test 5: RLS Isolation Between Two Dummy Users

**Purpose:** Verify RLS policies enforce read isolation between users

**Precondition:** USER_A and USER_B profiles exist with different visibility settings

**Setup:**

1. Create USER_A hobby (private visibility):

```sql
INSERT INTO public.hobbies (id, user_id, name, description, visibility)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM auth.users WHERE email = 'test.user.a@example.com' LIMIT 1),
    'Secret Photography',
    'Private hobby',
    'private'
);
```

2. Create USER_B hobby (public visibility):

```sql
INSERT INTO public.hobbies (id, user_id, name, description, visibility)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM auth.users WHERE email = 'test.user.b@example.com' LIMIT 1),
    'Public Photography',
    'Public hobby',
    'public'
);
```

**Test A: USER_B Querying Hobbies (Via Backend API with USER_B Token)**

This requires the backend API. The API should enforce RLS:

```bash
# As USER_B, query all hobbies
GET /api/v1/hobbies
Headers:
  Authorization: Bearer <USER_B_TOKEN>

# Expected Result:
# - USER_B sees only their own hobbies (private + public)
# - USER_B does NOT see USER_A's private hobbies
# - If USER_A's hobby has visibility='public', USER_B may see it (depends on schema)
```

**Test B: Direct SQL RLS Test (Requires Supabase CLI or JWT)**

If you have Supabase CLI set up, test with JWT:

```bash
# 1. Get USER_B's JWT token (login result)
# 2. Query hobbies with USER_B's JWT

psql postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres \
  -c "SET request.jwt.claims = '{\"sub\":\"<USER_B_ID>\"}'; SELECT id, name, user_id FROM public.hobbies;"

# Expected: Only USER_B's hobbies visible (or public hobbies if visibility='public')
```

**Expected Result:**
- RLS policy filters results based on user_id and visibility
- USER_B cannot see USER_A's private data
- USER_B can see USER_A's public data (if schema allows)

---

## Test 6: Verify Ownership Trigger on Practice_Sessions

**Purpose:** Verify ownership trigger prevents cross-user practice session creation

**Precondition:** USER_A and USER_B have hobbies and skills

**Setup:**

1. Create USER_A skill:

```sql
INSERT INTO public.skills (id, user_id, hobby_id, name, proficiency_level)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM auth.users WHERE email = 'test.user.a@example.com' LIMIT 1),
    (SELECT id FROM public.hobbies WHERE user_id = (SELECT id FROM auth.users WHERE email = 'test.user.a@example.com' LIMIT 1) LIMIT 1),
    'Photography Basics',
    'beginner'
);
```

**Test: Attempt Cross-User Practice Session**

```sql
-- ⚠️ THIS WILL FAIL (by design—ownership trigger)
INSERT INTO public.practice_sessions (id, user_id, skill_id, duration_minutes, notes)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM auth.users WHERE email = 'test.user.b@example.com' LIMIT 1),  -- User B
    (SELECT id FROM public.skills WHERE user_id = (SELECT id FROM auth.users WHERE email = 'test.user.a@example.com' LIMIT 1) LIMIT 1),  -- User A's skill
    30,
    'Practice session'
);

-- Expected: ERROR — validate_practice_sessions_ownership trigger blocks this
-- Error message: "Users can only create practice sessions for their own skills"
```

**Expected Result:**
- Insert fails with ownership error
- Error message indicates ownership violation
- No practice session is created

---

## Test 7: Profile Creation Error Handling

**Purpose:** Verify profile creation errors propagate (Decision 4)

**Precondition:** None (conceptual test)

**How to Test:**

This requires triggering an error in `create_profile_on_signup`. Conceptually:

1. If the trigger encounters an error (e.g., disk full, permission denied), it should:
   - Log a WARNING with user ID and error message
   - Re-raise the exception
   - Abort the signup transaction

2. To verify, create a user and check Supabase logs:

```sql
-- Check PostgreSQL logs for profile creation warnings
SELECT * FROM pg_read_file('postgresql.log', 0, 1000);

-- Or, in Supabase console:
-- Navigate to: Database Logs → PostgreSQL Logs
-- Search for: "Profile creation error"
```

**Expected Result:**
- If errors occur, they are logged with user ID
- Signup transaction is rolled back
- User account is not created

---

## Verification Summary Table

| Test | Component | Status | Evidence |
|---|---|---|---|
| 1 | Auto Profile Creation | To Verify | Profile row exists, username populated |
| 2 | Username Uniqueness | To Verify | Different usernames for different users |
| 3 | Cross-User Ownership | To Verify | Ownership trigger error on cross-user insert |
| 4A | Comment INSERT Security | To Verify | Error on unauthorized comment insert |
| 4B | Comment UPDATE Security | To Verify | Error on unauthorized comment update |
| 5 | RLS Isolation | To Verify | Different data visible to different users |
| 6 | Practice Session Ownership | To Verify | Ownership trigger error on cross-user insert |
| 7 | Error Propagation | To Verify | Logs show profile creation errors |

---

## Cleanup After Testing

Once all tests complete:

1. **Delete test accounts from Supabase Auth console:**
   - Navigate to Auth → Users
   - Select each test user (test.user.a@example.com, etc.)
   - Click Delete

2. **Cascading deletes will remove:**
   - All profiles (via ON DELETE CASCADE)
   - All hobbies, skills, goals, practice_sessions (via ON DELETE CASCADE)
   - All posts, comments, likes (via ON DELETE CASCADE)

3. **Verify cleanup:**

```sql
SELECT COUNT(*) FROM public.profiles;
-- Should match pre-test count
```

---

## Expected Test Results Summary

| Test | Expected Outcome |
|---|---|
| Auto profile creation | ✅ Profile auto-created with valid username |
| Username uniqueness | ✅ Each user has unique username |
| Cross-user ownership | ✅ Ownership trigger blocks cross-user operations |
| Private post comments | ✅ Comments blocked on others' private posts |
| RLS isolation | ✅ Users see only their own or public data |
| Error propagation | ✅ Profile errors abort signup |

If all tests pass: **Phase 4 is verified and production-ready.**

---

## Safety Checklist

- [x] No production user data will be modified
- [x] All tests use synthetic accounts only
- [x] Test accounts can be safely deleted after testing
- [x] No data is left behind (cascading deletes clean up)
- [x] All queries are read-heavy except setup
- [x] All destructive operations are intentional (delete test accounts)

---

## Support

If a test fails:
1. Note the exact error message
2. Cross-reference with Phase 4 migration file
3. Check PostgreSQL logs in Supabase console
4. Refer to `PHASE4_FINAL_AUDIT_REPORT.md` for known limitations

