#!/bin/bash
# Validation script for Hybrid Likes System implementation

echo "========================================================"
echo "HYBRID LIKES SYSTEM - IMPLEMENTATION VALIDATION"
echo "========================================================"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0

# Function to check file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅ PASS${NC} - $2"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} - $2 (file not found: $1)"
        ((FAILED++))
        return 1
    fi
}

# Function to check content in file
check_content() {
    if grep -q "$2" "$1" 2>/dev/null; then
        echo -e "${GREEN}✅ PASS${NC} - $3"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} - $3"
        ((FAILED++))
        return 1
    fi
}

# Function to count occurrences
count_content() {
    count=$(grep -c "$2" "$1" 2>/dev/null || echo "0")
    echo -e "${YELLOW}ℹ INFO${NC} - $3: $count"
}

echo ""
echo "Phase 1: Critical Bug Fix"
echo "----------------------------------------"
check_file "freefire/get_jwt.py" "get_jwt.py exists"
check_content "freefire/get_jwt.py" "https://loginbp.ggblueshark.com/MajorLogin" "get_jwt.py uses correct URL (not localhost)"
count_content "freefire/get_jwt.py" "localhost:8001" "Localhost references remaining"

echo ""
echo "Phase 2: Guest Likes Engine"
echo "----------------------------------------"
check_file "freefire/guest_likes_engine.py" "guest_likes_engine.py created"
check_content "freefire/guest_likes_engine.py" "send_likes_with_guests" "Main function send_likes_with_guests exists"
check_content "freefire/guest_likes_engine.py" "get_available_guests" "Helper function get_available_guests exists"
check_content "freefire/guest_likes_engine.py" "guest_usage_by_target.json" "Usage tracking with correct JSON file"
check_content "freefire/guest_likes_engine.py" "asyncio.Semaphore" "Concurrency control implemented"
check_file "freefire/guests_manager/guests_converted.json" "Guest accounts file exists"

# Count guest accounts
if [ -f "freefire/guests_manager/guests_converted.json" ]; then
    GUEST_COUNT=$(python3 -c "import json; print(len(json.load(open('freefire/guests_manager/guests_converted.json'))))" 2>/dev/null || echo "?")
    echo -e "${YELLOW}ℹ INFO${NC} - Total guest accounts available: $GUEST_COUNT"
fi

echo ""
echo "Phase 3: Hybrid Handler"
echo "----------------------------------------"
check_file "handlers/likes_hybrid.py" "likes_hybrid.py created"
check_content "handlers/likes_hybrid.py" "likes_hybrid_handler" "Main handler function exists"
check_content "handlers/likes_hybrid.py" "send_likes_with_guests" "Imports guest engine"
check_content "handlers/likes_hybrid.py" "send_likes_hl_gaming" "Imports HL Gaming fallback"
check_content "handlers/likes_hybrid.py" "@check_banned" "Uses check_banned decorator"
check_content "handlers/likes_hybrid.py" "@user_exists" "Uses user_exists decorator"
check_content "handlers/likes_hybrid.py" "method_used" "Tracks which method was used"
check_content "handlers/likes_hybrid.py" "Guest Accounts (Free)" "Guest success message"
check_content "handlers/likes_hybrid.py" "HL Gaming Premium" "HL Gaming fallback message"

echo ""
echo "Phase 4: Bot Registration"
echo "----------------------------------------"
check_file "bot.py" "bot.py exists"
check_content "bot.py" "from handlers.likes_hybrid import likes_hybrid_handler" "Hybrid handler imported"
check_content "bot.py" "CommandHandler.*likes.*likes_hybrid_handler" "Hybrid handler registered for /likes command"

# Check if old handler is removed
if grep -q "from handlers.likes_hl_gaming import likes_hl_gaming_handler" "bot.py" 2>/dev/null; then
    echo -e "${YELLOW}⚠ WARN${NC} - Old HL Gaming handler import still present (may cause confusion)"
fi

echo ""
echo "Additional Checks"
echo "----------------------------------------"
check_file "freefire/encrypt_like_body.py" "encrypt_like_body.py exists (required by guest engine)"
check_file "freefire/ff_proto/send_like_pb2.py" "send_like_pb2.py exists (protobuf definitions)"
check_file "freefire/hl_gaming_likes_api.py" "HL Gaming API exists (fallback)"

# Check for usage_history directory
if [ -d "usage_history" ]; then
    echo -e "${GREEN}✅ PASS${NC} - usage_history directory exists"
    ((PASSED++))
else
    echo -e "${YELLOW}ℹ INFO${NC} - usage_history directory will be created on first run"
fi

# Syntax check
echo ""
echo "Syntax Validation"
echo "----------------------------------------"
if python3 -m py_compile freefire/guest_likes_engine.py 2>/dev/null; then
    echo -e "${GREEN}✅ PASS${NC} - guest_likes_engine.py syntax valid"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} - guest_likes_engine.py syntax error"
    ((FAILED++))
fi

if python3 -m py_compile handlers/likes_hybrid.py 2>/dev/null; then
    echo -e "${GREEN}✅ PASS${NC} - likes_hybrid.py syntax valid"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} - likes_hybrid.py syntax error"
    ((FAILED++))
fi

if python3 -m py_compile bot.py 2>/dev/null; then
    echo -e "${GREEN}✅ PASS${NC} - bot.py syntax valid"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} - bot.py syntax error"
    ((FAILED++))
fi

# Summary
echo ""
echo "========================================================"
echo "VALIDATION SUMMARY"
echo "========================================================"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 ALL VALIDATIONS PASSED!${NC}"
    echo ""
    echo "Implementation Status:"
    echo "  ✅ Phase 1: Critical bug fix complete"
    echo "  ✅ Phase 2: Guest likes engine implemented"
    echo "  ✅ Phase 3: Hybrid handler created"
    echo "  ✅ Phase 4: Bot registration updated"
    echo ""
    echo "Next Steps:"
    echo "  1. Deploy to Railway/production"
    echo "  2. Test with /likes command in Telegram"
    echo "  3. Monitor logs for guest/fallback behavior"
    echo ""
    echo "Expected Behavior:"
    echo "  • First ~161 likes/target: Guest accounts (FREE)"
    echo "  • After exhaustion: HL Gaming fallback (PREMIUM)"
    echo "  • Smart automatic switching"
    exit 0
else
    echo ""
    echo -e "${RED}⚠️  SOME VALIDATIONS FAILED${NC}"
    echo "Please review the errors above"
    exit 1
fi
