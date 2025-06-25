#!/bin/bash
#
# Environment validation script for Kuwait Social AI deployment
# Checks if the system has all required tools for deployment
#

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Validation results
CHECKS_PASSED=0
CHECKS_FAILED=0
WARNINGS=0

print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}Kuwait Social AI - Environment Validation${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}\n"
}

check_command() {
    local cmd=$1
    local name=$2
    local required=${3:-true}
    
    echo -n "Checking $name... "
    if command -v "$cmd" &> /dev/null; then
        local version=$(eval "$cmd --version 2>/dev/null | head -1" || echo "version unknown")
        echo -e "${GREEN}✓ Found${NC} ($version)"
        ((CHECKS_PASSED++))
        return 0
    else
        if [[ "$required" == "true" ]]; then
            echo -e "${RED}✗ Not found (REQUIRED)${NC}"
            ((CHECKS_FAILED++))
        else
            echo -e "${YELLOW}⚠ Not found (optional)${NC}"
            ((WARNINGS++))
        fi
        return 1
    fi
}

check_doctl_auth() {
    echo -n "Checking DigitalOcean authentication... "
    if doctl auth list &> /dev/null; then
        echo -e "${GREEN}✓ Authenticated${NC}"
        ((CHECKS_PASSED++))
    else
        echo -e "${RED}✗ Not authenticated${NC}"
        echo "  Run: doctl auth init"
        ((CHECKS_FAILED++))
    fi
}

check_ssh_key() {
    echo -n "Checking SSH key... "
    if [[ -f ~/.ssh/id_rsa ]] || [[ -f ~/.ssh/id_ed25519 ]]; then
        echo -e "${GREEN}✓ SSH key found${NC}"
        ((CHECKS_PASSED++))
    else
        echo -e "${YELLOW}⚠ No default SSH key found${NC}"
        echo "  A new key will be created during deployment"
        ((WARNINGS++))
    fi
}

check_network() {
    echo -n "Checking internet connectivity... "
    if curl -s -o /dev/null -w "%{http_code}" https://api.digitalocean.com/v2/ | grep -q "401"; then
        echo -e "${GREEN}✓ Connected${NC}"
        ((CHECKS_PASSED++))
    else
        echo -e "${RED}✗ No connection to DigitalOcean API${NC}"
        ((CHECKS_FAILED++))
    fi
}

check_disk_space() {
    echo -n "Checking disk space... "
    local available=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [[ $available -gt 5 ]]; then
        echo -e "${GREEN}✓ ${available}GB available${NC}"
        ((CHECKS_PASSED++))
    else
        echo -e "${YELLOW}⚠ Only ${available}GB available (5GB recommended)${NC}"
        ((WARNINGS++))
    fi
}

estimate_costs() {
    echo -e "\n${BLUE}Cost Estimation:${NC}"
    echo "────────────────────────────────────"
    echo "Base droplet (s-4vcpu-8gb): $48/month"
    echo "With automated backups: $57.60/month"
    echo "Floating IP: $0/month (when assigned)"
    echo "Bandwidth: 5TB included"
    echo "────────────────────────────────────"
    echo -e "Total: ${GREEN}~$58/month (18 KWD)${NC}"
}

print_header

echo -e "${YELLOW}Checking required tools...${NC}"
check_command "doctl" "DigitalOcean CLI" true
check_command "git" "Git" true
check_command "ssh" "SSH client" true
check_command "openssl" "OpenSSL" true
check_command "curl" "cURL" true

echo -e "\n${YELLOW}Checking optional tools...${NC}"
check_command "docker" "Docker" false
check_command "docker-compose" "Docker Compose" false
check_command "jq" "jq (JSON processor)" false

echo -e "\n${YELLOW}Checking environment...${NC}"
if command -v doctl &> /dev/null; then
    check_doctl_auth
fi
check_ssh_key
check_network
check_disk_space

echo -e "\n${YELLOW}Checking project structure...${NC}"
for dir in scripts configs monitoring docs backup security; do
    echo -n "Checking $dir/ directory... "
    if [[ -d "$dir" ]]; then
        echo -e "${GREEN}✓ Found${NC}"
        ((CHECKS_PASSED++))
    else
        echo -e "${RED}✗ Missing${NC}"
        ((CHECKS_FAILED++))
    fi
done

# Cost estimation
estimate_costs

# Summary
echo -e "\n${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Validation Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Passed: $CHECKS_PASSED${NC}"
echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
echo -e "${RED}Failed: $CHECKS_FAILED${NC}"
echo ""

if [[ $CHECKS_FAILED -eq 0 ]]; then
    echo -e "${GREEN}✅ Environment is ready for deployment!${NC}"
    echo -e "\nNext steps:"
    echo "1. Run: ./scripts/deploy.sh"
    echo "2. Follow the prompts"
    echo "3. Update your DNS records"
    exit 0
else
    echo -e "${RED}❌ Environment is not ready!${NC}"
    echo -e "\nPlease fix the issues above before deploying."
    exit 1
fi