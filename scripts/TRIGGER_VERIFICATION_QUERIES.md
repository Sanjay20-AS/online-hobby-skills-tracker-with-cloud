# Phase 4 Trigger Verification Queries

**Purpose:** Read-only SQL queries to verify all Phase 4 triggers are deployed correctly  
**Safety:** All queries are SELECT only - no data modification  
**Location:** Run in Supabase SQL Editor

---

## Quick Summary Query

**Run this to get a one-line summary:**

```sql
SELECT COUNT(*) as total_triggers FROM pg_trigger t
JOIN pg_class r ON t.tgrelid = r.oid
JOIN pg_proc p ON t.tgfoid = p.oid
WHERE p.proname NOT LIKE 'RI_%'
AND (r.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
     OR r.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'auth'));

-- Expected result: 15 (or 16 including profile creation on auth.users)
```

---

## Complete Trigger Inventory (Authoritative)

**Run this to get full definitions with `pg_get_triggerdef()`:**

```sql
SELECT 
    t.tgname as trigger_name,
    r.relname as table_name,
    n.nspname as schema_name,
    pg_get_triggerdef(t.oid) as trigger_definition
FROM pg_trigger t
JOIN pg_class r ON t.tgrelid = r.oid
JOIN pg_namespace n ON r.relnamespace = n.oid
JOIN pg_proc p ON t.tgfoid = p.oid
WHERE p.proname NOT LIKE 'RI_%'
ORDER BY n.nspname, r.relname, t.tgname;
```

**Expected Results:** 15 rows showing full trigger CREATE statements

---

## Specific Trigger Verification Queries

### 1. Comment UPDATE Security Trigger

**Purpose:** Verify the comment UPDATE protection trigger is correctly registered

```sql
SELECT 
    t.tgname,
    r.relname as table_name,
    pg_get_triggerdef(t.oid) as definition
FROM pg_trigger t
JOIN pg_class r ON t.tgrelid = r.oid
WHERE t.tgname = 'trigger_validate_comment_visibility_on_update';
```

**Expected Result:**
```
trigger_name: trigger_validate_comment_visibility_on_update
table_name: comments
definition: CREATE TRIGGER trigger_validate_comment_visibility_on_update BEFORE UPDATE ON public.comments FOR EACH ROW EXECUTE FUNCTION validate_comment_visibility_on_update()
```

**What This Verifies:**
- ✅ Trigger exists
- ✅ Registered on comments table
- ✅ Event is BEFORE UPDATE (not DELETE)
- ✅ Calls correct function

---

### 2. Ownership Triggers (All 5)

**Purpose:** Verify all ownership validation triggers are present and correct

```sql
SELECT 
    t.tgname,
    r.relname as table_name,
    pg_get_triggerdef(t.oid) as definition
FROM pg_trigger t
JOIN pg_class r ON t.tgrelid = r.oid
JOIN pg_proc p ON t.tgfoid = p.oid
WHERE p.proname LIKE 'validate_%_ownership'
ORDER BY r.relname;
```

**Expected Results:** 5 rows
- trigger_validate_goal_ownership
- trigger_validate_milestone_ownership
- trigger_validate_post_ownership
- trigger_validate_practice_session_ownership
- trigger_validate_upload_ownership

**What This Verifies:**
- ✅ All 5 ownership triggers exist
- ✅ Each registered for BEFORE INSERT OR UPDATE
- ✅ Each calls the correct validation function

---

### 3. Comment Security Triggers (Both INSERT and UPDATE)

**Purpose:** Verify both comment INSERT and UPDATE protection

```sql
SELECT 
    t.tgname,
    r.relname as table_name,
    pg_get_triggerdef(t.oid) as definition
FROM pg_trigger t
JOIN pg_class r ON t.tgrelid = r.oid
WHERE r.relname = 'comments'
AND t.tgname LIKE 'trigger_prevent%' OR t.tgname LIKE 'trigger_validate_comment%'
ORDER BY t.tgname;
```

**Expected Results:** 2 rows
- trigger_prevent_unauthorized_comment (BEFORE INSERT)
- trigger_validate_comment_visibility_on_update (BEFORE UPDATE)

**What This Verifies:**
- ✅ Comment INSERT protected (unauthorized users blocked on insert)
- ✅ Comment UPDATE protected (unauthorized users blocked on update)

---

### 4. Profile Creation Trigger on auth.users

**Purpose:** Verify the profile auto-creation trigger is attached to auth.users

```sql
SELECT 
    t.tgname,
    r.relname as table_name,
    n.nspname as schema_name,
    pg_get_triggerdef(t.oid) as definition
FROM pg_trigger t
JOIN pg_class r ON t.tgrelid = r.oid
JOIN pg_namespace n ON r.relnamespace = n.oid
WHERE t.tgname = 'trigger_create_profile_on_signup';
```

**Expected Result:**
```
trigger_name: trigger_create_profile_on_signup
table_name: users
schema_name: auth
definition: CREATE TRIGGER trigger_create_profile_on_signup AFTER INSERT ON auth.users FOR EACH ROW EXECUTE FUNCTION create_profile_on_signup()
```

**What This Verifies:**
- ✅ Trigger exists on auth.users (not public schema)
- ✅ Event is AFTER INSERT (correct for user creation)
- ✅ Calls profile creation function

---

### 5. Timestamp Update Triggers

**Purpose:** Verify all tables have timestamp update triggers

```sql
SELECT 
    t.tgname,
    r.relname as table_name,
    pg_get_triggerdef(t.oid) as definition
FROM pg_trigger t
JOIN pg_class r ON t.tgrelid = r.oid
WHERE t.tgname LIKE 'trigger_%_updated_at'
ORDER BY r.relname;
```

**Expected Results:** 5 rows
- trigger_goals_updated_at
- trigger_hobbies_updated_at
- trigger_posts_updated_at
- trigger_profiles_updated_at
- trigger_skills_updated_at

**What This Verifies:**
- ✅ All temporal tables have timestamp triggers
- ✅ All registered for BEFORE UPDATE
- ✅ All call update_timestamp() function

---

### 6. Data Integrity Triggers

**Purpose:** Verify protection against self-likes and unauthorized likes

```sql
SELECT 
    t.tgname,
    r.relname as table_name,
    pg_get_triggerdef(t.oid) as definition
FROM pg_trigger t
JOIN pg_class r ON t.tgrelid = r.oid
JOIN pg_proc p ON t.tgfoid = p.oid
WHERE p.proname IN ('prevent_self_like', 'prevent_unauthorized_like')
ORDER BY t.tgname;
```

**Expected Results:** 2 rows
- trigger_prevent_self_like (BEFORE INSERT)
- trigger_prevent_unauthorized_like (BEFORE INSERT)

**What This Verifies:**
- ✅ Users cannot like their own posts
- ✅ Users cannot like others' private posts

---

## Comparison Verification

**Run this to compare deployed vs expected events:**

```sql
-- Check all custom triggers have correct event types
SELECT 
    t.tgname,
    r.relname,
    CASE 
        WHEN pg_get_triggerdef(t.oid) LIKE '%BEFORE INSERT%' THEN 'BEFORE INSERT'
        WHEN pg_get_triggerdef(t.oid) LIKE '%BEFORE UPDATE%' THEN 'BEFORE UPDATE'
        WHEN pg_get_triggerdef(t.oid) LIKE '%AFTER INSERT%' THEN 'AFTER INSERT'
        WHEN pg_get_triggerdef(t.oid) LIKE '%BEFORE INSERT OR UPDATE%' THEN 'BEFORE INSERT OR UPDATE'
        ELSE 'OTHER'
    END as trigger_event
FROM pg_trigger t
JOIN pg_class r ON t.tgrelid = r.oid
JOIN pg_proc p ON t.tgfoid = p.oid
WHERE p.proname NOT LIKE 'RI_%'
ORDER BY r.relname, t.tgname;
```

**Expected Result:** All triggers show correct event types (no OTHER)

---

## Summary Table (For Reference)

| Trigger Name | Table | Event | Purpose |
|---|---|---|---|
| trigger_create_profile_on_signup | auth.users | AFTER INSERT | Auto-create profile on signup |
| trigger_profiles_updated_at | profiles | BEFORE UPDATE | Auto-update timestamp |
| trigger_hobbies_updated_at | hobbies | BEFORE UPDATE | Auto-update timestamp |
| trigger_skills_updated_at | skills | BEFORE UPDATE | Auto-update timestamp |
| trigger_goals_updated_at | goals | BEFORE UPDATE | Auto-update timestamp |
| trigger_posts_updated_at | posts | BEFORE UPDATE | Auto-update timestamp |
| trigger_comments_updated_at | comments | BEFORE UPDATE | Auto-update timestamp |
| trigger_validate_goal_ownership | goals | BEFORE INSERT OR UPDATE | Ownership validation |
| trigger_validate_milestone_ownership | milestones | BEFORE INSERT OR UPDATE | Ownership validation |
| trigger_validate_post_ownership | posts | BEFORE INSERT OR UPDATE | Ownership validation |
| trigger_validate_practice_session_ownership | practice_sessions | BEFORE INSERT OR UPDATE | Ownership validation |
| trigger_validate_upload_ownership | uploads | BEFORE INSERT OR UPDATE | Ownership validation |
| trigger_prevent_self_like | likes | BEFORE INSERT | Prevent self-likes |
| trigger_prevent_unauthorized_like | likes | BEFORE INSERT | Prevent likes on private posts |
| trigger_prevent_unauthorized_comment | comments | BEFORE INSERT | Prevent comments on private posts |
| trigger_validate_comment_visibility_on_update | comments | BEFORE UPDATE | Prevent UPDATE on private post comments |

**Total:** 16 triggers (15 in public schema + 1 in auth schema)

---

## Notes

- All queries are **read-only** and safe to run
- Queries use `pg_get_triggerdef()` which is PostgreSQL's official function for retrieving trigger definitions
- Results can be run in Supabase SQL Editor without authentication credentials
- No data modification is performed

