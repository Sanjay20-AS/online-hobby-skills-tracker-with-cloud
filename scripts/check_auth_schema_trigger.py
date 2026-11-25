#!/usr/bin/env python3
"""Check if profile creation trigger exists on auth.users"""

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
    print("CHECKING PROFILE CREATION TRIGGER ON AUTH.USERS")
    print("=" * 100)
    
    # Check if trigger exists on auth.users
    cursor.execute("""
    SELECT 
        t.tgname,
        r.relname,
        n.nspname,
        pg_get_triggerdef(t.oid) as definition
    FROM pg_trigger t
    JOIN pg_class r ON t.tgrelid = r.oid
    JOIN pg_namespace n ON r.relnamespace = n.oid
    WHERE r.relname = 'users'
    AND n.nspname = 'auth';
    """)
    
    results = cursor.fetchall()
    
    if results:
        print(f"\n✅ Triggers found on auth.users: {len(results)}\n")
        for trigger_name, table_name, schema_name, definition in results:
            print(f"Trigger: {trigger_name}")
            print(f"Table: {schema_name}.{table_name}")
            print(f"Definition:")
            print(definition)
            print()
    else:
        print("\n❌ No triggers found on auth.users")
        print("\nThis means the profile creation trigger was NOT deployed on auth.users")
        print("However, Supabase Auth integration may handle this differently.")
    
    # Also check if the function exists
    print("\n" + "=" * 100)
    print("CHECKING IF PROFILE CREATION FUNCTION EXISTS")
    print("=" * 100)
    
    cursor.execute("""
    SELECT pg_get_functiondef(p.oid)
    FROM pg_proc p
    WHERE p.proname = 'create_profile_on_signup'
    AND p.pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public');
    """)
    
    result = cursor.fetchone()
    if result:
        print("\n✅ Function create_profile_on_signup exists in public schema")
        print("\nFunction is deployed and ready to be attached to auth.users")
    else:
        print("\n❌ Function create_profile_on_signup NOT found")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
