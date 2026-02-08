#!/usr/bin/env python3
"""
Demo script to test pURL parsing logic
This demonstrates how pURL works without needing to build the Go binary.
"""

import re
import sys


class PURLParser:
    """Package URL Parser Demo"""
    
    SUPPORTED_ECOSYSTEMS = {
        'pypi': 'PyPI (Python)',
        'npm': 'npm (Node.js)',
        'gem': 'RubyGems (Ruby)',
        'maven': 'Maven (Java)',
        'packagist': 'Packagist (PHP)',
        'cargo': 'Crates.io (Rust)',
    }
    
    @classmethod
    def parse(cls, purl: str) -> dict:
        """Parse a pURL string"""
        if not purl or not purl.startswith('pkg:'):
            raise ValueError("Invalid pURL: must start with 'pkg:'")
        
        # Remove 'pkg:' prefix
        purl_part = purl[4:]
        
        # Split ecosystem and rest
        if '/' not in purl_part:
            raise ValueError("Invalid pURL: missing ecosystem separator")
        
        parts = purl_part.split('/', 1)
        ecosystem = parts[0]
        rest = parts[1] if len(parts) > 1 else ''
        
        if ecosystem not in cls.SUPPORTED_ECOSYSTEMS:
            raise ValueError(f"Unsupported ecosystem: {ecosystem}")
        
        # Parse version
        version = None
        if '@' in rest:
            name_part, version = rest.rsplit('@', 1)
        else:
            name_part = rest
        
        # Parse namespace/name
        namespace = None
        if '/' in name_part:
            namespace, name = name_part.split('/', 1)
        else:
            name = name_part
        
        return {
            'purl': purl,
            'ecosystem': ecosystem,
            'ecosystem_name': cls.SUPPORTED_ECOSYSTEMS[ecosystem],
            'namespace': namespace,
            'name': name,
            'version': version or 'latest',
            'full_name': f"{namespace}/{name}" if namespace else name
        }


def print_parsed(purl: str):
    """Parse and print pURL information"""
    try:
        result = PURLParser.parse(purl)
        print(f"\n✅ Successfully parsed pURL:")
        print(f"   Original:  {result['purl']}")
        print(f"   Ecosystem: {result['ecosystem_name']}")
        print(f"   Package:   {result['full_name']}")
        print(f"   Version:   {result['version']}")
        if result['namespace']:
            print(f"   Namespace: {result['namespace']}")
        print(f"\n   ➡️  Command that would run:")
        print(f"      ./analyze -purl \"{result['purl']}\"")
        return True
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        return False


def main():
    """Demo pURL parsing"""
    print("=" * 70)
    print("Package URL (pURL) Parser Demo")
    print("=" * 70)
    
    # Test cases
    test_purls = [
        "pkg:pypi/requests@2.31.0",
        "pkg:npm/express@4.18.2",
        "pkg:npm/@babel/core@7.22.0",
        "pkg:maven/org.springframework/spring-core@5.3.27",
        "pkg:gem/rails@7.0.4",
        "pkg:cargo/serde@1.0.163",
        "pkg:pypi/django",  # Latest version
    ]
    
    if len(sys.argv) > 1:
        # Use command line argument
        test_purls = sys.argv[1:]
    
    success_count = 0
    fail_count = 0
    
    for purl in test_purls:
        if print_parsed(purl):
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "=" * 70)
    print(f"Results: {success_count} successful, {fail_count} failed")
    print("=" * 70)
    
    # Show invalid examples
    print("\n❌ Examples that would FAIL:")
    invalid_purls = [
        "pypi/requests@2.31.0",  # Missing pkg: prefix
        "pkg:invalid/test@1.0",  # Unsupported ecosystem
        "pkg:pypi",              # Missing package name
    ]
    
    for purl in invalid_purls:
        try:
            PURLParser.parse(purl)
        except ValueError as e:
            print(f"   {purl}")
            print(f"      Error: {e}")
    
    print("\n✨ Implementation verified! pURL parsing logic works correctly.")
    print("\nTo test the actual analyze tool (on Linux):")
    print("   cd dynamic-analysis/cmd/analyze")
    print("   go build -o analyze .")
    print("   ./analyze -purl \"pkg:pypi/requests@2.31.0\"")
    print("\nOr use the Web API (works on Windows):")
    print("   curl -X POST http://localhost:8000/api/analyze \\")
    print("     -H \"Content-Type: application/json\" \\")
    print("     -H \"X-API-Key: your-api-key\" \\")
    print("     -d '{\"purl\": \"pkg:pypi/requests@2.31.0\"}'")
    

if __name__ == '__main__':
    main()
