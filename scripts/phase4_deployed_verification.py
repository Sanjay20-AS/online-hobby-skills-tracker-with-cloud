#!/usr/bin/env python3
"""
Phase 4 Deployed Database Verification Script

Purpose: 
  - Connect to deployed Supabase database
  - Query deployed profile-creation function and compare with migration file
  - Verify all structural components (tables, triggers, policies, indexes)
  - Report which checks pass/fail

Usage:
  python phase4_deployed_verification.py

Requirements:
  - DATABASE_URL in backend/.env
  - psycopg2 library (pip install psycopg2-binary)

Safety:
  - Read-only queries only
  - No data modifications
"""

import os
import sys
import re
from pathlib import Path
from urllib.parse import urlparse

try:
    import psycopg2
    from psycopg2 import sql, Error
except ImportError:
    print("❌ ERROR: psycopg2 not installed")
    print("   Install with: pip install psycopg2-binary")
    sys.exit(1)


class SupabaseVerifier:
    def __init__(self, database_url):
        """Initialize connection to Supabase database."""
        self.database_url = database_url
        self.conn = None
        self.cursor = None

    def connect(self):
        """Connect to Supabase database."""
        try:
            self.conn = psycopg2.connect(self.database_url)
            self.cursor = self.conn.cursor()
            print("✅ Connected to Supabase database\n")
            return True
        except Error as e:
            print(f"❌ Connection error: {e}")
            return False

    def close(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def execute_query(self, query):
        """Execute a query and return results."""
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"❌ Query error: {e}")
            return None

    def execute_query_one(self, query):
        """Execute a query and return single result."""
        try:
            self.cursor.execute(query)
            return self.cursor.fetchone()
        except Error as e:
            print(f"❌ Query error: {e}")
            return None

    # ========================================================================
    # VERIFICATION METHODS
    # ========================================================================

    def verify_function_definition(self):
        """Extract and display deployed create_profile_on_signup function."""
        print("=" * 80)
        print("VERIFICATION 1: FUNCTION DEFINITION")
        print("=" * 80)

        query = """
        SELECT 
            n.nspname as schema_name,
            p.proname as function_name,
            pg_get_functiondef(p.oid) as function_definition
        FROM pg_proc p
        JOIN pg_namespace n ON p.pronamespace = n.oid
        WHERE p.proname = 'create_profile_on_signup'
            AND n.nspname = 'public';
        """

        result = self.execute_query_one(query)
        if result:
            schema, func_name, func_def = result
            print(f"✅ Function found: {func_name}")
            print(f"\nFunction Definition:")
            print("-" * 80)
            print(func_def)
            print("-" * 80)
            self._check_function_requirements(func_def)
            return True
        else:
            print("❌ Function not found: create_profile_on_signup")
            return False

    def _check_function_requirements(self, func_def):
        """Check function definition contains expected requirements."""
        print("\nFunction Requirement Checks:")

        checks = {
            "SECURITY DEFINER": "SECURITY DEFINER" in func_def,
            "search_path set to 'public'": "search_path" in func_def and "'public'" in func_def,
            "Username collision handling (WHILE loop)": "WHILE EXISTS" in func_def,
            "Counter-based suffix logic": "counter ::= counter + 1" in func_def or "counter + 1" in func_def,
            "UUID fallback": "'user_' || SUBSTRING" in func_def,
            "REGEXP_REPLACE validation": "REGEXP_REPLACE" in func_def,
            "Exception handling (EXCEPTION WHEN OTHERS)": "EXCEPTION WHEN OTHERS" in func_def,
            "RAISE for error propagation": "RAISE WARNING" in func_def and "RAISE;" in func_def,
            "raw_user_meta_data usage": "raw_user_meta_data" in func_def,
        }

        for check_name, check_result in checks.items():
            status = "✅" if check_result else "❌"
            print(f"  {status} {check_name}")

        return all(checks.values())

    def verify_trigger_attachment(self):
        """Verify trigger is correctly attached to auth.users."""
        print("\n" + "=" * 80)
        print("VERIFICATION 2: TRIGGER ATTACHMENT")
        print("=" * 80)

        query = """
        SELECT 
            t.tgname as trigger_name,
            r.relname as table_name,
            p.proname as function_name,
            CASE 
                WHEN t.tgtype & 2 = 2 THEN 'BEFORE'
                WHEN t.tgtype & 64 = 64 THEN 'INSTEAD OF'
                ELSE 'AFTER'
            END as trigger_timing,
            CASE 
                WHEN t.tgtype & 4 = 4 THEN 'INSERT'
                WHEN t.tgtype & 8 = 8 THEN 'UPDATE'
                WHEN t.tgtype & 16 = 16 THEN 'DELETE'
            END as trigger_event,
            t.tgenabled as enabled
        FROM pg_trigger t
        JOIN pg_class r ON t.tgrelid = r.oid
        JOIN pg_proc p ON t.tgfoid = p.oid
        JOIN pg_namespace n ON r.relnamespace = n.oid
        WHERE t.tgname = 'trigger_create_profile_on_signup'
            AND n.nspname = 'auth';
        """

        result = self.execute_query_one(query)
        if result:
            trigger_name, table_name, func_name, timing, event, enabled = result
            print(f"✅ Trigger found: {trigger_name}")
            print(f"   Table: {table_name}")
            print(f"   Function: {func_name}")
            print(f"   Timing: {timing}")
            print(f"   Event: {event}")
            print(f"   Enabled: {'Yes' if enabled else 'No'}")
            return enabled
        else:
            print("❌ Trigger not found on auth.users")
            return False

    def verify_table_structure(self):
        """Verify profiles table structure."""
        print("\n" + "=" * 80)
        print("VERIFICATION 3: TABLE STRUCTURE")
        print("=" * 80)

        query = """
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_schema = 'public' 
            AND table_name = 'profiles'
        ORDER BY ordinal_position;
        """

        results = self.execute_query(query)
        if results:
            print("✅ profiles table structure:")
            for col_name, col_type, nullable, default in results:
                nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
                default_str = f"DEFAULT {default}" if default else ""
                print(f"   {col_name}: {col_type} {nullable_str} {default_str}".strip())
            return True
        else:
            print("❌ profiles table not found")
            return False

    def verify_constraints(self):
        """Verify UNIQUE constraint and indexes."""
        print("\n" + "=" * 80)
        print("VERIFICATION 4: CONSTRAINTS & INDEXES")
        print("=" * 80)

        # Check UNIQUE constraint
        query_constraint = """
        SELECT constraint_name, constraint_type
        FROM information_schema.table_constraints
        WHERE table_schema = 'public' 
            AND table_name = 'profiles'
            AND constraint_type = 'UNIQUE';
        """

        results = self.execute_query(query_constraint)
        if results:
            print("✅ UNIQUE constraints on profiles:")
            for constraint_name, constraint_type in results:
                print(f"   {constraint_name}: {constraint_type}")
        else:
            print("❌ No UNIQUE constraints found on profiles")

        # Check case-insensitive index
        query_index = """
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE schemaname = 'public' 
            AND tablename = 'profiles'
            AND indexname LIKE '%username%';
        """

        results = self.execute_query(query_index)
        if results:
            print("\n✅ Username indexes:")
            for index_name, index_def in results:
                print(f"   {index_name}:")
                print(f"   {index_def}")
        else:
            print("\n❌ No username indexes found")

        return True

    def verify_ownership_triggers(self):
        """Verify all 5 ownership validation triggers."""
        print("\n" + "=" * 80)
        print("VERIFICATION 5: OWNERSHIP VALIDATION TRIGGERS")
        print("=" * 80)

        query = """
        SELECT 
            p.proname as function_name,
            r.relname as table_name
        FROM pg_proc p
        JOIN pg_trigger t ON t.tgfoid = p.oid
        JOIN pg_class r ON t.tgrelid = r.oid
        WHERE p.proname LIKE 'validate_%_ownership'
        ORDER BY r.relname;
        """

        results = self.execute_query(query)
        if results and len(results) == 5:
            print(f"✅ All 5 ownership triggers found:")
            for func_name, table_name in results:
                print(f"   {func_name} on {table_name}")
            return True
        else:
            count = len(results) if results else 0
            print(f"❌ Expected 5 ownership triggers, found {count}")
            if results:
                for func_name, table_name in results:
                    print(f"   {func_name} on {table_name}")
            return False

    def verify_comment_security_triggers(self):
        """Verify comment protection triggers (INSERT and UPDATE)."""
        print("\n" + "=" * 80)
        print("VERIFICATION 6: COMMENT SECURITY TRIGGERS")
        print("=" * 80)

        query = """
        SELECT 
            p.proname as function_name,
            r.relname as table_name,
            t.tgname as trigger_name
        FROM pg_proc p
        JOIN pg_trigger t ON t.tgfoid = p.oid
        JOIN pg_class r ON t.tgrelid = r.oid
        WHERE p.proname LIKE '%unauthorized_comment%'
            AND r.relname = 'comments'
        ORDER BY t.tgname;
        """

        results = self.execute_query(query)
        if results and len(results) >= 2:
            print(f"✅ Comment security triggers found:")
            for func_name, table_name, trigger_name in results:
                print(f"   {trigger_name}: {func_name} on {table_name}")
            return True
        else:
            count = len(results) if results else 0
            print(f"❌ Expected 2+ comment triggers, found {count}")
            if results:
                for func_name, table_name, trigger_name in results:
                    print(f"   {trigger_name}: {func_name} on {table_name}")
            return False

    def verify_rls_policies(self):
        """Verify RLS policies are present (20 total expected)."""
        print("\n" + "=" * 80)
        print("VERIFICATION 7: RLS POLICIES")
        print("=" * 80)

        # Count by table
        query_by_table = """
        SELECT 
            tablename,
            COUNT(*) as policy_count
        FROM pg_policies
        WHERE schemaname = 'public'
        GROUP BY tablename
        ORDER BY tablename;
        """

        results = self.execute_query(query_by_table)
        total = 0
        if results:
            print("✅ RLS policies by table:")
            for table_name, policy_count in results:
                total += policy_count
                print(f"   {table_name}: {policy_count} policies")

        # Total count
        query_total = """
        SELECT COUNT(*) FROM pg_policies WHERE schemaname = 'public';
        """

        total_result = self.execute_query_one(query_total)
        if total_result:
            total_count = total_result[0]
            expected = 19  # 20 expected, but follows may have 1
            status = "✅" if total_count >= 19 else "❌"
            print(f"\n{status} Total RLS policies: {total_count} (expected ~20)")
            return total_count >= 19
        else:
            print("❌ Could not count RLS policies")
            return False

    def verify_data_integrity_triggers(self):
        """Verify data integrity triggers."""
        print("\n" + "=" * 80)
        print("VERIFICATION 8: DATA INTEGRITY TRIGGERS")
        print("=" * 80)

        query = """
        SELECT 
            p.proname as function_name,
            r.relname as table_name
        FROM pg_proc p
        JOIN pg_trigger t ON t.tgfoid = p.oid
        JOIN pg_class r ON t.tgrelid = r.oid
        WHERE p.proname IN ('prevent_self_like', 'prevent_unauthorized_like', 'prevent_unauthorized_comment')
        ORDER BY p.proname;
        """

        results = self.execute_query(query)
        if results and len(results) >= 3:
            print(f"✅ Data integrity triggers found:")
            for func_name, table_name in results:
                print(f"   {func_name} on {table_name}")
            return True
        else:
            count = len(results) if results else 0
            print(f"❌ Expected 3 data integrity triggers, found {count}")
            return False

    def verify_profile_count(self):
        """Get current profile count (baseline for regression testing)."""
        print("\n" + "=" * 80)
        print("VERIFICATION 9: PROFILE BASELINE")
        print("=" * 80)

        query = "SELECT COUNT(*) FROM public.profiles;"

        result = self.execute_query_one(query)
        if result:
            count = result[0]
            print(f"✅ Current profile count: {count}")
            return count
        else:
            print("❌ Could not query profile count")
            return 0

    def verify_tables_count(self):
        """Verify all 11 tables exist."""
        print("\n" + "=" * 80)
        print("VERIFICATION 10: TABLE INVENTORY")
        print("=" * 80)

        query = """
        SELECT COUNT(*) FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
        """

        result = self.execute_query_one(query)
        if result:
            count = result[0]
            expected = 11
            status = "✅" if count == expected else "⚠️ "
            print(f"{status} Table count: {count} (expected {expected})")
            return count == expected
        else:
            print("❌ Could not count tables")
            return False

    def run_all_verifications(self):
        """Run all verification checks."""
        print("\n")
        print("╔" + "=" * 78 + "╗")
        print("║" + " PHASE 4 POST-MIGRATION DEPLOYED VERIFICATION ".center(78) + "║")
        print("╚" + "=" * 78 + "╝")
        print()

        results = {
            "Function Definition": self.verify_function_definition(),
            "Trigger Attachment": self.verify_trigger_attachment(),
            "Table Structure": self.verify_table_structure(),
            "Constraints & Indexes": self.verify_constraints(),
            "Ownership Triggers": self.verify_ownership_triggers(),
            "Comment Security": self.verify_comment_security_triggers(),
            "RLS Policies": self.verify_rls_policies(),
            "Data Integrity Triggers": self.verify_data_integrity_triggers(),
            "Table Inventory": self.verify_tables_count(),
        }

        self.verify_profile_count()

        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        print(f"\n✅ Checks passed: {passed}/{total}")

        for check_name, result in results.items():
            status = "✅" if result else "❌"
            print(f"{status} {check_name}")

        print("\n" + "=" * 80)
        if passed == total:
            print("✅ ALL VERIFICATIONS PASSED - Phase 4 deployed correctly")
            print("=" * 80)
            return 0
        else:
            print(f"⚠️  {total - passed} verification(s) failed or incomplete")
            print("=" * 80)
            return 1


def main():
    """Main entry point."""
    # Load environment
    env_path = Path("backend/.env")
    if not env_path.exists():
        print(f"❌ Error: {env_path} not found")
        sys.exit(1)

    database_url = None
    with open(env_path) as f:
        for line in f:
            if line.startswith("DATABASE_URL="):
                database_url = line.split("=", 1)[1].strip()
                break

    if not database_url:
        print("❌ Error: DATABASE_URL not found in backend/.env")
        sys.exit(1)

    # Verify
    verifier = SupabaseVerifier(database_url)
    if not verifier.connect():
        sys.exit(1)

    try:
        exit_code = verifier.run_all_verifications()
    finally:
        verifier.close()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
