# HTTP Simulation System - Quick Reference

## 🚀 Quick Start

```bash
# 1. Start services
cd service-simulation-module
docker-compose up -d

# 2. Check status
curl http://localhost:5000/status

# 3. Run demo
python demo_http_simulation.py
```

## 📊 Request Categories

| Category | Example URL | Response Type |
|----------|-------------|---------------|
| `static_content` | `/style.css` | CSS/JS/Image |
| `api_call` | `/api/v1/data` | JSON |
| `executable_download` | `/tool.exe` | Safe fake/honeypot |
| `authentication` | `/login` | Fake auth |
| `malicious` | `?q=<script>` | Blocked/Logged |

## 🔒 Risk Levels & Actions

| Risk | Triggers | Action |
|------|----------|--------|
| **Low** | Normal requests | Serve content |
| **Medium** | Suspicious patterns | Honeypot |
| **High** | Command injection, severe attacks | Block |

## 🛠️ Common Commands

### Analyze Request
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"method":"GET","url":"/file.exe","headers":{},"client_ip":"1.2.3.4"}'
```

### Download Executable (triggers sandbox)
```bash
curl http://localhost:5000/malware.exe -o file.exe
```

### View Logs
```bash
curl http://localhost:5000/logs/executables
```

### Test XSS Detection
```bash
curl "http://localhost:5000/search?q=<script>alert('xss')</script>"
```

## 📁 Important Files

| File | Purpose |
|------|---------|
| `analyzer/http_analyzer.py` | Request analysis |
| `analyzer/request_classifier.py` | Request classification |
| `handler/response_handler.py` | Response generation |
| `handler/safe_executable_handler.py` | Safe executable handling |
| `shared/logs/executables/` | Sandboxed files |
| `HTTP_SIMULATION_GUIDE.md` | Full documentation |

## 🔍 Response Headers to Check

- `X-Simulated`: true (all responses)
- `X-Sandboxed`: true (safe fake executable)
- `X-Honeypot`: true (honeypot executable)
- `X-Category`: request category
- `X-Risk-Level`: low/medium/high
- `X-Request-ID`: unique tracking ID

## 🧪 Testing Scenarios

```bash
# 1. Normal static file
curl http://localhost:5000/style.css

# 2. Safe executable
curl http://localhost:5000/installer.exe

# 3. Suspicious executable
curl http://localhost:5000/backdoor.exe -H "User-Agent: Malware"

# 4. Path traversal attack
curl "http://localhost:5000/../../etc/passwd"

# 5. SQL injection
curl "http://localhost:5000/api?id=1' OR '1'='1"

# 6. API request
curl http://localhost:5000/api/v1/packages

# 7. Login simulation
curl http://localhost:5000/auth/login
```

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Connection refused | `docker-compose up` |
| Module import error | Check `__init__.py` files exist |
| Logs not written | Check `/logs` volume permissions |
| Port in use | Change port in `docker-compose.yml` |

## 📖 Full Documentation
See [HTTP_SIMULATION_GUIDE.md](HTTP_SIMULATION_GUIDE.md) for complete details.
