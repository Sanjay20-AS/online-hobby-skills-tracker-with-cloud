#!/usr/bin/env python3
"""
Final comprehensive trigger verification using pg_get_triggerdef()
Compare deployed vs migration file expectations
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
    print("PHASE 4 FINAL TRIGGER VERIFICATION")
    print("=" * 120)
    
    # Get complete inventory
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
    
    # Expected triggers from migration file
    expected = {
        'trigger_create_profile_on_signup': {'table': 'users', 'schema': 'auth', 'event': 'AFTER INSERT'},
        'trigger_profiles_updated_at': {'table': 'profiles', 'event': 'BEFORE UPDATE'},
        'trigger_hobbies_updated_at': {'table': 'hobbies', 'event': 'BEFORE UPDATE'},
        'trigger_skills_updated_at': {'table': 'skills', 'event': 'BEFORE UPDATE'},
        'trigger_goals_updated_at': {'table': 'goals', 'event': 'BEFORE UPDATE'},
        'trigger_posts_updated_at': {'table': 'posts', 'event': 'BEFORE UPDATE'},
        'trigger_comments_updated_at': {'table': 'comments', 'event': 'BEFORE UPDATE'},
        'trigger_prevent_self_like': {'table': 'likes', 'event': 'BEFORE INSERT'},
        'trigger_prevent_unauthorized_comment': {'table': 'comments', 'event': 'BEFORE INSERT'},
        'trigger_prevent_unauthorized_like': {'table': 'likes', 'event': 'BEFORE INSERT'},
        'trigger_validate_goal_ownership': {'table': 'goals', 'event': 'BEFORE INSERT OR UPDATE'},
        'trigger_validate_practice_session_ownership': {'table': 'practice_sessions', 'event': 'BEFORE INSERT OR UPDATE'},
        'trigger_validate_milestone_ownership': {'table': 'milestones', 'event': 'BEFORE INSERT OR UPDATE'},
        'trigger_validate_post_ownership': {'table': 'posts', 'event': 'BEFORE INSERT OR UPDATE'},
        'trigger_validate_upload_ownership': {'table': 'uploads', 'event': 'BEFORE INSERT OR UPDATE'},
        'trigger_validate_comment_visibility_on_update': {'table': 'comments', 'event': 'BEFORE UPDATE'},
    }
    
    print("\nTRIGGER VERIFICATION TABLE")
    print("-" * 120)
    print(f"{'Trigger Name':<50} {'Table':<20} {'Expected Event':<25} {'Deployed Event':<25}")
    print("-" * 120)
    
    deployed_dict = {}
    for trigger_name, table_name, trigger_def in triggers:
        deployed_dict[trigger_name] = (table_name, trigger_def)
    
    issues = []
    for trigger_name, expected_info in expected.items():
        expected_table = expected_info['table']
        expected_event = expected_info['event']
        
        if trigger_name in deployed_dict:
            deployed_table, deployed_def = deployed_dict[trigger_name]
            
            # Extract event from trigger definition
            if 'BEFORE INSERT OR UPDATE' in deployed_def:
                deployed_event = 'BEFORE INSERT OR UPDATE'
            elif 'BEFORE INSERT' in deployed_def:
                deployed_event = 'BEFORE INSERT'
            elif 'BEFORE UPDATE' in deployed_def:
                deployed_event = 'BEFORE UPDATE'
            elif 'AFTER INSERT' in deployed_def:
                deployed_event = 'AFTER INSERT'
            else:
                deployed_event = 'UNKNOWN'
            
            # Check for mismatch
            match = expected_event == deployed_event
            status = '✅' if match else '❌'
            
            if not match:
                issues.append({
                    'trigger': trigger_name,
                    'table': deployed_table,
                    'expected': expected_event,
                    'deployed': deployed_event
                })
            
            print(f"{trigger_name:<50} {deployed_table:<20} {expected_event:<25} {deployed_event:<25} {status}")
        else:
            print(f"{trigger_name:<50} {'MISSING':<20} {expected_event:<25} {'NOT FOUND':<25} ❌")
            issues.append({
                'trigger': trigger_name,
                'table': expected_table,
                'expected': expected_event,
                'deployed': 'NOT FOUND'
            })
    
    print("\n" + "=" * 120)
    print("VERIFICATION RESULTS")
    print("=" * 120)
    
    if not issues:
        print("\n✅ ALL TRIGGERS DEPLOYED CORRECTLY")
        print(f"   Total triggers: {len(triggers)}")
        print(f"   All events match expected definitions")
        print("\n🟢 NO CORRECTIONS NEEDED - Phase 4 trigger implementation is correct!")
    else:
        print(f"\n❌ ISSUES FOUND: {len(issues)}")
        for issue in issues:
            print(f"\n   Trigger: {issue['trigger']}")
            print(f"   Table: {issue['table']}")
            print(f"   Expected: {issue['expected']}")
            print(f"   Deployed: {issue['deployed']}")
    
    # Double-check the critical trigger
    print("\n" + "=" * 120)
    print("CRITICAL FOCUS: Comment UPDATE Protection")
    print("=" * 120)
    
    cursor.execute("""
    SELECT pg_get_triggerdef(t.oid)
    FROM pg_trigger t
    WHERE t.tgname = 'trigger_validate_comment_visibility_on_update';
    """)
    
    result = cursor.fetchone()
    if result:
        trigger_def = result[0]
        print(f"\nTrigger Definition:")
        print(trigger_def)
        
        if "BEFORE UPDATE" in trigger_def:
            print("\n✅ CONFIRMED: Correctly registered for BEFORE UPDATE")
            print("   Comment UPDATE protection is properly implemented")
        else:
            print("\n❌ ERROR: Not registered for UPDATE")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
