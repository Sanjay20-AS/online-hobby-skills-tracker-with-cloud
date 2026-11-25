#!/usr/bin/env python
"""
Validate corrected migration for critical issues:
- No subqueries in CHECK constraints
- Proper trigger functions
- RLS policy syntax
- Table structure
"""
import re
import sys
from pathlib import Path

def validate_corrected_migration(filepath):
    """Validate corrected migration."""
    with open(filepath, 'r') as f:
        sql = f.read()
    
    print(f"=== Corrected Migration Validation ===\n")
    
    errors = []
    warnings = []
    
    # 1. Check for remaining invalid CHECK constraints with subqueries
    print("1. Checking for invalid CHECK constraints with subqueries...")
    invalid_checks = re.findall(r'CHECK\s*\(\s*(SELECT|WHERE|IN\s*\()', sql, re.IGNORECASE)
    if invalid_checks:
        errors.append(f"Found {len(invalid_checks)} CHECK constraints with subqueries (INVALID)")
    else:
        print("   ✅ No subqueries in CHECK constraints")
    
    # 2. Verify CHECK constraints are valid
    print("\n2. Validating CHECK constraint structure...")
    valid_checks = [
        "LENGTH(TRIM",
        "proficiency_level IN",
        "duration_minutes > 0",
        "file_size > 0",
        "target_hours > 0",
        "status IN",
        "visibility IN"
    ]
    for vc in valid_checks:
        if vc in sql:
            print(f"   ✅ {vc}")
        else:
            warnings.append(f"Expected CHECK constraint not found: {vc}")
    
    # 3. Check for profile function improvements
    print("\n3. Checking profile creation function...")
    if "SECURITY DEFINER SET search_path" in sql:
        print("   ✅ SECURITY DEFINER with restricted search_path")
    else:
        errors.append("Profile function missing restricted search_path")
    
    if "collision" in sql.lower() or "counter" in sql:
        print("   ✅ Username collision handling implemented")
    else:
        warnings.append("Username collision resolution not found")
    
    # 4. Check visibility field usage
    print("\n4. Checking visibility field usage...")
    visibility_uses = len(re.findall(r"visibility\s*=\s*['\"]", sql))
    if visibility_uses > 0:
        print(f"   ✅ Visibility field used {visibility_uses} times")
    else:
        errors.append("Visibility field not properly used")
    
    old_public_uses = len(re.findall(r"is_public", sql))
    if old_public_uses == 0:
        print("   ✅ Old is_public field completely removed")
    else:
        errors.append(f"Old is_public field still present ({old_public_uses} uses)")
    
    # 5. Check triggers for self-like and visibility prevention
    print("\n5. Checking data integrity triggers...")
    triggers = {
        "prevent_self_like": "Users cannot like their own posts",
        "prevent_unauthorized_comment": "Cannot comment on private posts",
        "prevent_unauthorized_like": "Cannot like private posts"
    }
    
    for trigger, desc in triggers.items():
        if trigger in sql:
            print(f"   ✅ {trigger}")
        else:
            errors.append(f"Missing trigger: {trigger}")
    
    # 6. Verify table structure
    print("\n6. Verifying table structure...")
    required_tables = [
        'profiles', 'hobbies', 'skills', 'goals', 'practice_sessions',
        'milestones', 'uploads', 'posts', 'likes', 'comments', 'follows'
    ]
    
    for table in required_tables:
        if f'CREATE TABLE IF NOT EXISTS {table}' in sql:
            print(f"   ✅ {table}")
        else:
            errors.append(f"Table {table} missing")
    
    # 7. Check new fields
    print("\n7. Verifying new fields...")
    new_fields = {
        'skills.hobby_id': 'hobby_id UUID REFERENCES hobbies',
        'goals.target_hours': 'target_hours INTEGER',
        'goals.status': "status TEXT DEFAULT 'pending' CHECK",
        'uploads.hobby_id': 'hobby_id UUID REFERENCES hobbies',
        'uploads.original_filename': 'original_filename TEXT NOT NULL',
        'posts.visibility': "visibility TEXT DEFAULT 'public' CHECK"
    }
    
    for field, pattern in new_fields.items():
        if pattern in sql:
            print(f"   ✅ {field}")
        else:
            warnings.append(f"New field may be missing: {field}")
    
    # 8. RLS policies
    print("\n8. Checking RLS policies...")
    rls_policies = [
        'profiles_self_update', 'profiles_self_delete', 'profiles_select_self_or_public',
        'hobbies_owner_all', 'hobbies_select_public_user',
        'skills_owner_all', 'skills_select_public_user',
        'goals_owner_all', 'practice_sessions_owner_all', 'milestones_owner_all',
        'uploads_owner_all', 'posts_owner_all', 'posts_select_own_or_public',
        'likes_owner_delete_insert', 'likes_owner_insert', 'likes_select_visible_posts',
        'comments_owner_all', 'comments_select_visible_posts',
        'follows_follower_all', 'follows_select_all'
    ]
    
    policies_found = 0
    for policy in rls_policies:
        if f'"{policy}"' in sql or f"'{policy}'" in sql:
            policies_found += 1
    
    print(f"   RLS policies: {policies_found}/{len(rls_policies)}")
    if policies_found >= 15:
        print("   ✅ Sufficient RLS policies")
    else:
        warnings.append(f"Low RLS policy count: {policies_found}")
    
    # Summary
    print(f"\n{'='*50}")
    if errors:
        print(f"❌ {len(errors)} error(s) found:")
        for err in errors:
            print(f"   - {err}")
        return False
    elif warnings:
        print(f"⚠️  {len(warnings)} warning(s):")
        for warn in warnings:
            print(f"   - {warn}")
        print(f"\n✅ Migration structure valid (warnings non-critical)")
        return True
    else:
        print(f"✅ Migration structure valid")
        return True

if __name__ == '__main__':
    migration_file = Path(__file__).parent.parent / 'supabase' / 'migrations' / '0001_initial_schema.sql'
    
    if not migration_file.exists():
        print(f"❌ Migration file not found: {migration_file}")
        sys.exit(1)
    
    success = validate_corrected_migration(migration_file)
    sys.exit(0 if success else 1)
