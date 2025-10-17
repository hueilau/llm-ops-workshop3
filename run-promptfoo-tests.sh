#!/bin/bash

# Promptfoo Testing Script for FastAPI QA Service
# This script runs hallucination and bias detection tests

set -e

echo "🧪 Starting Promptfoo Tests for Hallucination and Bias Detection..."

# Check if promptfoo is installed
if ! command -v promptfoo &> /dev/null; then
    echo "📦 Installing Promptfoo..."
    npm install -g promptfoo
fi

# Wait for FastAPI service to be ready
echo "⏳ Waiting for FastAPI service to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ FastAPI service is ready!"
        break
    fi
    echo "Waiting... ($i/30)"
    sleep 2
done

# Check if service is accessible
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ FastAPI service is not accessible. Please ensure it's running on port 8000."
    exit 1
fi

# Run Promptfoo evaluation
echo "🔍 Running Promptfoo evaluation..."
promptfoo eval -c promptfoo.yaml

# Generate report
echo "📊 Generating test report..."
promptfoo view --port 3000 &
VIEWER_PID=$!

echo ""
echo "🎉 Promptfoo tests completed!"
echo "📊 View results at: http://localhost:3000"
echo "📁 Results saved to: ./promptfoo-results.json"
echo ""
echo "Key Test Areas:"
echo "  ✓ Hallucination Detection"
echo "  ✓ Gender Bias Detection"
echo "  ✓ Cultural Bias Detection" 
echo "  ✓ Factual Consistency"
echo "  ✓ Context Grounding"
echo ""

# Wait for user input to close viewer
read -p "Press Enter to close the report viewer..."
kill $VIEWER_PID 2>/dev/null || true

echo "✅ Testing session completed!"