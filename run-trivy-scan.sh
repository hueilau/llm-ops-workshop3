#!/bin/bash

# Trivy Security Scanner Script for Local Development
# Comprehensive security scanning for the LLMOps pipeline

set -e

echo "🛡️  Trivy Security Scanner for LLMOps Pipeline"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Trivy is installed
if ! command -v trivy &> /dev/null; then
    echo -e "${YELLOW}⚠️  Trivy not found. Installing...${NC}"
    
    # Install Trivy based on OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install trivy
        else
            echo -e "${RED}❌ Please install Homebrew first or install Trivy manually${NC}"
            echo "   Visit: https://aquasecurity.github.io/trivy/latest/getting-started/installation/"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo apt-get update
        sudo apt-get install wget apt-transport-https gnupg lsb-release
        wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
        echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
        sudo apt-get update
        sudo apt-get install trivy
    else
        echo -e "${RED}❌ Unsupported OS. Please install Trivy manually${NC}"
        echo "   Visit: https://aquasecurity.github.io/trivy/latest/getting-started/installation/"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Trivy is installed${NC}"
trivy --version

# Create reports directory
mkdir -p ./security-reports
cd ./security-reports

echo ""
echo -e "${BLUE}🔍 Running comprehensive security scans...${NC}"

# 1. Filesystem vulnerability scan
echo -e "${BLUE}📁 Scanning filesystem for vulnerabilities...${NC}"
trivy fs --config ../trivy.yaml --format table --output fs-vulnerabilities.txt .. || true
trivy fs --config ../trivy.yaml --format json --output fs-vulnerabilities.json .. || true

# 2. Configuration scan (Docker, K8s, etc.)
echo -e "${BLUE}⚙️  Scanning configuration files...${NC}"
trivy config --format table --output config-issues.txt .. || true
trivy config --format json --output config-issues.json .. || true

# 3. Secret scan
echo -e "${BLUE}🔐 Scanning for exposed secrets...${NC}"
trivy fs --scanners secret --format table --output secrets-scan.txt .. || true
trivy fs --scanners secret --format json --output secrets-scan.json .. || true

# 4. Docker image scan (if image exists)
IMAGE_NAME="hueilau/llm-ops-workshop3:latest"
if docker image inspect $IMAGE_NAME &> /dev/null; then
    echo -e "${BLUE}🐳 Scanning Docker image: $IMAGE_NAME${NC}"
    trivy image --format table --output docker-vulnerabilities.txt $IMAGE_NAME || true
    trivy image --format json --output docker-vulnerabilities.json $IMAGE_NAME || true
else
    echo -e "${YELLOW}⚠️  Docker image $IMAGE_NAME not found locally. Build it first with:${NC}"
    echo "   docker build -t $IMAGE_NAME ."
fi

# 5. License scan
echo -e "${BLUE}📄 Scanning licenses...${NC}"
trivy fs --scanners license --format table --output license-scan.txt .. || true

echo ""
echo -e "${GREEN}🎉 Security scanning completed!${NC}"
echo -e "${BLUE}📊 Reports generated in ./security-reports/:${NC}"

# Display summary
echo ""
echo "📋 SCAN SUMMARY"
echo "==============="

if [[ -f fs-vulnerabilities.txt ]]; then
    CRITICAL_FS=$(grep -c "CRITICAL" fs-vulnerabilities.txt || echo "0")
    HIGH_FS=$(grep -c "HIGH" fs-vulnerabilities.txt || echo "0")
    echo -e "📁 Filesystem: ${RED}$CRITICAL_FS Critical${NC}, ${YELLOW}$HIGH_FS High${NC}"
fi

if [[ -f config-issues.txt ]]; then
    CRITICAL_CONFIG=$(grep -c "CRITICAL" config-issues.txt || echo "0")
    HIGH_CONFIG=$(grep -c "HIGH" config-issues.txt || echo "0")
    echo -e "⚙️  Configuration: ${RED}$CRITICAL_CONFIG Critical${NC}, ${YELLOW}$HIGH_CONFIG High${NC}"
fi

if [[ -f secrets-scan.txt ]]; then
    SECRETS_FOUND=$(grep -c "SECRET" secrets-scan.txt || echo "0")
    if [[ $SECRETS_FOUND -gt 0 ]]; then
        echo -e "🔐 Secrets: ${RED}$SECRETS_FOUND Found${NC}"
    else
        echo -e "🔐 Secrets: ${GREEN}None Found${NC}"
    fi
fi

if [[ -f docker-vulnerabilities.txt ]]; then
    CRITICAL_DOCKER=$(grep -c "CRITICAL" docker-vulnerabilities.txt || echo "0")
    HIGH_DOCKER=$(grep -c "HIGH" docker-vulnerabilities.txt || echo "0")
    echo -e "🐳 Docker Image: ${RED}$CRITICAL_DOCKER Critical${NC}, ${YELLOW}$HIGH_DOCKER High${NC}"
fi

echo ""
echo -e "${BLUE}📖 Detailed reports:${NC}"
ls -la *.txt *.json 2>/dev/null || echo "No report files generated"

echo ""
echo -e "${GREEN}🛡️  Security scanning complete!${NC}"
echo -e "${BLUE}💡 Tip: Review critical and high severity issues before deployment${NC}"

cd ..

# Return to original directory
echo ""
echo -e "${BLUE}🚀 Ready for secure deployment!${NC}"