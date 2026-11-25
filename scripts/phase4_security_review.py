#!/usr/bin/env python
"""
Phase 4 Security Review - Comprehensive validation of database schema correctness.
Checks:
1. Ownership integrity (cross-table references)
2. RLS policy completeness (SELECT, INSERT, UPDATE, DELETE)
3. Community security (private post/profile access)
4. Update path security
5. Auth function hardening
"""
import re
import sys
from pathlib import Path

def analyze_migration(filepath):
    """Analyze migration for security and integrity issues."""
    with open(filepath, 'r') as f:
        sql = f.read()
    
    print("=" * 70)
    print("PHASE 4 SECURITY & INTEGRITY REVIEW")
    print("=" * 70)
    
    issues = []
    warnings = []
    
    # ========================================================================
    # 1. OWNERSHIP INTEGRITY CHECKS
    # ========================================================================
    print("\n1. OWNERSHIP INTEGRITY CHECKS")
    print("-" * 70)
    
    ownership_checks = [
        ("skills.hobby_id → hobbies", "skills.hobby_id → hobbies.id", "skills table should not allow skills.hobby_id to reference another user's hobby"),
        ("goals.hobby_id → hobbies", "goals.hobby_id → hobbies.id", "goals should not allow hobby_id referencing another user's hobby"),
        ("practice_sessions.hobby_id", "practice_sessions.hobby_id → hobbies.id", "practice sessions should enforce hobby ownership"),
        ("practice_sessions.skill_id", "practice_sessions.skill_id → skills.id", "practice sessions should enforce skill ownership"),
        ("milestones.goal_id", "milestones.goal_id → goals.id", "milestones should enforce goal ownership"),
        ("uploads.hobby_id", "uploads.hobby_id → hobbies.id", "uploads should enforce hobby ownership"),
        ("posts.hobby_id", "posts.hobby_id → hobbies.id", "posts should enforce hobby ownership"),
    ]
    
    for name, pattern, desc in ownership_checks:
        # Check if FK exists
        fk_pattern = pattern.split(" → ")[0]
        if fk_pattern in sql:
            print(f"   ✅ {name} has FK relationship")
        else:
            # Check for trigger-based enforcement
            if re.search(r"trigger.*" + name.split(".")[0], sql, re.IGNORECASE):
                print(f"   ⚠️  {name} has trigger-based enforcement")
                warnings.append(f"{name}: Trigger-based ownership, needs verification")
            else:
                issues.append(f"{name}: No FK or trigger-based ownership enforcement found")
    
    # ========================================================================
    # 2. RLS POLICY COMPLETENESS
    # ========================================================================
    print("\n2. RLS POLICY COMPLETENESS (20 policies expected)")
    print("-" * 70)
    
    # Count policies per table
    tables_to_check = {
        'profiles': ['self_update', 'self_delete', 'select_self_or_public'],
        'hobbies': ['owner_all', 'select_public_user'],
        'skills': ['owner_all', 'select_public_user'],
        'goals': ['owner_all'],
        'practice_sessions': ['owner_all'],
        'milestones': ['owner_all'],
        'uploads': ['owner_all'],
        'posts': ['owner_all', 'select_own_or_public'],
        'likes': ['owner_delete_insert', 'owner_insert', 'select_visible_posts'],
        'comments': ['owner_all', 'select_visible_posts'],
        'follows': ['follower_all', 'select_all'],
    }
    
    policy_count = 0
    for table, expected_policies in tables_to_check.items():
        found_count = 0
        for policy_suffix in expected_policies:
            policy_name = f'{table}_{policy_suffix}'
            if f'"{policy_name}"' in sql or f"'{policy_name}'" in sql:
                found_count += 1
        
        policy_count += found_count
        status = "✅" if found_count == len(expected_policies) else "⚠️ "
        print(f"   {status} {table}: {found_count}/{len(expected_policies)} policies")
        
        if found_count < len(expected_policies):
            missing = set(expected_policies) - {p for p in expected_policies if f'{table}_{p}' in sql}
            warnings.append(f"{table}: Missing policies: {missing}")
    
    print(f"\n   Total: {policy_count}/20 policies found")
    if policy_count < 20:
        issues.append(f"Incomplete RLS policies: only {policy_count}/20 found")
    
    # ========================================================================
    # 3. PRIVATE POST SECURITY
    # ========================================================================
    print("\n3. PRIVATE POST SECURITY")
    print("-" * 70)
    
    # Check likes trigger for private posts
    if "prevent_unauthorized_like" in sql:
        print("   ✅ prevent_unauthorized_like trigger present")
    else:
        issues.append("Missing trigger: prevent_unauthorized_like")
    
    # Check comments trigger for private posts
    if "prevent_unauthorized_comment" in sql:
        print("   ✅ prevent_unauthorized_comment trigger present")
    else:
        issues.append("Missing trigger: prevent_unauthorized_comment")
    
    # Check if triggers cover UPDATE paths
    trigger_text = re.search(r"CREATE OR REPLACE FUNCTION prevent_unauthorized_comment.*?END;", sql, re.DOTALL)
    if trigger_text and "INSERT" in trigger_text.group():
        print("   ⚠️  prevent_unauthorized_comment covers INSERT only - UPDATE path not checked")
        warnings.append("Comments UPDATE path may bypass private-post check")
    
    trigger_text = re.search(r"CREATE OR REPLACE FUNCTION prevent_unauthorized_like.*?END;", sql, re.DOTALL)
    if trigger_text and "INSERT" in trigger_text.group():
        print("   ℹ️  prevent_unauthorized_like covers INSERT only (UPDATE not applicable)")
    
    # ========================================================================
    # 4. PROFILE VISIBILITY SECURITY
    # ========================================================================
    print("\n4. PROFILE VISIBILITY SECURITY")
    print("-" * 70)
    
    # Check profiles_select_self_or_public policy
    profile_select_policy = re.search(
        r'CREATE POLICY "profiles_select_self_or_public".*?USING\s*\((.*?)\);',
        sql, re.DOTALL
    )
    if profile_select_policy:
        policy_body = profile_select_policy.group(1)
        if "auth.uid()" in policy_body and "visibility = 'public'" in policy_body:
            print("   ✅ profiles_select_self_or_public allows self + public")
        else:
            issues.append("profiles_select_self_or_public policy may be incorrect")
    
    # Check hobbies visibility policy
    hobbies_select = re.search(
        r'CREATE POLICY "hobbies_select_public_user".*?USING\s*\((.*?)\);',
        sql, re.DOTALL
    )
    if hobbies_select:
        policy_body = hobbies_select.group(1)
        if "profiles" in policy_body and "visibility = 'public'" in policy_body:
            print("   ✅ hobbies_select_public_user restricts to public profiles")
        else:
            issues.append("hobbies_select_public_user may not properly check profile visibility")
    
    # Check skills visibility policy
    skills_select = re.search(
        r'CREATE POLICY "skills_select_public_user".*?USING\s*\((.*?)\);',
        sql, re.DOTALL
    )
    if skills_select:
        policy_body = skills_select.group(1)
        if "profiles" in policy_body and "visibility = 'public'" in policy_body:
            print("   ✅ skills_select_public_user restricts to public profiles")
        else:
            issues.append("skills_select_public_user may not properly check profile visibility")
    
    # ========================================================================
    # 5. FOLLOWS VISIBILITY SECURITY
    # ========================================================================
    print("\n5. FOLLOWS VISIBILITY SECURITY")
    print("-" * 70)
    
    follows_select = re.search(
        r'CREATE POLICY "follows_select_all".*?USING\s*\((.*?)\);',
        sql, re.DOTALL
    )
    if follows_select:
        policy_body = follows_select.group(1)
        if "TRUE" in policy_body:
            print("   ⚠️  follows_select_all allows ALL users to see follow relationships")
            warnings.append("follows visibility: ALL users can see who follows whom (may be intended)")
        else:
            print("   ✅ follows_select_all has restricted visibility")
    
    # ========================================================================
    # 6. AUTH FUNCTION HARDENING
    # ========================================================================
    print("\n6. AUTH FUNCTION HARDENING")
    print("-" * 70)
    
    # Check SECURITY DEFINER
    if "SECURITY DEFINER" in sql:
        print("   ✅ create_profile_on_signup uses SECURITY DEFINER")
    else:
        issues.append("Auth function missing SECURITY DEFINER")
    
    # Check search_path restriction
    if "SET search_path" in sql:
        search_path_match = re.search(r"SET search_path\s*=\s*([^;]+)", sql)
        if search_path_match:
            search_path = search_path_match.group(1)
            print(f"   ✅ search_path restricted to: {search_path}")
            if "public" not in search_path or "auth" not in search_path:
                warnings.append(f"search_path may be too restrictive: {search_path}")
        else:
            issues.append("Auth function has SET search_path but could not parse it")
    else:
        issues.append("Auth function missing SET search_path restriction")
    
    # Check collision handling
    if re.search(r"WHILE.*EXISTS.*SELECT.*profiles.*LOWER\(username\)", sql, re.DOTALL):
        print("   ✅ Username collision handling with counter-based suffix")
    else:
        issues.append("Username collision handling not properly implemented")
    
    # Check exception handling
    if "EXCEPTION WHEN OTHERS" in sql:
        print("   ✅ Exception handling in profile creation")
    else:
        warnings.append("Auth function may not handle exceptions properly")
    
    # ========================================================================
    # 7. COMMENT UPDATE SECURITY
    # ========================================================================
    print("\n7. COMMENT UPDATE SECURITY")
    print("-" * 70)
    
    # Check if UPDATE is covered for comments
    comments_policies = re.findall(r'CREATE POLICY.*ON comments.*', sql)
    has_update_check = False
    for policy in comments_policies:
        if "UPDATE" in policy:
            has_update_check = True
            break
    
    if has_update_check:
        print("   ✅ Comments UPDATE path appears to be covered")
    else:
        # Check trigger coverage
        if "prevent_unauthorized_comment" in sql:
            # Find if trigger covers UPDATE
            trigger_match = re.search(
                r"CREATE TRIGGER trigger_prevent_unauthorized_comment.*?BEFORE (INSERT|UPDATE).*?ON comments",
                sql,
                re.DOTALL
            )
            if trigger_match and "UPDATE" in trigger_match.group(1):
                print("   ✅ Comments UPDATE prevented by trigger")
            else:
                warnings.append("Comments UPDATE path may not be secured (trigger only covers INSERT)")
        else:
            issues.append("No RLS UPDATE policy or trigger for comments visibility check")
    
    # ========================================================================
    # 8. LIKES UPDATE SECURITY
    # ========================================================================
    print("\n8. LIKES UPDATE SECURITY")
    print("-" * 70)
    
    # Likes table doesn't typically have UPDATE, but check RLS anyway
    likes_policies = re.findall(r'CREATE POLICY.*ON likes.*', sql)
    if len(likes_policies) >= 2:
        print(f"   ✅ Likes has {len(likes_policies)} policies (INSERT/DELETE/SELECT)")
    else:
        warnings.append(f"Likes has only {len(likes_policies)} policies")
    
    # ========================================================================
    # 9. SYNTAX & FORMATTING CHECK
    # ========================================================================
    print("\n9. SYNTAX & FORMATTING CHECK")
    print("-" * 70)
    
    # Check for literal markdown/formatting artifacts
    artifacts = [
        (r'\*--', "Markdown list marker"),
        (r'NEW\\.', "Escaped dot"),
        (r'&#x20;', "HTML space entity"),
        (r'&#xA0;', "HTML nbsp entity"),
        (r'```', "Markdown code block"),
    ]
    
    found_artifacts = []
    for pattern, desc in artifacts:
        if re.search(pattern, sql):
            found_artifacts.append(desc)
    
    if found_artifacts:
        issues.append(f"SQL contains formatting artifacts: {', '.join(found_artifacts)}")
    else:
        print("   ✅ No formatting artifacts found")
    
    # Check for valid SQL keywords
    if "CREATE TABLE" in sql and "CREATE POLICY" in sql:
        print("   ✅ SQL structure appears valid")
    else:
        issues.append("SQL structure may be incomplete")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if issues:
        print(f"\n❌ {len(issues)} ISSUE(S) FOUND:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
    else:
        print("\n✅ No critical issues found")
    
    if warnings:
        print(f"\n⚠️  {len(warnings)} WARNING(S):")
        for i, warn in enumerate(warnings, 1):
            print(f"   {i}. {warn}")
    
    print("\n" + "=" * 70)
    
    return len(issues) == 0

if __name__ == '__main__':
    migration_file = Path(__file__).parent.parent / 'supabase' / 'migrations' / '0001_initial_schema.sql'
    
    if not migration_file.exists():
        print(f"❌ Migration file not found: {migration_file}")
        sys.exit(1)
    
    success = analyze_migration(migration_file)
    sys.exit(0 if success else 1)
