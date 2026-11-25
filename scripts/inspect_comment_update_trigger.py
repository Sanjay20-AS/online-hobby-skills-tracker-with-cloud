#!/usr/bin/env python3
"""Inspect comment UPDATE trigger function."""

import psycopg2

# Read DATABASE_URL securely
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
    
    print("=" * 80)
    print("COMMENT UPDATE PROTECTION INVESTIGATION")
    print("=" * 80)
    
    # Get the function definition
    cursor.execute("""
    SELECT pg_get_functiondef(p.oid)
    FROM pg_proc p
    WHERE p.proname = 'validate_comment_visibility_on_update';
    """)
    
    result = cursor.fetchone()
    if result:
        print("\n✅ Function found: validate_comment_visibility_on_update\n")
        print(result[0])
    else:
        print("\n❌ Function not found: validate_comment_visibility_on_update\n")
    
    # Get ALL triggers on comments ordered by name
    print("\n" + "=" * 80)
    print("ALL TRIGGERS ON COMMENTS TABLE")
    print("=" * 80 + "\n")
    
    cursor.execute("""
    SELECT 
        t.tgname,
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
    WHERE r.relname = 'comments'
    AND p.proname NOT LIKE 'RI_%'
    ORDER BY t.tgname;
    """)
    
    for trigger_name, func_name, timing, event in cursor.fetchall():
        print(f"{timing} {event:6} - {trigger_name:45} -> {func_name}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
