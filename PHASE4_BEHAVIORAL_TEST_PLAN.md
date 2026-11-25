# Phase 4 Behavioral Testing Plan — Concise Summary

**Status:** Ready for Approval  
**Risk Level:** 🟢 LOW (synthetic accounts only, non-destructive)  
**Timeline:** ~17 minutes total

---

## Six Tests Classified

| # | Test | Type | Creates Users | Creates Data | Approval? |
|---|------|------|---|---|---|
| 1 | Auto Profile Creation | SQL verify | ✅ 1 | 🟢 Auto | ✅ YES |
| 2 | Username Uniqueness | SQL verify | ✅ 1 | 🟢 Auto | ✅ YES |
| 3 | Ownership Triggers | SQL insert | — | ✅ 1-2 | ✅ YES |
| 4 | Comment Security | SQL insert/update | — | ✅ 2-3 | ✅ YES |
| 5 | RLS Isolation | API query | — | ✅ 2 | ✅ YES |
| 6 | Error Handling | SQL verify | ✅ 1 | 🟢 Auto | ✅ YES |

---

## Synthetic Accounts Required

```
Email: test.user.a@example.com | Password: TestPass123! | Purpose: Profile + ownership
Email: test.user.b@example.com | Password: TestPass123! | Purpose: RLS + unauthorized
Email: test.user.c@example.com | Password: TestPass123! | Purpose: Optional extra
```

**All accounts deleted after testing (cascading delete removes all test data)**

---

## Data That Will Be Created

| Table | Records | Owned By | Cleanup |
|-------|---------|----------|---------|
| profiles | 3 | Test users | ✅ Cascade delete |
| hobbies | 1-2 | Test users | ✅ Cascade delete |
| posts | 1 | TEST USER_A | ✅ Cascade delete |
| comments | 1-2 | Test users | ✅ Cascade delete |
| skills | 1 | Test users | ✅ Cascade delete |

**Total: ~15 temporary records. All removed when accounts deleted.**

---

## Tests Safe to Run WITHOUT Approval

### ✅ Read-Only Verification (Anytime)

```sql
-- Verify trigger definitions (no data changes)
SELECT pg_get_triggerdef(t.oid) FROM pg_trigger t WHERE tgname LIKE 'trigger_%';

-- Verify RLS policies exist
SELECT policyname FROM pg_policies WHERE tablename = 'profiles';

-- Verify UNIQUE constraint
SELECT constraint_name FROM information_schema.table_constraints 
WHERE table_name = 'profiles' AND constraint_type = 'UNIQUE';
```

**These are inspection-only, safe to run anytime.**

---

## Tests Requiring EXPLICIT Approval

🔴 **ALL 6 behavioral tests require approval because they:**
- Create synthetic test users (even if temporary)
- Modify database records (even if temporary)
- Require cleanup operations

---

## Production Data Risks: 🟢 LOW

**Why:**
- Test accounts isolated by email pattern (test.user.*)
- All data temporary and marked for deletion
- Cascading deletes remove everything
- No schema or trigger modifications
- No production user data touched

**Mitigation:**
- Pre-test record count baseline
- Explicit cleanup procedure
- Post-cleanup verification
- All test emails use "test.user" pattern

---

## Execution Steps (If Approved)

### Phase 1: Create Test Users (2 min)
- Create test.user.a@example.com via Supabase Auth console
- Create test.user.b@example.com via Supabase Auth console
- Wait 2 seconds for profile auto-creation trigger

### Phase 2: Run Tests 1-2 (3 min)
- Verify profiles auto-created (Test 1)
- Verify unique usernames (Test 2)

### Phase 3: Run Tests 3-7 (10 min)
- Create test data (hobbies, posts, comments, skills)
- Run ownership trigger tests (block cross-user creates)
- Run comment security tests (block unauthorized operations)
- Run RLS isolation test (verify data filtering)
- Run error handling test (verify trigger errors propagate)

### Phase 4: Cleanup (2 min)
- Delete test.user.a@example.com from Supabase Auth
- Delete test.user.b@example.com from Supabase Auth
- Verify cascading deletes removed all test data
- Verify record counts match baseline

---

## Expected Outcomes

| Test | Expected | Result |
|------|----------|--------|
| 1 | Profile auto-created with username | ✅ PASS |
| 2 | Different usernames (uniqueness works) | ✅ PASS |
| 3 | Ownership trigger blocks cross-user skill | ✅ PASS |
| 4A | Comment INSERT blocked on private post | ✅ PASS |
| 4B | Comment UPDATE blocked on private post | ✅ PASS |
| 5 | RLS filters USER_B's view of data | ✅ PASS |
| 6 | Error logs show profile creation flow | ✅ PASS |

**If all pass: Phase 4 behavioral verification complete ✅**

---

## Important Notes

### RLS Testing (Test 5)

**Cannot use SQL Editor admin connection** — It bypasses RLS (admin context)

**Must use:**
- Backend API with USER_B JWT token, OR
- Supabase CLI with USER_B JWT, OR
- Browser app login as USER_B

**Purpose:** Verify RLS actually filters data for non-admin users

### Ownership Trigger Tests (Tests 3, 6)

**Expected to FAIL (by design):**
- Cross-user inserts will raise exceptions
- Error messages show trigger is working
- No data is inserted
- ✅ This is PASS result

---

## What I Need From You

**Choose one:**

1. **"Approve Phase 4 behavioral testing plan"**
   - I will create test users
   - Run all 6 tests
   - Delete test accounts
   - Report final results
   
2. **"Approve with modifications"** + specify changes
   - I will adjust and re-plan
   
3. **"Do not approve"**
   - No test data will be created
   
4. **"Approve only Tests 1,2,5"** (specify which)
   - I will run only selected tests

**Default:** No tests execute without approval.

---

## See Also

- **Full Detailed Plan:** Artifact "Phase 4 Behavioral Testing — Execution Plan & Classification"
- **Test Procedures:** `scripts/PHASE4_TEST_PLAN.md`
- **Trigger Verification:** `scripts/TRIGGER_VERIFICATION_QUERIES.md`

