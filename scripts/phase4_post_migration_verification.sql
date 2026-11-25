-- ============================================================================
-- PHASE 4 POST-MIGRATION VERIFICATION SCRIPT
-- ============================================================================
-- Purpose: Verify the deployed profile-creation function and database schema
-- Usage: Run in Supabase SQL Editor or via psql
-- Safety: Read-only queries; no modifications to production data
-- ============================================================================

-- ============================================================================
-- SECTION 1: FUNCTION DEFINITION INSPECTION
-- ============================================================================
-- Purpose: Extract and display the deployed create_profile_on_signup function

SELECT 
    n.nspname as schema_name,
    p.proname as function_name,
    pg_get_functiondef(p.oid) as function_definition
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE p.proname = 'create_profile_on_signup'
    AND n.nspname = 'public';

-- ============================================================================
-- SECTION 2: TRIGGER VERIFICATION
-- ============================================================================
-- Purpose: Verify the trigger is correctly attached to auth.users

SELECT 
    t.tgname as trigger_name,
    r.relname as table_name,
    t.tgtype as trigger_type,
    p.proname as function_name,
    t.tgenabled as enabled
FROM pg_trigger t
JOIN pg_class r ON t.tgrelid = r.oid
JOIN pg_proc p ON t.tgfoid = p.oid
WHERE t.tgname = 'trigger_create_profile_on_signup'
    AND r.relname = 'users'
    AND r.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'auth');

-- ============================================================================
-- SECTION 3: TABLE STRUCTURE VERIFICATION
-- ============================================================================
-- Purpose: Verify profiles table structure matches migration

SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public' 
    AND table_name = 'profiles'
ORDER BY ordinal_position;

-- ============================================================================
-- SECTION 4: CONSTRAINT VERIFICATION
-- ============================================================================
-- Purpose: Verify UNIQUE constraint on username

SELECT 
    constraint_name,
    constraint_type,
    table_name
FROM information_schema.table_constraints
WHERE table_schema = 'public' 
    AND table_name = 'profiles'
    AND constraint_type IN ('UNIQUE', 'PRIMARY KEY');

-- Purpose: Verify case-insensitive unique index

SELECT 
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public' 
    AND tablename = 'profiles'
    AND indexname LIKE '%username%';

-- ============================================================================
-- SECTION 5: OWNERSHIP TRIGGER VERIFICATION
-- ============================================================================
-- Purpose: Verify all 5 ownership validation triggers are present

SELECT 
    t.tgname as trigger_name,
    r.relname as table_name,
    p.proname as function_name
FROM pg_trigger t
JOIN pg_class r ON t.tgrelid = r.oid
JOIN pg_proc p ON t.tgfoid = p.oid
WHERE p.proname LIKE 'validate_%_ownership'
    AND r.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
ORDER BY r.relname;

-- ============================================================================
-- SECTION 6: COMMENT SECURITY TRIGGER VERIFICATION
-- ============================================================================
-- Purpose: Verify comment protection triggers (INSERT and UPDATE)

SELECT 
    t.tgname as trigger_name,
    r.relname as table_name,
    p.proname as function_name,
    CASE 
        WHEN t.tgtype & 2 = 2 THEN 'BEFORE'
        WHEN t.tgtype & 64 = 64 THEN 'INSTEAD OF'
        ELSE 'AFTER'
    END as trigger_timing,
    CASE 
        WHEN t.tgtype & 4 = 4 THEN 'INSERT'
        WHEN t.tgtype & 8 = 8 THEN 'UPDATE'
        WHEN t.tgtype & 16 = 16 THEN 'DELETE'
    END as trigger_event
FROM pg_trigger t
JOIN pg_class r ON t.tgrelid = r.oid
JOIN pg_proc p ON t.tgfoid = p.oid
WHERE (p.proname LIKE '%unauthorized_comment%' OR p.proname LIKE '%prevent_unauthorized_comment%')
    AND r.relname = 'comments'
ORDER BY t.tgname;

-- ============================================================================
-- SECTION 7: RLS POLICY VERIFICATION
-- ============================================================================
-- Purpose: Count RLS policies per table (expect 20 total)

SELECT 
    schemaname,
    tablename,
    COUNT(*) as policy_count
FROM pg_policies
WHERE schemaname = 'public'
GROUP BY schemaname, tablename
ORDER BY tablename;

-- Overall policy count
SELECT COUNT(*) as total_rls_policies
FROM pg_policies
WHERE schemaname = 'public';

-- ============================================================================
-- SECTION 8: FOLLOWS TABLE VISIBILITY POLICY
-- ============================================================================
-- Purpose: Verify follows RLS policy is restricted to authenticated users

SELECT 
    policyname,
    qual,
    with_check,
    permissive
FROM pg_policies
WHERE schemaname = 'public'
    AND tablename = 'follows';

-- ============================================================================
-- SECTION 9: DATA INTEGRITY TRIGGER VERIFICATION
-- ============================================================================
-- Purpose: Verify prevent_self_like, prevent_unauthorized_like, prevent_unauthorized_comment

SELECT 
    p.proname as function_name,
    r.relname as table_name,
    t.tgname as trigger_name
FROM pg_proc p
JOIN pg_trigger t ON t.tgfoid = p.oid
JOIN pg_class r ON t.tgrelid = r.oid
WHERE p.proname IN ('prevent_self_like', 'prevent_unauthorized_like', 'prevent_unauthorized_comment')
ORDER BY p.proname;

-- ============================================================================
-- SECTION 10: PROFILE COUNT (BASELINE)
-- ============================================================================
-- Purpose: Get current profile count (for regression testing)

SELECT COUNT(*) as current_profile_count FROM public.profiles;

-- ============================================================================
-- SECTION 11: FUNCTION SOURCE CODE INSPECTION
-- ============================================================================
-- Purpose: Display key sections of create_profile_on_signup for verification

SELECT 
    p.proname,
    pg_get_functiondef(p.oid) as full_definition
FROM pg_proc p
WHERE p.proname = 'create_profile_on_signup';
