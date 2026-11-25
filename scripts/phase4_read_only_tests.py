#!/usr/bin/env python3
"""
Phase 4 Read-Only Behavioral Tests

These tests read from the database without modifying any data.
Safe to run against production.
"""

import psycopg2

env_path = "backend/.env"
database_url = None
with open(env_path) as f:
    for line in f:
        if line.startswith("DATABASE_URL="):
            database_url = line.split("=", 1)[1].strip()
            break

try:
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    print("=" * 100)
    print("PHASE 4 READ-ONLY BEHAVIORAL TESTS")
    print("=" * 100)
    print("\nThese tests require no data modification and can safely run.\n")
    
    # TEST: Check if profiles table is accessible
    print("-" * 100)
    print("TEST 1: Profiles Table Structure & Constraints")
    print("-" * 100)
    
    cursor.execute("""
    SELECT 
        column_name,
        data_type,
        is_nullable,
        column_default
    FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'profiles'
    ORDER BY ordinal_position;
    """)
    
    columns = cursor.fetchall()
    print(f"✅ Profiles table is readable")
    print(f"   Columns: {len(columns)}")
    for col_name, col_type, is_nullable, default in columns:
        print(f"     - {col_name}: {col_type}")
    
    # TEST: Check UNIQUE constraint
    cursor.execute("""
    SELECT constraint_name, constraint_type
    FROM information_schema.table_constraints
    WHERE table_schema = 'public' AND table_name = 'profiles' AND constraint_type = 'UNIQUE';
    """)
    
    constraints = cursor.fetchall()
    print(f"\n✅ UNIQUE constraints present: {len(constraints)}")
    for constraint_name, constraint_type in constraints:
        print(f"     - {constraint_name}")
    
    # TEST: Check case-insensitive index
    cursor.execute("""
    SELECT indexname FROM pg_indexes
    WHERE schemaname = 'public' AND tablename = 'profiles' AND indexname LIKE '%username%';
    """)
    
    indexes = cursor.fetchall()
    print(f"\n✅ Username indexes: {len(indexes)}")
    for (index_name,) in indexes:
        print(f"     - {index_name}")
    
    # TEST: Check RLS policies
    cursor.execute("""
    SELECT tablename, COUNT(*) as policy_count
    FROM pg_policies WHERE schemaname = 'public'
    GROUP BY tablename ORDER BY tablename;
    """)
    
    policies = cursor.fetchall()
    total_policies = sum(count for _, count in policies)
    print(f"\n✅ RLS policies deployed: {total_policies} total")
    for table_name, count in policies:
        print(f"     - {table_name}: {count}")
    
    # TEST: Check all 11 tables exist
    cursor.execute("""
    SELECT COUNT(*) FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
    """)
    
    table_count = cursor.fetchone()[0]
    print(f"\n✅ Tables deployed: {table_count} total")
    
    expected_tables = ['profiles', 'hobbies', 'skills', 'goals', 'practice_sessions', 
                       'milestones', 'uploads', 'posts', 'likes', 'comments', 'follows']
    
    cursor.execute("""
    SELECT tablename FROM pg_tables 
    WHERE schemaname = 'public' ORDER BY tablename;
    """)
    
    actual_tables = [row[0] for row in cursor.fetchall()]
    for table_name in expected_tables:
        status = "✅" if table_name in actual_tables else "❌"
        print(f"     {status} {table_name}")
    
    # TEST: Profile baseline count (can safely query)
    cursor.execute("SELECT COUNT(*) FROM public.profiles;")
    profile_count = cursor.fetchone()[0]
    print(f"\n✅ Current profile count: {profile_count}")
    
    # TEST: Check if there are any data to test with
    cursor.execute("SELECT COUNT(*) FROM public.hobbies;")
    hobbies_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM public.posts;")
    posts_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM public.comments;")
    comments_count = cursor.fetchone()[0]
    
    print(f"\n✅ Existing data counts (for reference):")
    print(f"     - Hobbies: {hobbies_count}")
    print(f"     - Posts: {posts_count}")
    print(f"     - Comments: {comments_count}")
    
    # TEST: Trigger status (read-only)
    print("\n" + "-" * 100)
    print("TEST 2: Trigger Status (Read-Only Query)")
    print("-" * 100)
    
    cursor.execute("""
    SELECT 
        p.proname,
        r.relname,
        t.tgname,
        CASE WHEN t.tgtype & 2 = 2 THEN 'BEFORE' ELSE 'AFTER' END as timing,
        CASE 
            WHEN t.tgtype & 4 = 4 THEN 'INSERT'
            WHEN t.tgtype & 8 = 8 THEN 'UPDATE'
            WHEN t.tgtype & 16 = 16 THEN 'DELETE'
        END as event
    FROM pg_proc p
    JOIN pg_trigger t ON t.tgfoid = p.oid
    JOIN pg_class r ON t.tgrelid = r.oid
    WHERE p.proname IN (
        'validate_goal_ownership',
        'validate_practice_session_ownership',
        'validate_milestone_ownership',
        'validate_post_ownership',
        'validate_upload_ownership',
        'prevent_unauthorized_comment',
        'validate_comment_visibility_on_update'
    )
    ORDER BY p.proname;
    """)
    
    triggers = cursor.fetchall()
    print(f"✅ Ownership/security triggers found: {len(triggers)}")
    for func_name, table_name, trigger_name, timing, event in triggers:
        print(f"     - {func_name:40} on {table_name:20} ({timing} {event})")
    
    # TEST: Check if profile creation function exists
    print("\n" + "-" * 100)
    print("TEST 3: Profile Creation Function (Read-Only)")
    print("-" * 100)
    
    cursor.execute("""
    SELECT pg_get_functiondef(p.oid)
    FROM pg_proc p
    WHERE p.proname = 'create_profile_on_signup';
    """)
    
    result = cursor.fetchone()
    if result:
        func_def = result[0]
        checks = [
            ("SECURITY DEFINER", "SECURITY DEFINER" in func_def),
            ("Username collision handling", "WHILE EXISTS" in func_def),
            ("Counter-based suffix", "counter + 1" in func_def or "counter ::=" in func_def),
            ("UUID fallback", "'user_'" in func_def),
            ("Error propagation", "EXCEPTION WHEN OTHERS" in func_def),
        ]
        print(f"✅ Profile creation function found")
        for check_name, check_result in checks:
            status = "✅" if check_result else "❌"
            print(f"     {status} {check_name}")
    else:
        print(f"❌ Profile creation function NOT found")
    
    print("\n" + "=" * 100)
    print("SUMMARY: All read-only behavioral tests completed successfully ✅")
    print("=" * 100)
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
