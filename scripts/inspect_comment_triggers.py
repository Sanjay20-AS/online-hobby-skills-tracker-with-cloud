#!/usr/bin/env python3
"""Detailed inspection of comment security triggers."""

import os
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
    
    # Query: Get ALL comment-related triggers
    query = """
    SELECT 
        t.tgname as trigger_name,
        r.relname as table_name,
        p.proname as function_name,
        CASE 
            WHEN t.tgtype & 2 = 2 THEN 'BEFORE'
            WHEN t.tgtype & 64 = 64 THEN 'INSTEAD OF'
            ELSE 'AFTER'
        END as timing,
        CASE 
            WHEN t.tgtype & 4 = 4 THEN 'INSERT'
            WHEN t.tgtype & 8 = 8 THEN 'UPDATE'
            WHEN t.tgtype & 16 = 16 THEN 'DELETE'
        END as event
    FROM pg_trigger t
    JOIN pg_class r ON t.tgrelid = r.oid
    JOIN pg_proc p ON t.tgfoid = p.oid
    WHERE r.relname = 'comments'
    ORDER BY t.tgname;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    print("=" * 80)
    print("COMMENT SECURITY TRIGGERS - DETAILED INSPECTION")
    print("=" * 80)
    print(f"\nTotal comment triggers found: {len(results)}\n")
    
    for trigger_name, table_name, func_name, timing, event in results:
        print(f"Trigger: {trigger_name}")
        print(f"  Table: {table_name}")
        print(f"  Function: {func_name}")
        print(f"  Timing: {timing}")
        print(f"  Event: {event}")
        print()
    
    # Check for UPDATE event specifically
    print("\nUPDATE Event Check:")
    cursor.execute("""
    SELECT t.tgname, 
           CASE WHEN t.tgtype & 8 = 8 THEN 'YES' ELSE 'NO' END as is_update_trigger
    FROM pg_trigger t
    JOIN pg_class r ON t.tgrelid = r.oid
    WHERE r.relname = 'comments'
    ORDER BY t.tgname;
    """)
    
    update_results = cursor.fetchall()
    for trigger_name, is_update in update_results:
        print(f"  {trigger_name}: UPDATE={is_update}")
    
    # Check if function covers UPDATE in its logic
    print("\nFunction Definition Check:")
    cursor.execute("""
    SELECT pg_get_functiondef(p.oid)
    FROM pg_proc p
    WHERE p.proname = 'prevent_unauthorized_comment';
    """)
    
    func_def = cursor.fetchone()
    if func_def:
        func_text = func_def[0]
        print(f"Function length: {len(func_text)} chars")
        print(f"Covers UPDATE logic: {'UPDATE' in func_text or 'TG_OP' in func_text}")
        print(f"Uses TG_OP: {'TG_OP' in func_text}")
    
    conn.close()
    print("\n✅ Query executed successfully")
    
except Exception as e:
    print(f"❌ Error: {e}")
