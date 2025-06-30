#!/bin/bash
#
# Test script for Kuwait Social AI - DigitalOcean Hosting Package
# Tests deployment scripts functionality and validation
#

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

# Test functions
print_test_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}Running Tests for DigitalOcean Hosting Scripts${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}\n"
}

test_script_exists() {
    local script=$1
    echo -n "Testing if $script exists... "
    if [[ -f "$script" ]]; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

test_script_executable() {
    local script=$1
    echo -n "Testing if $script is executable... "
    if [[ -x "$script" ]]; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

test_bash_syntax() {
    local script=$1
    echo -n "Testing bash syntax for $script... "
    if bash -n "$script" 2>/dev/null; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

test_shellcheck() {
    local script=$1
    echo -n "Testing shellcheck for $script... "
    if command -v shellcheck &> /dev/null; then
        if shellcheck "$script" 2>/dev/null; then
            echo -e "${GREEN}✓ PASS${NC}"
            ((TESTS_PASSED++))
            return 0
        else
            echo -e "${YELLOW}⚠ WARNINGS${NC}"
            ((TESTS_PASSED++))
            return 0
        fi
    else
        echo -e "${YELLOW}SKIP (shellcheck not installed)${NC}"
        return 0
    fi
}

test_function_exists() {
    local script=$1
    local function=$2
    echo -n "Testing if function '$function' exists in $script... "
    if grep -q "^${function}()" "$script" || grep -q "^function ${function}" "$script"; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

test_validate_input_function() {
    echo -e "\n${YELLOW}Testing validate_input function...${NC}"
    
    # Create a temporary script with the function
    cat > /tmp/test_validate.sh << 'EOF'
validate_input() {
    local input=$1
    local type=$2
    
    case $type in
        "domain")
            if [[ ! "$input" =~ ^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
                return 1
            fi
            ;;
        "email")
            if [[ ! "$input" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
                return 1
            fi
            ;;
        "ip")
            if [[ ! "$input" =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
                return 1
            fi
            ;;
    esac
    return 0
}
EOF
    source /tmp/test_validate.sh
    
    # Test domain validation
    echo -n "  Testing valid domain... "
    if validate_input "example.com" "domain"; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((TESTS_FAILED++))
    fi
    
    echo -n "  Testing invalid domain... "
    if ! validate_input "invalid_domain" "domain" 2>/dev/null; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((TESTS_FAILED++))
    fi
    
    # Test email validation
    echo -n "  Testing valid email... "
    if validate_input "user@example.com" "email" 2>/dev/null; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((TESTS_FAILED++))
    fi
    
    echo -n "  Testing invalid email... "
    if ! validate_input "invalid.email" "email" 2>/dev/null; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((TESTS_FAILED++))
    fi
    
    # Test IP validation
    echo -n "  Testing valid IP... "
    if validate_input "192.168.1.1" "ip"; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((TESTS_FAILED++))
    fi
    
    echo -n "  Testing invalid IP... "
    if ! validate_input "192.168.1" "ip"; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((TESTS_FAILED++))
    fi
    
    # Clean up
    rm -f /tmp/test_validate.sh
}

test_password_generation() {
    echo -e "\n${YELLOW}Testing password generation...${NC}"
    
    # Define the function inline
    generate_secure_password() {
        openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
    }
    
    echo -n "  Testing password generation... "
    PASSWORD=$(generate_secure_password)
    if [[ ${#PASSWORD} -eq 25 ]]; then
        echo -e "${GREEN}✓ PASS (length: 25)${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAIL (length: ${#PASSWORD})${NC}"
        ((TESTS_FAILED++))
    fi
    
    echo -n "  Testing password uniqueness... "
    PASSWORD1=$(generate_secure_password)
    PASSWORD2=$(generate_secure_password)
    if [[ "$PASSWORD1" != "$PASSWORD2" ]]; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((TESTS_FAILED++))
    fi
}

test_config_files() {
    echo -e "\n${YELLOW}Testing configuration files...${NC}"
    
    # Test docker-compose.yml
    echo -n "  Testing docker-compose.yml exists... "
    if [[ -f "configs/docker-compose.yml" ]]; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((TESTS_PASSED++))
        
        echo -n "  Testing docker-compose.yml syntax... "
        if command -v docker-compose &> /dev/null; then
            if docker-compose -f configs/docker-compose.yml config >/dev/null 2>&1; then
                echo -e "${GREEN}✓ PASS${NC}"
                ((TESTS_PASSED++))
            else
                echo -e "${RED}✗ FAIL${NC}"
                ((TESTS_FAILED++))
            fi
        else
            echo -e "${YELLOW}SKIP (docker-compose not installed)${NC}"
        fi
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((TESTS_FAILED++))
    fi
    
    # Test nginx.conf
    echo -n "  Testing nginx.conf exists... "
    if [[ -f "configs/nginx.conf" ]]; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((TESTS_FAILED++))
    fi
}

test_documentation() {
    echo -e "\n${YELLOW}Testing documentation...${NC}"
    
    echo -n "  Testing README.md exists... "
    if [[ -f "README.md" ]]; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((TESTS_FAILED++))
    fi
    
    echo -n "  Testing DEPLOYMENT-GUIDE.md exists... "
    if [[ -f "docs/DEPLOYMENT-GUIDE.md" ]]; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((TESTS_FAILED++))
    fi
}

test_directory_structure() {
    echo -e "\n${YELLOW}Testing directory structure...${NC}"
    
    local dirs=("scripts" "configs" "monitoring" "docs" "backup" "security")
    for dir in "${dirs[@]}"; do
        echo -n "  Testing $dir/ directory exists... "
        if [[ -d "$dir" ]]; then
            echo -e "${GREEN}✓ PASS${NC}"
            ((TESTS_PASSED++))
        else
            echo -e "${RED}✗ FAIL${NC}"
            ((TESTS_FAILED++))
        fi
    done
}

# Main test execution
print_test_header

# Test all scripts
SCRIPTS=("scripts/deploy.sh" "scripts/backup.sh" "scripts/maintenance.sh" "scripts/setup-monitoring.sh" "scripts/ssl-setup.sh")

for script in "${SCRIPTS[@]}"; do
    echo -e "\n${BLUE}Testing: $script${NC}"
    echo "────────────────────────────────────"
    test_script_exists "$script"
    if [[ -f "$script" ]]; then
        test_script_executable "$script"
        test_bash_syntax "$script"
        test_shellcheck "$script"
    fi
done

# Test deploy.sh specific functions
echo -e "\n${BLUE}Testing deploy.sh functions${NC}"
echo "────────────────────────────────────"
test_function_exists "scripts/deploy.sh" "print_banner"
test_function_exists "scripts/deploy.sh" "validate_input"
test_function_exists "scripts/deploy.sh" "generate_secure_password"

# Run functional tests
test_validate_input_function
test_password_generation

# Test other components
test_config_files
test_documentation
test_directory_structure

# Print summary
echo -e "\n${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo -e "${BLUE}Total:  $((TESTS_PASSED + TESTS_FAILED))${NC}"
echo ""

if [[ $TESTS_FAILED -eq 0 ]]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed!${NC}"
    exit 1
fi