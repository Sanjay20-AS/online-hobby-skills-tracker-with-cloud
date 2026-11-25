#!/usr/bin/env python3
"""
Deep inspection of deployed trigger definitions using pg_get_triggerdef()
Compare with migration file definitions
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
    
    print("=" * 120)
    print("PHASE 4 TRIGGER DEFINITION INVESTIGATION")
    print("Using pg_get_triggerdef() for authoritative trigger definitions")
    print("=" * 120)
    
    # Get ALL user-defined triggers with their full definitions
    cursor.execute("""
    SELECT 
        t.tgname as trigger_name,
        r.relname as table_name,
        pg_get_triggerdef(t.oid) as trigger_definition
    FROM pg_trigger t
    JOIN pg_class r ON t.tgrelid = r.oid
    JOIN pg_proc p ON t.tgfoid = p.oid
    JOIN pg_namespace n ON r.relnamespace = n.oid
    WHERE n.nspname = 'public'
    AND p.proname NOT LIKE 'RI_%'
    ORDER BY r.relname, t.tgname;
    """)
    
    triggers = cursor.fetchall()
    
    print(f"\nTotal user-defined triggers found: {len(triggers)}\n")
    
    # Categorize triggers
    ownership_triggers = []
    comment_triggers = []
    timestamp_triggers = []
    data_integrity_triggers = []
    profile_triggers = []
    
    for trigger_name, table_name, trigger_def in triggers:
        if 'ownership' in trigger_name:
            ownership_triggers.append((trigger_name, table_name, trigger_def))
        elif 'comment' in trigger_name:
            comment_triggers.append((trigger_name, table_name, trigger_def))
        elif 'updated_at' in trigger_name:
            timestamp_triggers.append((trigger_name, table_name, trigger_def))
        elif 'self_like' in trigger_name or 'unauthorized_like' in trigger_name:
            data_integrity_triggers.append((trigger_name, table_name, trigger_def))
        elif 'profile' in trigger_name:
            profile_triggers.append((trigger_name, table_name, trigger_def))
    
    # Display ownership triggers
    print("-" * 120)
    print("OWNERSHIP VALIDATION TRIGGERS (5 Expected)")
    print("-" * 120)
    for trigger_name, table_name, trigger_def in ownership_triggers:
        print(f"\n{trigger_name} on {table_name}:")
        print(trigger_def)
    print(f"\nTotal: {len(ownership_triggers)}/5")
    
    # Display comment triggers
    print("\n" + "-" * 120)
    print("COMMENT SECURITY TRIGGERS (2+ Expected: INSERT + UPDATE)")
    print("-" * 120)
    for trigger_name, table_name, trigger_def in comment_triggers:
        print(f"\n{trigger_name} on {table_name}:")
        print(trigger_def)
    print(f"\nTotal: {len(comment_triggers)}/2+")
    
    # Specifically check comment UPDATE trigger
    print("\n" + "-" * 120)
    print("CRITICAL CHECK: trigger_validate_comment_visibility_on_update")
    print("-" * 120)
    
    cursor.execute("""
    SELECT pg_get_triggerdef(t.oid)
    FROM pg_trigger t
    WHERE t.tgname = 'trigger_validate_comment_visibility_on_update';
    """)
    
    result = cursor.fetchone()
    if result:
        comment_update_def = result[0]
        print(f"\nDeployed Definition:")
        print(comment_update_def)
        
        # Check which event it's registered for
        if "BEFORE UPDATE" in comment_update_def:
            print("\n✅ CORRECT: Registered for BEFORE UPDATE")
            is_update = True
        elif "BEFORE DELETE" in comment_update_def:
            print("\n❌ WRONG: Registered for BEFORE DELETE (should be UPDATE)")
            is_update = False
        elif "BEFORE INSERT" in comment_update_def:
            print("\n❌ WRONG: Registered for BEFORE INSERT (should be UPDATE)")
            is_update = False
        else:
            print("\n❓ UNKNOWN: Could not determine trigger event")
            is_update = None
    else:
        print("❌ Trigger NOT found")
        is_update = False
    
    # Display timestamp triggers
    print("\n" + "-" * 120)
    print("TIMESTAMP UPDATE TRIGGERS")
    print("-" * 120)
    print(f"Found: {len(timestamp_triggers)}")
    for trigger_name, table_name, trigger_def in timestamp_triggers:
        print(f"\n{trigger_name}:")
        # Print abbreviated
        if len(trigger_def) > 150:
            print(trigger_def[:150] + "...")
        else:
            print(trigger_def)
    
    # Display data integrity triggers
    print("\n" + "-" * 120)
    print("DATA INTEGRITY TRIGGERS (3 Expected)")
    print("-" * 120)
    for trigger_name, table_name, trigger_def in data_integrity_triggers:
        print(f"\n{trigger_name}:")
        # Print first 100 chars
        if len(trigger_def) > 100:
            print(trigger_def[:100] + "...")
        else:
            print(trigger_def)
    print(f"\nTotal: {len(data_integrity_triggers)}/3")
    
    # Summary
    print("\n" + "=" * 120)
    print("SUMMARY")
    print("=" * 120)
    print(f"Ownership triggers: {len(ownership_triggers)}/5")
    print(f"Comment triggers: {len(comment_triggers)}/2")
    print(f"Timestamp triggers: {len(timestamp_triggers)}")
    print(f"Data integrity triggers: {len(data_integrity_triggers)}/3")
    
    if is_update is False:
        print("\n🔴 CRITICAL ISSUE CONFIRMED:")
        print("   trigger_validate_comment_visibility_on_update is NOT registered for UPDATE")
        print("   This is a migration corruption issue that requires correction")
    elif is_update is True:
        print("\n✅ NO ISSUE: trigger_validate_comment_visibility_on_update correctly registered for UPDATE")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
