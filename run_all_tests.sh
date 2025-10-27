#!/bin/bash
# IntelliVoice Device - Run All Tests
# Comprehensive test suite runner

echo "================================"
echo "IntelliVoice Device Test Suite"
echo "================================"
echo ""

FAILED=0
PASSED=0

# Test 1: Configuration Test
echo "Running Configuration Validation Tests..."
if python3 test_intellivoice.py 2>/dev/null; then
    echo "✓ Configuration tests PASSED"
    ((PASSED++))
else
    echo "✗ Configuration tests FAILED"
    ((FAILED++))
fi

echo ""
echo "--------------------------------"
echo ""

# Test 2: Unit Tests
echo "Running Unit Tests..."
if python3 test_units.py 2>/dev/null | grep -q "Success rate: 100.0%"; then
    echo "✓ Unit tests PASSED"
    ((PASSED++))
else
    echo "✗ Unit tests FAILED"
    python3 test_units.py 2>/dev/null | tail -5
    ((FAILED++))
fi

echo ""
echo "================================"
echo "Test Summary"
echo "================================"
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "All tests passed!"
    exit 0
else
    echo "Some tests failed"
    exit 1
fi

