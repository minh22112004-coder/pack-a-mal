#!/bin/bash

# Example script to analyze packages using pURL
# This demonstrates various ways to use pURL with the analyze tool

echo "=== Package Analysis with pURL Examples ==="
echo ""

# Example 1: Basic pURL analysis
echo "1. Analyzing Python package using pURL..."
./analyze -purl "pkg:pypi/requests@2.31.0" -mode dynamic

# Example 2: Latest version
echo ""
echo "2. Analyzing latest version of a package..."
./analyze -purl "pkg:pypi/flask" -mode static

# Example 3: npm scoped package
echo ""
echo "3. Analyzing npm scoped package..."
./analyze -purl "pkg:npm/@babel/core@7.22.0" -mode dynamic,static

# Example 4: Maven package with namespace
echo ""
echo "4. Analyzing Maven package..."
./analyze -purl "pkg:maven/org.springframework/spring-core@5.3.27" -mode static

# Example 5: With custom buckets for results
echo ""
echo "5. Analyzing with result storage..."
./analyze \
  -purl "pkg:pypi/django@4.2.0" \
  -mode dynamic,static \
  -dynamic-bucket "gs://my-bucket/dynamic" \
  -static-bucket "gs://my-bucket/static"

# Example 6: Offline analysis (no network access)
echo ""
echo "6. Offline analysis..."
./analyze -purl "pkg:npm/lodash@4.17.21" -mode static -offline

echo ""
echo "=== Examples Complete ==="
