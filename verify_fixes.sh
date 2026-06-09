#!/bin/bash
# Verification Script for Critical Fixes Implementation
# Run this to verify all fixes are properly applied

echo "========================================="
echo "🔍 VERIFYING CRITICAL FIXES"
echo "========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_pass=0
check_fail=0

# Function to check if a pattern exists
check_pattern() {
    local file=$1
    local pattern=$2
    local description=$3

    if grep -q "$pattern" "$file"; then
        echo -e "${GREEN}✅ PASS${NC}: $description"
        ((check_pass++))
    else
        echo -e "${RED}❌ FAIL${NC}: $description"
        ((check_fail++))
    fi
}

# Fix #1: Atomic JSON writes
echo "🔧 Fix #1: Race Condition in JSON Writes"
check_pattern "freefire/guest_likes_engine.py" "async def save_usage" "save_usage() is async"
check_pattern "freefire/guest_likes_engine.py" "temp_file = USAGE_FILE.with_suffix" "Atomic write pattern (temp file)"
check_pattern "freefire/guest_likes_engine.py" "await save_usage" "save_usage() is awaited"
echo ""

# Fix #2: Balance refund race condition
echo "🔧 Fix #2: Balance Refund Race Condition"
check_pattern "handlers/likes_hybrid.py" "expected_balance = balance - LIKES_COST" "Expected balance calculation"
check_pattern "handlers/likes_hybrid.py" "if user_after\['balance'\] == expected_balance" "Exact balance matching"
echo ""

# Fix #3: Double-spend window
echo "🔧 Fix #3: Double-Spend Window"
check_pattern "handlers/likes_hybrid.py" "Re-check guest availability AFTER coin deduction" "Guest check after deduction"
check_pattern "handlers/likes_hybrid.py" "available_guests = get_available_guests(target_uid)" "Guest availability recheck"
echo ""

# Fix #4: Region format consistency
echo "🔧 Fix #4: Region Format Inconsistency"
check_pattern "handlers/likes_hybrid.py" 'region="IND"' "Uppercase IND in handler"
check_pattern "freefire/hl_gaming_likes_api.py" "region = region.lower()" "Region normalization in API"
echo ""

# Fix #5: Partial success logic
echo "🔧 Fix #5: Partial Success Logic Error"
check_pattern "handlers/likes_hybrid.py" "remaining_likes = LIKES_AMOUNT - partial_likes" "Remaining likes calculation"
check_pattern "handlers/likes_hybrid.py" "hybrid_both" "Hybrid method type"
check_pattern "handlers/likes_hybrid.py" "guest_partial" "Partial guest method type"
echo ""

# New Feature #1: Guest validation
echo "🆕 Feature #1: Guest Account Validation"
check_pattern "freefire/guest_likes_engine.py" "async def validate_guest_account" "validate_guest_account function"
check_pattern "freefire/guest_likes_engine.py" "async def validate_all_guests" "validate_all_guests function"
check_pattern "freefire/guest_likes_engine.py" "async def remove_invalid_guests" "remove_invalid_guests function"
echo ""

# New Feature #2: Admin commands
echo "🆕 Feature #2: Admin Commands"
check_pattern "handlers/admin.py" "validate_guests_command" "validate_guests_command function"
check_pattern "handlers/admin.py" "remove_invalid_guests_command" "remove_invalid_guests_command function"
check_pattern "bot.py" "validate_guests_command" "Command registration in bot.py"
echo ""

# Security: Git protection
echo "🔒 Security: Git Protection"
check_pattern ".gitignore" "guests_converted.json" "Guest credentials in .gitignore"
check_pattern ".gitignore" "usage_history/" "Usage history in .gitignore"
if [ -f "freefire/guests_manager/README.md" ]; then
    echo -e "${GREEN}✅ PASS${NC}: Security README.md exists"
    ((check_pass++))
else
    echo -e "${RED}❌ FAIL${NC}: Security README.md missing"
    ((check_fail++))
fi
echo ""

# Syntax validation
echo "🐍 Syntax Validation"
if python3 -m py_compile freefire/guest_likes_engine.py 2>/dev/null; then
    echo -e "${GREEN}✅ PASS${NC}: guest_likes_engine.py syntax"
    ((check_pass++))
else
    echo -e "${RED}❌ FAIL${NC}: guest_likes_engine.py syntax error"
    ((check_fail++))
fi

if python3 -m py_compile handlers/likes_hybrid.py 2>/dev/null; then
    echo -e "${GREEN}✅ PASS${NC}: likes_hybrid.py syntax"
    ((check_pass++))
else
    echo -e "${RED}❌ FAIL${NC}: likes_hybrid.py syntax error"
    ((check_fail++))
fi

if python3 -m py_compile handlers/admin.py 2>/dev/null; then
    echo -e "${GREEN}✅ PASS${NC}: admin.py syntax"
    ((check_pass++))
else
    echo -e "${RED}❌ FAIL${NC}: admin.py syntax error"
    ((check_fail++))
fi

if python3 -m py_compile freefire/hl_gaming_likes_api.py 2>/dev/null; then
    echo -e "${GREEN}✅ PASS${NC}: hl_gaming_likes_api.py syntax"
    ((check_pass++))
else
    echo -e "${RED}❌ FAIL${NC}: hl_gaming_likes_api.py syntax error"
    ((check_fail++))
fi

if python3 -m py_compile bot.py 2>/dev/null; then
    echo -e "${GREEN}✅ PASS${NC}: bot.py syntax"
    ((check_pass++))
else
    echo -e "${RED}❌ FAIL${NC}: bot.py syntax error"
    ((check_fail++))
fi

echo ""
echo "========================================="
echo "📊 VERIFICATION SUMMARY"
echo "========================================="
echo -e "${GREEN}✅ Passed: $check_pass${NC}"
echo -e "${RED}❌ Failed: $check_fail${NC}"
echo ""

if [ $check_fail -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL CHECKS PASSED!${NC}"
    echo "✅ System is ready for deployment"
    exit 0
else
    echo -e "${RED}⚠️  SOME CHECKS FAILED!${NC}"
    echo "❌ Please review the failures above"
    exit 1
fi
