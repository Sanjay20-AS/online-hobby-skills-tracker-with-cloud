#!/usr/bin/env python3
"""Comprehensive trigger verification."""

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
    print("COMPREHENSIVE TRIGGER VERIFICATION")
    print("=" * 100)
    
    # Get ALL user-defined triggers (exclude system RI_ triggers)
    cursor.execute("""
    SELECT 
        t.tgname,
        r.relname as table_name,
        p.proname,
        CASE WHEN t.tgtype & 2 = 2 THEN 'BEFORE' ELSE 'AFTER' END as timing,
        CASE 
            WHEN t.tgtype & 4 = 4 THEN 'INSERT'
            WHEN t.tgtype & 8 = 8 THEN 'UPDATE'
            WHEN t.tgtype & 16 = 16 THEN 'DELETE'
        END as event
    FROM pg_trigger t
    JOIN pg_class r ON t.tgrelid = r.oid
    JOIN pg_proc p ON t.tgfoid = p.oid
    JOIN pg_namespace n ON r.relnamespace = n.oid
    WHERE n.nspname = 'public'
    AND p.proname NOT LIKE 'RI_%'
    ORDER BY r.relname, t.tgname;
    """)
    
    results = cursor.fetchall()
    
    expected_triggers = {
        'profiles': 'trigger_create_profile_on_signup (via auth.users)',
        'profiles': 'trigger_profiles_updated_at',
        'hobbies': 'trigger_hobbies_updated_at',
        'skills': 'trigger_skills_updated_at',
        'goals': 'trigger_goals_updated_at',
        'posts': 'trigger_posts_updated_at',
        'comments': 'trigger_comments_updated_at',
        'likes': 'trigger_likes_updated_at',
    }
    
    print(f"\nTotal user-defined triggers found: {len(results)}\n")
    
    trigger_dict = {}
    for trigger_name, table_name, func_name, timing, event in results:
        if table_name not in trigger_dict:
            trigger_dict[table_name] = []
        trigger_dict[table_name].append({
            'name': trigger_name,
            'func': func_name,
            'timing': timing,
            'event': event
        })
    
    for table_name in sorted(trigger_dict.keys()):
        print(f"\n{table_name.upper()}:")
        for tri in trigger_dict[table_name]:
            print(f"  {tri['timing']:6} {tri['event']:6} - {tri['name']:50} -> {tri['func']}")
    
    # Specific checks
    print("\n" + "=" * 100)
    print("SPECIFIC CHECKS")
    print("=" * 100)
    
    checks = [
        ("Profile creation on auth.users", 
         "SELECT COUNT(*) FROM pg_trigger t JOIN pg_class r ON t.tgrelid = r.oid WHERE t.tgname = 'trigger_create_profile_on_signup' AND r.relname = 'users'"),
        ("Ownership triggers (5 total)", 
         "SELECT COUNT(*) FROM pg_proc WHERE proname LIKE 'validate_%_ownership'"),
        ("Comment INSERT security", 
         "SELECT COUNT(*) FROM pg_trigger t JOIN pg_class r ON t.tgrelid = r.oid WHERE t.tgname = 'trigger_prevent_unauthorized_comment' AND r.relname = 'comments'"),
        ("Comment UPDATE security", 
         "SELECT COUNT(*) FROM pg_trigger t JOIN pg_class r ON t.tgrelid = r.oid WHERE t.tgname = 'trigger_validate_comment_visibility_on_update' AND r.relname = 'comments' AND (t.tgtype & 8 = 8)"),
        ("Timestamp triggers", 
         "SELECT COUNT(*) FROM pg_trigger WHERE tgname LIKE 'trigger_%_updated_at'"),
    ]
    
    for check_name, query in checks:
        cursor.execute(query)
        result = cursor.fetchone()[0]
        status = "✅" if result > 0 else "❌"
        print(f"{status} {check_name}: {result}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
