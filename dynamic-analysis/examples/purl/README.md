# Package URL (pURL) Examples

This directory contains examples, test scripts, and documentation for analyzing packages using the Package URL (pURL) format.

## Overview

Package URL (pURL) is a standard format for identifying software packages across different ecosystems using a universal identifier: `pkg:ecosystem/namespace/name@version`

## Files in This Directory

### Documentation & Examples

- **[PURL_EXAMPLES.md](PURL_EXAMPLES.md)** - Comprehensive guide with detailed examples for analyzing packages using pURL format
  - Command-line analysis examples
  - Batch processing workflows
  - API integration examples
  - SBOM analysis scenarios

### Test & Demo Scripts

- **[test_purl_ubuntu.sh](test_purl_ubuntu.sh)** - Comprehensive test suite for pURL functionality
  - Tests all 6 supported ecosystems (PyPI, npm, Maven, RubyGems, etc.)
  - Validates scoped packages, namespaces, and version resolution
  - Run on Ubuntu/WSL environment

- **[test_purl_parsing.py](test_purl_parsing.py)** - Python demonstration script
  - Simulates pURL parsing logic
  - Useful for testing without building the Go binary

- **[analyze-with-purl.sh](analyze-with-purl.sh)** - Shell script with various pURL usage examples
  - Single package analysis
  - Batch processing
  - Different ecosystem examples

- **[purl-examples.txt](purl-examples.txt)** - Sample pURL list for quick testing
  - Covers all supported ecosystems
  - Includes scoped and namespaced packages

## Quick Start

### Command-Line Analysis

```bash
# Build the analyze tool first
cd ../../
make build

# Analyze a Python package
./analyze -purl "pkg:pypi/requests@2.31.0"

# Analyze an npm package (scoped)
./analyze -purl "pkg:npm/@babel/core@7.22.0"

# Analyze latest version
./analyze -purl "pkg:pypi/flask"
```

### Run Test Suite

```bash
# On Ubuntu/WSL
cd purl/
chmod +x test_purl_ubuntu.sh
./test_purl_ubuntu.sh
```

## Supported Ecosystems

- **PyPI** - `pkg:pypi/package-name@version`
- **npm** - `pkg:npm/package-name@version` or `pkg:npm/@scope/package@version`
- **Maven** - `pkg:maven/group.id/artifact-id@version`
- **RubyGems** - `pkg:gem/package-name@version`
- **Packagist** - `pkg:composer/vendor/package@version`
- **Crates.io** - `pkg:cargo/package-name@version`

## Additional Documentation

- **[../../docs/PURL_GUIDE.md](../../docs/PURL_GUIDE.md)** - Complete implementation guide
- **[Package URL Specification](https://github.com/package-url/purl-spec)** - Official pURL spec

## Requirements

- Go 1.22.2+ (for building analyze tool)
- Ubuntu/WSL (for testing, due to Unix syscall dependencies)
- Internet connection (for downloading packages)
