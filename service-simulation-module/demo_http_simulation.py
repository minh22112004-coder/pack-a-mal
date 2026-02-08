"""
Demo Script - HTTP Simulation System
Demonstrating key features with examples
"""

import requests
import json
from time import sleep


def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def demo_1_status_check():
    """Demo 1: Check service status"""
    print_section("DEMO 1: Service Status Check")
    
    response = requests.get("http://localhost:5000/status")
    data = response.json()
    
    print("Endpoint: GET /status")
    print(f"Status Code: {response.status_code}")
    print(f"\nResponse:")
    print(json.dumps(data, indent=2))
    
    print(f"\n✓ Service is running with features:")
    for feature in data['features']:
        print(f"  - {feature}")


def demo_2_analyze_executable():
    """Demo 2: Analyze an executable download request"""
    print_section("DEMO 2: Analyze Executable Download Request")
    
    test_request = {
        "method": "GET",
        "url": "/download/suspicious_tool.exe",
        "headers": {
            "User-Agent": "Wget/1.20",
            "Accept": "application/octet-stream"
        },
        "client_ip": "192.168.100.50"
    }
    
    print("Request to analyze:")
    print(json.dumps(test_request, indent=2))
    
    response = requests.post(
        "http://localhost:5000/analyze",
        json=test_request
    )
    
    data = response.json()
    
    print(f"\n{'─'*70}")
    print("Analysis Result:")
    print(f"{'─'*70}")
    print(f"Category: {data['classification']['category']}")
    print(f"Sub-category: {data['classification']['sub_category']}")
    print(f"Intent: {data['classification']['intent']}")
    print(f"Confidence: {data['classification']['confidence']*100}%")
    print(f"Risk Level: {data['analysis']['security_flags']['risk_level'].upper()}")
    print(f"Recommended Action: {data['classification']['recommended_action']}")
    print(f"\nSummary: {data['summary']}")
    
    print(f"\n✓ Request analyzed successfully")


def demo_3_simulate_safe_download():
    """Demo 3: Simulate safe executable download"""
    print_section("DEMO 3: Simulate Safe Executable Download")
    
    url = "http://localhost:5000/tools/installer.exe"
    print(f"Downloading: {url}")
    
    response = requests.get(url)
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"\nResponse Headers:")
    print(f"  Content-Type: {response.headers.get('Content-Type')}")
    print(f"  X-Simulated: {response.headers.get('X-Simulated')}")
    print(f"  X-Sandboxed: {response.headers.get('X-Sandboxed')}")
    print(f"  X-Category: {response.headers.get('X-Category')}")
    print(f"  X-Risk-Level: {response.headers.get('X-Risk-Level')}")
    
    print(f"\nContent Preview (first 200 bytes):")
    print(response.content[:200])
    
    print(f"\n✓ Safe executable served from sandbox")


def demo_4_honeypot_executable():
    """Demo 4: Trigger honeypot for suspicious request"""
    print_section("DEMO 4: Honeypot Executable for Suspicious Request")
    
    url = "http://localhost:5000/malware/backdoor.exe"
    headers = {
        "User-Agent": "Malicious-Bot/1.0",
        "X-Custom-Header": "suspicious-value"
    }
    
    print(f"Downloading: {url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    
    response = requests.get(url, headers=headers)
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"\nResponse Headers:")
    print(f"  X-Honeypot: {response.headers.get('X-Honeypot')}")
    print(f"  X-Tracking-Enabled: {response.headers.get('X-Tracking-Enabled')}")
    print(f"  X-Request-ID: {response.headers.get('X-Request-ID')}")
    print(f"  X-Risk-Level: {response.headers.get('X-Risk-Level')}")
    
    print(f"\nContent Preview (first 300 bytes):")
    print(response.content[:300])
    
    print(f"\n✓ Honeypot executable served with tracking")


def demo_5_malicious_request():
    """Demo 5: Detect and block malicious request"""
    print_section("DEMO 5: Detect Malicious Request")
    
    # XSS attempt
    url = "http://localhost:5000/search?q=<script>alert('XSS')</script>"
    
    print(f"Malicious URL: {url}")
    print("Attack Type: XSS (Cross-Site Scripting)")
    
    response = requests.get(url)
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Risk Level: {response.headers.get('X-Risk-Level')}")
    print(f"Category: {response.headers.get('X-Category')}")
    
    if response.status_code == 403:
        print(f"\nResponse:")
        print(json.dumps(response.json(), indent=2))
        print(f"\n✓ Malicious request blocked")
    else:
        print(f"\n✓ Malicious request detected and logged")


def demo_6_api_simulation():
    """Demo 6: API endpoint simulation"""
    print_section("DEMO 6: API Endpoint Simulation")
    
    url = "http://localhost:5000/api/v1/packages/info"
    
    print(f"API Request: GET {url}")
    
    response = requests.get(url)
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nResponse:")
        print(json.dumps(data, indent=2))
        print(f"\n✓ API response generated successfully")


def demo_7_auth_simulation():
    """Demo 7: Authentication simulation"""
    print_section("DEMO 7: Authentication Endpoint Simulation")
    
    # GET login page
    print("Step 1: GET /auth/login")
    response = requests.get("http://localhost:5000/auth/login")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
    
    # POST login
    print("\nStep 2: Simulate POST login")
    test_request = {
        "method": "POST",
        "url": "/auth/login",
        "headers": {"Content-Type": "application/json"},
        "body": '{"username":"admin","password":"password123"}',
        "client_ip": "10.0.0.1"
    }
    
    response = requests.post(
        "http://localhost:5000/simulate",
        json=test_request
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
    
    print(f"\n✓ Fake authentication successful")


def demo_8_view_logs():
    """Demo 8: View executable request logs"""
    print_section("DEMO 8: View Executable Request Logs")
    
    response = requests.get("http://localhost:5000/logs/executables")
    
    data = response.json()
    
    print(f"Total Executable Requests Logged: {data['count']}")
    
    if data['count'] > 0:
        print(f"\nRecent Logs:")
        for i, log in enumerate(data['logs'][-5:], 1):  # Last 5
            print(f"\n  [{i}] Request ID: {log.get('request_id', 'N/A')}")
            print(f"      Filename: {log.get('filename', 'N/A')}")
            print(f"      Platform: {log.get('platform', 'N/A')}")
            print(f"      Risk Level: {log.get('risk_level', 'N/A')}")
            print(f"      Client IP: {log.get('client_ip', 'N/A')}")
            print(f"      Timestamp: {log.get('timestamp', 'N/A')}")
    
    print(f"\n✓ Logs retrieved successfully")


def demo_9_static_content():
    """Demo 9: Static content serving"""
    print_section("DEMO 9: Static Content Serving")
    
    static_files = [
        ("/styles/main.css", "CSS"),
        ("/scripts/app.js", "JavaScript"),
        ("/images/logo.png", "Image"),
        ("/fonts/roboto.woff2", "Font")
    ]
    
    for path, file_type in static_files:
        url = f"http://localhost:5000{path}"
        response = requests.get(url)
        
        print(f"{file_type:12} {path}")
        print(f"             Status: {response.status_code}, " + 
              f"Type: {response.headers.get('Content-Type')}, " +
              f"Size: {len(response.content)} bytes")
    
    print(f"\n✓ All static content served successfully")


def run_all_demos():
    """Run all demonstrations"""
    demos = [
        ("Service Status", demo_1_status_check),
        ("Analyze Executable Request", demo_2_analyze_executable),
        ("Safe Executable Download", demo_3_simulate_safe_download),
        ("Honeypot Executable", demo_4_honeypot_executable),
        ("Malicious Request Detection", demo_5_malicious_request),
        ("API Simulation", demo_6_api_simulation),
        ("Authentication Simulation", demo_7_auth_simulation),
        ("View Logs", demo_8_view_logs),
        ("Static Content", demo_9_static_content)
    ]
    
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*15 + "HTTP SIMULATION SYSTEM - DEMO" + " "*24 + "║")
    print("╚" + "="*68 + "╝")
    
    for i, (name, demo_func) in enumerate(demos, 1):
        try:
            demo_func()
            sleep(0.5)  # Small pause between demos
        except Exception as e:
            print(f"\n✗ Error in demo: {e}")
    
    print_section("✓ ALL DEMOS COMPLETED")
    print("Thank you for exploring the HTTP Simulation System!")
    print("\nFor more information, see: HTTP_SIMULATION_GUIDE.md")


if __name__ == "__main__":
    import sys
    
    try:
        # Check if service is running
        requests.get("http://localhost:5000/status", timeout=2)
        
        # Run demos
        run_all_demos()
        
    except requests.exceptions.ConnectionError:
        print("\n" + "="*70)
        print("ERROR: Cannot connect to HTTP Simulation Service")
        print("="*70)
        print("\nPlease ensure the service is running:")
        print("  1. cd service-simulation-module")
        print("  2. docker-compose up")
        print("\nThen run this demo script again.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        sys.exit(0)
