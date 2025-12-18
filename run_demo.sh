#!/bin/bash

# ==============================================================================
# Automation Framework Demo Runner
# ==============================================================================

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Automation Framework Demo${NC}"

# 1. Environment Check
echo "Checking environment..."
if [ ! -d "devvenv" ]; then
    echo -e "${RED}❌ Virtual environment 'devvenv' not found!${NC}"
    exit 1
fi
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    exit 1
fi

# 2. Cleanup Old Reports
echo "Cleaning up old reports..."
rm -rf allure-results/* reports/*

# 3. Run Tests
echo "Running Test Suite..."
# Running all tests in tests/ folder, skipping those marked with @skip (UI tests)
PYTHONPATH=. ./devvenv/bin/pytest tests/ --alluredir=allure-results --html=reports/report.html --self-contained-html

TEST_EXIT_CODE=$?

# 4. Report Generation
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed successfully!${NC}"
else
    echo -e "${RED}⚠️ Some tests failed or were skipped.${NC}"
fi

echo -e "${GREEN}📊 Generating Allure Report...${NC}"
./scripts/serve_report.sh
