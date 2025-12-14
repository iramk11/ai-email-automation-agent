#!/bin/bash
# Test runner script for AI Email Automation Agent

echo "🧪 Running AI Email Automation Agent Test Suite"
echo "================================================"
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest not found. Installing dependencies..."
    pip install -r requirements.txt
fi

# Run tests based on argument
case "$1" in
    unit)
        echo "📦 Running unit tests..."
        pytest backend/tests/unit/ -v
        ;;
    integration)
        echo "🔗 Running integration tests..."
        pytest backend/tests/integration/ -v
        ;;
    coverage)
        echo "📊 Running tests with coverage..."
        pytest --cov=backend --cov-report=html --cov-report=term-missing
        echo ""
        echo "✅ Coverage report generated in htmlcov/index.html"
        ;;
    all|"")
        echo "🚀 Running all tests..."
        pytest backend/tests/ -v
        ;;
    *)
        echo "Usage: $0 [unit|integration|coverage|all]"
        echo ""
        echo "Options:"
        echo "  unit        - Run unit tests only"
        echo "  integration - Run integration tests only"
        echo "  coverage    - Run all tests with coverage report"
        echo "  all         - Run all tests (default)"
        exit 1
        ;;
esac

echo ""
echo "✅ Tests completed!"

