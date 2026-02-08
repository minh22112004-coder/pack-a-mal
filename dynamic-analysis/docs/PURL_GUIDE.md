# Package URL (pURL) Implementation Guide

## Tổng Quan

Tài liệu này hướng dẫn sử dụng Package URL (pURL) để scan và phân tích packages trong hệ thống Pack-A-Mal.

## pURL là gì?

Package URL (pURL) là một chuẩn định danh phổ quát cho các software packages từ nhiều hệ sinh thái khác nhau.

**Cú pháp:**
```
pkg:<ecosystem>/<namespace>/<name>@<version>?<qualifiers>#<subpath>
```

**Ví dụ:**
- `pkg:pypi/requests@2.31.0` - Python package
- `pkg:npm/express@4.18.2` - Node.js package  
- `pkg:npm/@angular/core@15.0.0` - npm scoped package
- `pkg:maven/org.springframework/spring-core@5.3.27` - Java package

## Ecosystems Được Hỗ Trợ

| Ecosystem | pURL Type | Ví Dụ |
|-----------|-----------|--------|
| Python (PyPI) | `pypi` | `pkg:pypi/django@4.2.0` |
| Node.js (npm) | `npm` | `pkg:npm/express@4.18.2` |
| Ruby (RubyGems) | `gem` | `pkg:gem/rails@7.0.4` |
| Java (Maven) | `maven` | `pkg:maven/org.springframework/spring-core@5.3.27` |
| PHP (Packagist) | `packagist` | `pkg:packagist/symfony/symfony@5.4.0` |
| Rust (Crates) | `cargo` | `pkg:cargo/serde@1.0.163` |

## Sử Dụng pURL với Analyze Tool

### Command-Line (Linux/WSL)

**Cú pháp cơ bản:**
```bash
./analyze -purl "pkg:ecosystem/name@version"
```

**Ví dụ:**
```bash
# Phân tích Python package
./analyze -purl "pkg:pypi/requests@2.31.0"

# Phân tích npm scoped package
./analyze -purl "pkg:npm/@babel/core@7.22.0"

# Chỉ định analysis mode
./analyze -purl "pkg:npm/express@4.18.2" -mode dynamic,static

# Phân tích latest version (không chỉ định version)
./analyze -purl "pkg:pypi/django"
```

### Web API

**Endpoint:** `POST /api/analyze`

**Request:**
```json
{
  "purl": "pkg:pypi/requests@2.31.0",
  "priority": 0
}
```

**Response:**
```json
{
  "task_id": 12345,
  "status": "queued",
  "purl": "pkg:pypi/requests@2.31.0",
  "package_name": "requests",
  "package_version": "2.31.0",
  "ecosystem": "pypi",
  "result_url": "/api/tasks/12345/status",
  "download_url": "/reports/pypi/requests/2.31.0.json"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"purl": "pkg:pypi/requests@2.31.0"}'
```

## Testing

### Test trên Ubuntu/WSL

```bash
# Build analyze tool
cd dynamic-analysis/cmd/analyze
go build -o analyze .

# Run test script
bash /path/to/test_purl_ubuntu.sh

# Manual test
./analyze -purl "pkg:pypi/requests@2.31.0" -mode static
```

### Test với Python Script

```bash
cd dynamic-analysis/examples
python test_purl_parsing.py
```

## Implementation Details

### Code Changes

**File:** [cmd/analyze/main.go](../cmd/analyze/main.go)

- Thêm flag `-purl` để nhận pURL input
- Tích hợp `packageurl-go` library  
- Logic parse và resolve package từ pURL
- Tương thích với phương pháp cũ (-ecosystem/-package/-version)

**Key Functions:**
```go
// Parse pURL string
purlObj, err := packageurl.FromString(*purl)

// Resolve package from pURL
pkg, err := worker.ResolvePurl(purlObj)
```

## Examples & Resources

### Sample pURLs

Xem file [examples/purl-examples.txt](../examples/purl-examples.txt) cho danh sách pURL mẫu.

### Detailed Examples

Xem [examples/PURL_EXAMPLES.md](../examples/PURL_EXAMPLES.md) cho:
- Command-line examples
- Python/JavaScript API examples
- SBOM analysis workflows
- Security audit scenarios

### Test Scripts

- [test_purl_parsing.py](../examples/test_purl_parsing.py) - pURL parser demo
- [analyze-with-purl.sh](../examples/analyze-with-purl.sh) - Shell script examples
- [test_purl_ubuntu.sh](../examples/test_purl_ubuntu.sh) - Comprehensive test suite

## Troubleshooting

### Common Errors

**Error:** "Invalid pURL format"
```bash
# ❌ Sai - thiếu pkg: prefix
./analyze -purl "pypi/requests@2.31.0"

# ✅ Đúng
./analyze -purl "pkg:pypi/requests@2.31.0"
```

**Error:** "Unsupported ecosystem"
```bash
# Kiểm tra ecosystems được hỗ trợ
./analyze -help | grep ecosystem
```

**Error:** "Package not found"
```bash
# Thử với latest version để kiểm tra package tồn tại
./analyze -purl "pkg:pypi/package-name"
```

## Lợi Ích

1. **Universal Format**: Một format cho tất cả ecosystems
2. **Unambiguous**: Rõ ràng về package, version, và nguồn
3. **URL-Safe**: Sử dụng được trong URLs và APIs
4. **Standardized**: Dựa trên [pURL specification](https://github.com/package-url/purl-spec)
5. **SBOM Compatible**: Tương thích với SPDX, CycloneDX
6. **Convenient**: Tất cả thông tin trong một chuỗi

## References

- [pURL Specification](https://github.com/package-url/purl-spec)
- [packageurl-go Library](https://github.com/package-url/packageurl-go)
- [Examples Documentation](../examples/PURL_EXAMPLES.md)
- [Main README](../../README.md)
