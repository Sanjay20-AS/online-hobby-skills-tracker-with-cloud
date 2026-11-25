#!/usr/bin/env python
"""
Validate SQL migration structure without executing against remote database.
Performs syntax checks, counts components, and verifies referential integrity.
"""
import re
import sys
from pathlib import Path

def validate_migration(filepath):
    """Validate migration file structure."""
    with open(filepath, 'r') as f:
        sql = f.read()
    
    print(f"=== Migration Validation: {Path(filepath).name} ===\n")
    
    errors = []
    warnings = []
    
    # 1. Component counts
    tables = len(re.findall(r'CREATE TABLE IF NOT EXISTS', sql))
    policies = len(re.findall(r'CREATE POLICY', sql))
    triggers = len(re.findall(r'CREATE.*TRIGGER', sql))
    indexes = len(re.findall(r'CREATE.*INDEX', sql))
    functions = len(re.findall(r'CREATE OR REPLACE FUNCTION', sql))
    
    print(f"Components:")
    print(f"  Tables: {tables}")
    print(f"  Policies: {policies}")
    print(f"  Triggers: {triggers}")
    print(f"  Indexes: {indexes}")
    print(f"  Functions: {functions}")
    
    if tables != 11:
        errors.append(f"Expected 11 tables, found {tables}")
    
    if policies < 10:
        errors.append(f"Expected 10+ policies, found {policies}")
    
    if functions < 2:
        warnings.append(f"Expected 2+ functions, found {functions}")
    
    # 2. Table names
    print(f"\nExpected tables:")
    expected_tables = [
        'profiles', 'hobbies', 'skills', 'goals', 'practice_sessions',
        'milestones', 'uploads', 'posts', 'likes', 'comments', 'follows'
    ]
    
    for table in expected_tables:
        if f'CREATE TABLE IF NOT EXISTS {table}' in sql:
            print(f"  ✅ {table}")
        else:
            print(f"  ❌ {table}")
            errors.append(f"Table '{table}' not found")
    
    # 3. RLS enabled
    print(f"\nRLS tables:")
    rls_tables = len(re.findall(r'ALTER TABLE.*ENABLE ROW LEVEL SECURITY', sql))
    print(f"  RLS enabled on {rls_tables} tables")
    if rls_tables != 11:
        warnings.append(f"Expected RLS on 11 tables, found {rls_tables}")
    
    # 4. Foreign key references to auth.users
    auth_refs = len(re.findall(r'REFERENCES auth\.users', sql))
    print(f"\nauth.users references: {auth_refs}")
    if auth_refs < 7:  # At least profiles, hobbies, skills, goals, practice_sessions, posts, etc.
        warnings.append(f"Low auth.users references ({auth_refs})")
    
    # 5. Unique constraints
    unique_constraints = len(re.findall(r'UNIQUE', sql))
    print(f"Unique constraints: {unique_constraints}")
    if unique_constraints < 5:
        warnings.append(f"Low unique constraints ({unique_constraints})")
    
    # 6. CHECK constraints
    check_constraints = len(re.findall(r'CHECK\s*\(', sql))
    print(f"Check constraints: {check_constraints}")
    if check_constraints < 10:
        warnings.append(f"Low check constraints ({check_constraints})")
    
    # 7. Bracket balance
    print(f"\nSyntax check:")
    open_parens = sql.count('(')
    close_parens = sql.count(')')
    print(f"  Parentheses: {open_parens} open, {close_parens} close")
    if open_parens != close_parens:
        errors.append(f"Parentheses mismatch: {open_parens} open vs {close_parens} close")
    else:
        print(f"  ✅ Balanced")
    
    # 8. Critical keywords
    print(f"\nCritical components:")
    keywords = [
        ('CREATE TABLE', 'Table definitions'),
        ('ENABLE ROW LEVEL SECURITY', 'RLS activation'),
        ('CREATE POLICY', 'RLS policies'),
        ('REFERENCES auth.users', 'Auth integration'),
        ('CREATE.*TRIGGER', 'Triggers for automation'),
    ]
    
    for pattern, desc in keywords:
        if re.search(pattern, sql):
            print(f"  ✅ {desc}")
        else:
            print(f"  ❌ {desc}")
            errors.append(f"Missing: {desc}")
    
    # 9. Dangerous keywords (should not be present)
    print(f"\nSafety checks:")
    dangerous = ['DROP TABLE', 'TRUNCATE', 'DELETE FROM', 'ALTER TABLE.*DROP']
    found_dangerous = []
    for pattern in dangerous:
        if re.search(pattern, sql, re.IGNORECASE):
            found_dangerous.append(pattern)
    
    if found_dangerous:
        warnings.append(f"Found potentially destructive patterns: {', '.join(found_dangerous)}")
        print(f"  ⚠️  Destructive patterns found (expected in rollback section)")
    else:
        print(f"  ✅ No destructive patterns in main migration")
    
    # Summary
    print(f"\n{'='*50}")
    if errors:
        print(f"❌ {len(errors)} error(s) found:")
        for err in errors:
            print(f"   - {err}")
        return False
    elif warnings:
        print(f"⚠️  {len(warnings)} warning(s) found:")
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
    
    success = validate_migration(migration_file)
    sys.exit(0 if success else 1)
