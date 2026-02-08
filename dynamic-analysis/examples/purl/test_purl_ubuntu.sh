#!/bin/bash

# Demo pURL với analyze tool trên Ubuntu/WSL
# Test tất cả ecosystems được hỗ trợ

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║          Pack-A-Mal pURL Test trên Ubuntu/WSL                    ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

cd /mnt/d/PROJECT/Project/pack-a-mal/dynamic-analysis/cmd/analyze

# Test cases with pURL
declare -a TESTS=(
    "pkg:pypi/requests@2.31.0|Python (PyPI)"
    "pkg:npm/express@4.18.2|Node.js (npm)"
    "pkg:npm/@babel/core@7.22.0|npm scoped package"
    "pkg:maven/org.springframework/spring-core@5.3.27|Java (Maven)"
    "pkg:gem/rails@7.0.4|Ruby (RubyGems)"
    "pkg:pypi/django|PyPI latest version"
)

SUCCESS=0
TOTAL=0

for test in "${TESTS[@]}"; do
    IFS='|' read -r purl description <<< "$test"
    TOTAL=$((TOTAL + 1))
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📦 Test $TOTAL: $description"
    echo "   pURL: $purl"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Run analyze with timeout
    OUTPUT=$(timeout 5 ./analyze -purl "$purl" -mode static 2>&1)
    
    # Check if pURL was parsed successfully
    if echo "$OUTPUT" | grep -q "Got pURL request"; then
        echo "   ✅ pURL parse: SUCCESS"
        
        # Extract resolved package info
        RESOLVED=$(echo "$OUTPUT" | grep "Processing resolved package" | head -1)
        if [ ! -z "$RESOLVED" ]; then
            ECOSYSTEM=$(echo "$RESOLVED" | grep -oP 'ecosystem[^,}]*' | cut -d'"' -f3)
            NAME=$(echo "$RESOLVED" | grep -oP 'name[^,}]*' | cut -d'"' -f3)
            VERSION=$(echo "$RESOLVED" | grep -oP 'version[^,}]*' | cut -d'"' -f3)
            
            echo "   ✅ Resolved package:"
            echo "      - Ecosystem: $ECOSYSTEM"
            echo "      - Name: $NAME"
            echo "      - Version: $VERSION"
            SUCCESS=$((SUCCESS + 1))
        fi
    else
        echo "   ❌ FAILED: Could not parse pURL"
    fi
    echo ""
done

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                        Test Summary                              ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo "✅ Successful: $SUCCESS/$TOTAL"
echo "❌ Failed: $((TOTAL - SUCCESS))/$TOTAL"
echo ""

if [ $SUCCESS -eq $TOTAL ]; then
    echo "🎉 All tests passed! pURL implementation is working perfectly!"
    echo ""
    echo "✨ Features verified:"
    echo "   ✅ pURL parsing and validation"
    echo "   ✅ Multiple ecosystems (PyPI, npm, Maven, RubyGems)"
    echo "   ✅ Scoped packages (npm @babel/core)"
    echo "   ✅ Namespace packages (Maven org.springframework)"
    echo "   ✅ Latest version resolution (no version specified)"
    echo "   ✅ Integration with analyze tool"
else
    echo "⚠️  Some tests failed. Check output above."
fi

echo ""
echo "📖 Usage examples:"
echo "   ./analyze -purl \"pkg:pypi/requests@2.31.0\""
echo "   ./analyze -purl \"pkg:npm/@babel/core@7.22.0\" -mode static"
echo "   ./analyze -purl \"pkg:maven/org.springframework/spring-core@5.3.27\""
echo ""
echo "📚 Documentation: /mnt/d/PROJECT/Project/pack-a-mal/dynamic-analysis/docs/PURL_USAGE_GUIDE.md"
