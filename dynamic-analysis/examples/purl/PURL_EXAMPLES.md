# Example: Analyzing Packages using pURL

## Quick Start

### Using the Analyze Tool

```bash
# Build the analyze tool
cd dynamic-analysis/cmd/analyze
go build -o analyze main.go

# Analyze a Python package
./analyze -purl "pkg:pypi/requests@2.31.0"

# Analyze with specific modes
./analyze -purl "pkg:npm/express@4.18.2" -mode dynamic,static

# Analyze latest version
./analyze -purl "pkg:pypi/django"
```

### Using the Downloader Tool

```bash
# Build the downloader tool
cd dynamic-analysis/cmd/downloader
go build -o downloader main.go

# Download packages from pURL list
./downloader -f ../../examples/purl-examples.txt -d ./downloads
```

### Using the Web API

```bash
# Analyze via API
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{
    "purl": "pkg:pypi/requests@2.31.0"
  }'

# Check analysis status
curl -X GET http://localhost:8000/api/tasks/12345/status \
  -H "X-API-Key: your-api-key-here"
```

## Example Scenarios

### Scenario 1: Analyze Multiple Packages from Different Ecosystems

```bash
# Create a pURL list file
cat > mixed-packages.txt <<EOF
pkg:pypi/requests@2.31.0
pkg:npm/express@4.18.2
pkg:gem/rails@7.0.4
pkg:maven/org.springframework/spring-core@5.3.27
EOF

# Download all packages
./downloader -f mixed-packages.txt -d ./packages

# Analyze each package
for purl in $(cat mixed-packages.txt); do
  ./analyze -purl "$purl" -mode dynamic,static
done
```

### Scenario 2: Analyze Specific npm Scoped Packages

```bash
# React ecosystem packages
./analyze -purl "pkg:npm/react@18.2.0" -mode static
./analyze -purl "pkg:npm/react-dom@18.2.0" -mode static
./analyze -purl "pkg:npm/@types/react@18.2.0" -mode static

# Angular ecosystem packages
./analyze -purl "pkg:npm/@angular/core@15.0.0" -mode dynamic
./analyze -purl "pkg:npm/@angular/common@15.0.0" -mode dynamic
```

### Scenario 3: Security Audit Workflow

```bash
# 1. Extract dependencies from your project
# For Python (requirements.txt to pURL)
cat requirements.txt | while read line; do
  pkg=$(echo $line | cut -d'=' -f1)
  ver=$(echo $line | cut -d'=' -f3)
  echo "pkg:pypi/$pkg@$ver"
done > purls.txt

# 2. Download all dependencies
./downloader -f purls.txt -d ./audit-packages

# 3. Analyze each dependency
while read purl; do
  echo "Analyzing: $purl"
  ./analyze -purl "$purl" -mode dynamic,static \
    -dynamic-bucket "gs://audit-results/dynamic" \
    -static-bucket "gs://audit-results/static"
done < purls.txt
```

### Scenario 4: Comparing Package Versions

```bash
# Analyze different versions of the same package
for version in 2.28.0 2.29.0 2.30.0 2.31.0; do
  echo "Analyzing requests version $version"
  ./analyze -purl "pkg:pypi/requests@$version" -mode static
done
```

### Scenario 5: SBOM Analysis

```bash
# Example: Analyze all packages from a CycloneDX SBOM
# Install jq if not available: apt-get install jq

# Extract pURLs from SBOM
jq -r '.components[].purl' sbom.json > sbom-purls.txt

# Download all SBOM packages
./downloader -f sbom-purls.txt -d ./sbom-packages

# Analyze all SBOM packages
while read purl; do
  ./analyze -purl "$purl" -mode dynamic,static
done < sbom-purls.txt
```

## Python Script Example

```python
#!/usr/bin/env python3
"""
Example: Analyze packages using pURL via subprocess
"""
import subprocess
import json

def analyze_package_purl(purl, modes=['dynamic', 'static']):
    """Analyze a package using its pURL"""
    cmd = [
        './analyze',
        '-purl', purl,
        '-mode', ','.join(modes)
    ]
    
    print(f"Analyzing: {purl}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✓ Success: {purl}")
    else:
        print(f"✗ Failed: {purl}")
        print(f"Error: {result.stderr}")
    
    return result.returncode == 0

# Example usage
packages = [
    "pkg:pypi/requests@2.31.0",
    "pkg:npm/express@4.18.2",
    "pkg:gem/rails@7.0.4",
]

results = {}
for purl in packages:
    results[purl] = analyze_package_purl(purl)

# Print summary
print("\n=== Analysis Summary ===")
for purl, success in results.items():
    status = "✓" if success else "✗"
    print(f"{status} {purl}")
```

## Web API Examples

### Python Example

```python
import requests
import time

API_KEY = "your-api-key-here"
BASE_URL = "http://localhost:8000"

def analyze_package(purl):
    """Submit package for analysis"""
    response = requests.post(
        f"{BASE_URL}/api/analyze",
        headers={
            "Content-Type": "application/json",
            "X-API-Key": API_KEY
        },
        json={"purl": purl}
    )
    return response.json()

def check_status(task_id):
    """Check analysis status"""
    response = requests.get(
        f"{BASE_URL}/api/tasks/{task_id}/status",
        headers={"X-API-Key": API_KEY}
    )
    return response.json()

# Analyze a package
result = analyze_package("pkg:pypi/requests@2.31.0")
task_id = result['task_id']
print(f"Task ID: {task_id}")

# Poll for completion
while True:
    status = check_status(task_id)
    print(f"Status: {status['status']}")
    
    if status['status'] == 'completed':
        print(f"Report available at: {status['download_url']}")
        break
    elif status['status'] == 'failed':
        print(f"Analysis failed: {status.get('error_message')}")
        break
    
    time.sleep(5)
```

### JavaScript Example

```javascript
const axios = require('axios');

const API_KEY = 'your-api-key-here';
const BASE_URL = 'http://localhost:8000';

async function analyzePackage(purl) {
  const response = await axios.post(
    `${BASE_URL}/api/analyze`,
    { purl },
    {
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
      }
    }
  );
  return response.data;
}

async function checkStatus(taskId) {
  const response = await axios.get(
    `${BASE_URL}/api/tasks/${taskId}/status`,
    {
      headers: { 'X-API-Key': API_KEY }
    }
  );
  return response.data;
}

async function main() {
  // Analyze a package
  const result = await analyzePackage('pkg:npm/express@4.18.2');
  console.log(`Task ID: ${result.task_id}`);
  
  // Poll for completion
  while (true) {
    const status = await checkStatus(result.task_id);
    console.log(`Status: ${status.status}`);
    
    if (status.status === 'completed') {
      console.log(`Report available at: ${status.download_url}`);
      break;
    } else if (status.status === 'failed') {
      console.log(`Analysis failed: ${status.error_message}`);
      break;
    }
    
    await new Promise(resolve => setTimeout(resolve, 5000));
  }
}

main();
```

## Testing Tips

1. **Start with static analysis**: It's faster and doesn't require networking
   ```bash
   ./analyze -purl "pkg:pypi/requests@2.31.0" -mode static
   ```

2. **Use offline mode for local testing**: Prevents network side effects
   ```bash
   ./analyze -purl "pkg:npm/lodash@4.17.21" -offline
   ```

3. **Test with known packages first**: Start with popular, well-known packages

4. **Check logs**: Enable verbose logging for debugging
   ```bash
   LOGGER_ENV=development ./analyze -purl "pkg:pypi/django@4.2.0"
   ```

## Common Issues

### Issue: "Invalid pURL format"
**Solution**: Ensure pURL starts with `pkg:` and follows the correct format
```bash
# Wrong
./analyze -purl "pypi/requests@2.31.0"

# Correct
./analyze -purl "pkg:pypi/requests@2.31.0"
```

### Issue: "Unsupported ecosystem"
**Solution**: Check the ecosystem type is supported
```bash
# Check available ecosystems
./analyze -help | grep ecosystem
```

### Issue: Package not found
**Solution**: Verify package name and version exist in the ecosystem
```bash
# Test with latest version first
./analyze -purl "pkg:pypi/package-name"
```

## Further Reading

- [pURL Usage Guide](../docs/PURL_USAGE_GUIDE.md)
- [Analysis Tool Documentation](../README.md)
- [API Documentation](../../web/packamal/API_DOCUMENTATION.md)
