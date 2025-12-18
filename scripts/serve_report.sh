#!/bin/bash
# scripts/serve_report.sh

# Check for local allure first
if [ -f "./bin/allure/bin/allure" ]; then
    ALLURE_CMD="./bin/allure/bin/allure"
elif command -v allure &> /dev/null; then
    ALLURE_CMD="allure"
else
    echo "❌ Allure command not found."
    echo "Run: ./scripts/install_allure.sh"
    exit 1
fi

echo "🚀 Generating and Serving Allure Report using $ALLURE_CMD..."
$ALLURE_CMD serve allure-results
