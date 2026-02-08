# Hệ Thống Giả Lập HTTP Mở Rộng

## 📋 Tổng Quan

Hệ thống giả lập HTTP mở rộng cung cấp khả năng:
- **Phân tích yêu cầu HTTP đến** - Trích xuất và phân tích chi tiết các thành phần của request
- **Nhận diện mục đích truy cập** - Phân loại request theo mục đích và độ nguy hiểm
- **Trả về phản hồi phù hợp** - Tạo response động dựa trên loại request
- **Xử lý an toàn file thực thi** - Cơ chế sandbox và honeypot cho executable downloads

## 🏗️ Kiến Trúc Hệ Thống

```
HTTP Request → Analyzer → Classifier → Response Handler → HTTP Response
                                              ↓
                                    Safe Executable Handler
                                              ↓
                                    Sandbox/Honeypot/Block
```

### Components

1. **HTTPRequestAnalyzer** (`analyzer/http_analyzer.py`)
   - Phân tích method, URL, headers, body
   - Trích xuất query parameters
   - Phát hiện file extension và executable requests
   - Kiểm tra security flags (XSS, SQL injection, path traversal, etc.)

2. **RequestClassifier** (`analyzer/request_classifier.py`)
   - Phân loại request thành 9 categories
   - Xác định intent và confidence level
   - Đề xuất recommended action

3. **ResponseHandler** (`handler/response_handler.py`)
   - Tạo response phù hợp cho từng loại request
   - Hỗ trợ static content, API, auth, downloads
   - Tích hợp SafeExecutableHandler

4. **SafeExecutableHandler** (`handler/safe_executable_handler.py`)
   - Xử lý an toàn executable downloads
   - 3 chiến lược: sandbox_fake, honeypot, block
   - Logging và metadata tracking

## 📊 Request Categories

| Category | Description | Example URLs |
|----------|-------------|--------------|
| `static_content` | Images, CSS, JS, fonts | `/style.css`, `/logo.png` |
| `api_call` | API endpoints | `/api/users`, `/v1/data.json` |
| `file_download` | File downloads | `/download/doc.pdf` |
| `executable_download` | Executable files | `/malware.exe`, `/script.sh` |
| `upload` | File uploads | POST to `/upload` |
| `authentication` | Login/auth | `/login`, `/oauth/token` |
| `data_exfiltration` | Suspicious uploads | `/backdoor.php`, `/c2` |
| `malicious` | Attack attempts | SQL injection, XSS |
| `unknown` | Unclassified | - |

## 🔒 Security Features

### Risk Levels
- **Low**: Bình thường, không có dấu hiệu nguy hiểm
- **Medium**: Có một số pattern đáng ngờ
- **High**: Phát hiện attack patterns hoặc command injection

### Security Flags
- `has_path_traversal`: Phát hiện `../` patterns
- `has_xss_attempt`: Phát hiện `<script>` tags
- `has_sql_injection`: Phát hiện SQL keywords
- `has_command_injection`: Phát hiện command execution attempts

### Safe Executable Handling Strategies

#### 1. Sandbox Fake (Low Risk)
```python
# Trả về file giả an toàn
# Chỉ chứa metadata, không có code thực thi
Headers: X-Sandboxed: true
```

#### 2. Honeypot (Medium Risk)
```python
# Trả về file có tracking capabilities
# Có thể monitor behavior nếu được execute
Headers: X-Honeypot: true, X-Tracking-Enabled: true
```

#### 3. Block (High Risk)
```python
# Block request hoàn toàn
Status: 403 Forbidden
```

## 🚀 API Endpoints

### 1. GET /status
Kiểm tra trạng thái service

**Response:**
```json
{
  "service": "http-simulation",
  "status": "running",
  "version": "2.0",
  "features": [
    "http_analysis",
    "request_classification",
    "safe_executable_handling",
    "adaptive_response"
  ]
}
```

### 2. POST /analyze
Phân tích một HTTP request (testing/debugging)

**Request Body:**
```json
{
  "method": "GET",
  "url": "/download/malware.exe",
  "headers": {
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*"
  },
  "body": null,
  "client_ip": "192.168.1.100"
}
```

**Response:**
```json
{
  "analysis": {
    "timestamp": "2026-02-08T10:30:00.000Z",
    "method": "GET",
    "url": "/download/malware.exe",
    "file_extension": ".exe",
    "is_executable_request": true,
    "security_flags": {
      "risk_level": "medium",
      "suspicious_patterns_found": []
    }
  },
  "classification": {
    "category": "executable_download",
    "sub_category": ".exe",
    "confidence": 0.95,
    "intent": "download_executable",
    "recommended_action": "sandbox_and_serve"
  },
  "summary": "GET request to /download/malware.exe from 192.168.1.100 (executable download) [MEDIUM RISK]"
}
```

### 3. POST /simulate
Simulate request và trả về response thực tế

**Request:** Giống `/analyze`

**Response:** HTTP response thực tế với content, headers, status code

### 4. GET /stats
Lấy thống kê về requests đã xử lý

### 5. GET /logs/executables
Liệt kê tất cả executable requests đã được log

**Response:**
```json
{
  "logs": [
    {
      "type": "executable_request",
      "request_id": "a1b2c3d4e5f67890",
      "timestamp": "2026-02-08T10:30:00.000Z",
      "filename": "malware.exe",
      "extension": ".exe",
      "platform": "windows",
      "client_ip": "192.168.1.100",
      "risk_level": "medium"
    }
  ],
  "count": 1
}
```

### 6. Catch-all: /* (All Methods)
Xử lý mọi HTTP request không match các endpoint trên

## 💻 Sử Dụng

### Khởi động hệ thống

```bash
cd service-simulation-module
docker-compose up --build
```

### Test với curl

#### 1. Kiểm tra status
```bash
curl http://localhost:5000/status
```

#### 2. Phân tích request
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "method": "GET",
    "url": "/download/tool.exe",
    "headers": {"User-Agent": "Python/3.9"},
    "client_ip": "10.0.0.5"
  }'
```

#### 3. Simulate executable download
```bash
curl -X POST http://localhost:5000/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "method": "GET",
    "url": "/malware.exe",
    "headers": {"Accept": "application/octet-stream"},
    "client_ip": "192.168.1.100"
  }' -o downloaded.exe
```

#### 4. Test API request
```bash
curl http://localhost:5000/api/v1/users
```

#### 5. Test static content
```bash
curl http://localhost:5000/styles/main.css
curl http://localhost:5000/images/logo.png
```

#### 6. Test malicious request
```bash
curl "http://localhost:5000/search?q=<script>alert('xss')</script>"
```

#### 7. View executable logs
```bash
curl http://localhost:5000/logs/executables
```

### Test với Python

```python
import requests

# Analyze a request
response = requests.post('http://localhost:5000/analyze', json={
    'method': 'GET',
    'url': '/download/setup.exe',
    'headers': {'User-Agent': 'Malware/1.0'},
    'client_ip': '1.2.3.4'
})

print(response.json())

# Simulate and download
response = requests.post('http://localhost:5000/simulate', json={
    'method': 'GET',
    'url': '/backdoor.sh',
    'headers': {},
    'client_ip': '5.6.7.8'
})

with open('simulated.sh', 'wb') as f:
    f.write(response.content)

print(f"Headers: {response.headers}")
print(f"Sandboxed: {response.headers.get('X-Sandboxed')}")
```

## 📁 File Structure

```
service-simulation-module/
├── service-simulation/
│   └── app/
│       ├── analyzer/
│       │   ├── __init__.py
│       │   ├── http_analyzer.py        # HTTP request analysis
│       │   └── request_classifier.py   # Request classification
│       ├── handler/
│       │   ├── __init__.py
│       │   ├── response_handler.py          # Response generation
│       │   └── safe_executable_handler.py   # Safe executable handling
│       ├── api/
│       │   └── server.py               # Flask API endpoints
│       ├── collector/
│       │   └── logs.py
│       ├── config/
│       │   └── inetsim.py
│       └── main.py
└── shared/
    └── logs/
        └── executables/                # Sandboxed executables
            ├── <request_id>_file.exe
            ├── <request_id>_file.exe.metadata.json
            └── executable_requests.log
```

## 🔍 Logging

### Executable Request Log Format
```json
{
  "type": "executable_request",
  "request_id": "unique_hash",
  "timestamp": "2026-02-08T10:30:00.000Z",
  "filename": "malware.exe",
  "extension": ".exe",
  "platform": "windows",
  "client_ip": "192.168.1.100",
  "risk_level": "medium",
  "is_suspicious": false
}
```

### Sandboxed File Metadata
Mỗi file được sandbox sẽ có file `.metadata.json` kèm theo:
```json
{
  "request_id": "a1b2c3d4e5f67890",
  "timestamp": "2026-02-08T10:30:00.000Z",
  "filename": "malware.exe",
  "extension": ".exe",
  "full_path": "/download/malware.exe",
  "client_ip": "192.168.1.100",
  "user_agent": "Mozilla/5.0",
  "platform": "windows",
  "risk_assessment": {
    "level": "medium",
    "is_suspicious": true
  },
  "handling_strategy": "honeypot"
}
```

## ⚙️ Configuration

### Tùy chỉnh Executable Signatures
Trong `safe_executable_handler.py`:

```python
self.executable_signatures = {
    '.exe': {
        'magic_bytes': b'MZ',
        'mime_type': 'application/x-msdownload',
        'platform': 'windows'
    },
    # Thêm signatures mới...
}
```

### Tùy chỉnh Security Patterns
Trong `http_analyzer.py`:

```python
self.suspicious_patterns = [
    r'\.\./',           # Path traversal
    r'<script',         # XSS
    r'union.*select',   # SQL injection
    # Thêm patterns mới...
]
```

## 🧪 Testing Scenarios

### Scenario 1: Normal Static Content
```bash
curl http://localhost:5000/style.css
# Expected: CSS content, status 200
```

### Scenario 2: Executable Download (Low Risk)
```bash
curl http://localhost:5000/installer.exe -o test.exe
# Expected: Safe fake executable, X-Sandboxed: true
```

### Scenario 3: Suspicious Executable (Medium Risk)
```bash
curl http://localhost:5000/backdoor.exe -H "User-Agent: Malware"
# Expected: Honeypot executable, X-Honeypot: true
```

### Scenario 4: Malicious Request (High Risk)
```bash
curl "http://localhost:5000/download?file=../../etc/passwd"
# Expected: Blocked, status 403
```

### Scenario 5: API Request
```bash
curl http://localhost:5000/api/v1/data.json
# Expected: JSON response, simulated data
```

## 🐛 Troubleshooting

### Issue: Module import errors
**Solution:** Đảm bảo các `__init__.py` đã được tạo trong `analyzer/` và `handler/`

### Issue: Sandbox directory không tồn tại
**Solution:** Kiểm tra volume mapping trong `docker-compose.yml`:
```yaml
volumes:
  - ./shared/logs:/logs
```

### Issue: Logs không được ghi
**Solution:** Kiểm tra permissions của thư mục `shared/logs/`

## 📈 Future Enhancements

- [ ] Database integration cho statistics
- [ ] Real-time dashboard cho monitoring
- [ ] Machine learning cho better classification
- [ ] Integration với dynamic analysis system
- [ ] Advanced honeypot executables với actual tracking code
- [ ] Support cho thêm file types (PDF, Office docs)
- [ ] Rate limiting và abuse prevention
- [ ] Webhook notifications cho high-risk requests

## 📚 References

- [Flask Documentation](https://flask.palletsprojects.com/)
- [HTTP Status Codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- [MIME Types](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types)
- [Executable File Formats](https://en.wikipedia.org/wiki/Executable)
