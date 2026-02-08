"""
Test Script cho HTTP Simulation System
Kiểm tra tất cả các tính năng chính
"""

import requests
import json
from typing import Dict, Any


class HTTPSimulationTester:
    """Test suite cho HTTP simulation system"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.test_results = []
    
    def run_test(self, name: str, test_func):
        """Execute một test và lưu kết quả"""
        print(f"\n{'='*60}")
        print(f"TEST: {name}")
        print(f"{'='*60}")
        
        try:
            result = test_func()
            self.test_results.append({
                'name': name,
                'status': 'PASSED',
                'result': result
            })
            print(f"✓ PASSED")
            return result
        except Exception as e:
            self.test_results.append({
                'name': name,
                'status': 'FAILED',
                'error': str(e)
            })
            print(f"✗ FAILED: {e}")
            return None
    
    def test_status(self):
        """Test 1: Kiểm tra status endpoint"""
        response = requests.get(f"{self.base_url}/status")
        assert response.status_code == 200
        data = response.json()
        assert data['service'] == 'http-simulation'
        assert data['status'] == 'running'
        print(f"Response: {json.dumps(data, indent=2)}")
        return data
    
    def test_static_content_css(self):
        """Test 2: Static content - CSS"""
        response = requests.get(f"{self.base_url}/styles/main.css")
        assert response.status_code == 200
        assert 'text/css' in response.headers['Content-Type']
        print(f"Content-Type: {response.headers['Content-Type']}")
        print(f"Content: {response.text[:100]}...")
        return response.text
    
    def test_static_content_image(self):
        """Test 3: Static content - Image"""
        response = requests.get(f"{self.base_url}/images/logo.png")
        assert response.status_code == 200
        assert 'image/png' in response.headers['Content-Type']
        print(f"Content-Type: {response.headers['Content-Type']}")
        print(f"Content-Length: {response.headers.get('Content-Length')} bytes")
        return len(response.content)
    
    def test_api_request(self):
        """Test 4: API request"""
        response = requests.get(f"{self.base_url}/api/v1/users")
        assert response.status_code == 200
        assert 'application/json' in response.headers['Content-Type']
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        return data
    
    def test_executable_download_low_risk(self):
        """Test 5: Executable download - Low risk"""
        response = requests.get(f"{self.base_url}/download/installer.exe")
        assert response.status_code == 200
        assert response.headers.get('X-Simulated') == 'true'
        assert response.headers.get('X-Sandboxed') == 'true'
        print(f"Headers: {dict(response.headers)}")
        print(f"Content preview: {response.content[:200]}...")
        return response.headers
    
    def test_executable_download_medium_risk(self):
        """Test 6: Executable download - Medium risk"""
        response = requests.get(
            f"{self.base_url}/backdoor.exe",
            headers={'User-Agent': 'SuspiciousAgent/1.0'}
        )
        assert response.status_code == 200
        assert response.headers.get('X-Honeypot') == 'true'
        print(f"Headers: {dict(response.headers)}")
        print(f"Content preview: {response.content[:200]}...")
        return response.headers
    
    def test_malicious_request_xss(self):
        """Test 7: Malicious request - XSS attempt"""
        response = requests.get(
            f"{self.base_url}/search",
            params={'q': '<script>alert("xss")</script>'}
        )
        assert response.status_code in [200, 403]  # May be blocked or served
        print(f"Status: {response.status_code}")
        print(f"Risk-Level: {response.headers.get('X-Risk-Level')}")
        return response.status_code
    
    def test_malicious_request_path_traversal(self):
        """Test 8: Malicious request - Path traversal"""
        response = requests.get(f"{self.base_url}/download/../../../etc/passwd")
        assert response.status_code in [200, 403]
        print(f"Status: {response.status_code}")
        print(f"Risk-Level: {response.headers.get('X-Risk-Level')}")
        return response.status_code
    
    def test_analyze_endpoint(self):
        """Test 9: /analyze endpoint"""
        test_request = {
            "method": "GET",
            "url": "/download/malware.exe",
            "headers": {
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/octet-stream"
            },
            "client_ip": "192.168.1.100"
        }
        
        response = requests.post(
            f"{self.base_url}/analyze",
            json=test_request
        )
        assert response.status_code == 200
        data = response.json()
        
        print(f"Category: {data['classification']['category']}")
        print(f"Intent: {data['classification']['intent']}")
        print(f"Risk Level: {data['analysis']['security_flags']['risk_level']}")
        print(f"Summary: {data['summary']}")
        
        return data
    
    def test_simulate_endpoint(self):
        """Test 10: /simulate endpoint"""
        test_request = {
            "method": "POST",
            "url": "/api/login",
            "headers": {
                "Content-Type": "application/json"
            },
            "body": '{"username":"test","password":"test123"}',
            "client_ip": "10.0.0.1"
        }
        
        response = requests.post(
            f"{self.base_url}/simulate",
            json=test_request
        )
        assert response.status_code == 200
        
        print(f"Content-Type: {response.headers['Content-Type']}")
        if 'application/json' in response.headers['Content-Type']:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Response: {response.text[:200]}...")
        
        return response.text
    
    def test_authentication_request(self):
        """Test 11: Authentication request"""
        response = requests.get(f"{self.base_url}/auth/login")
        assert response.status_code == 200
        assert response.headers.get('X-Category') == 'authentication'
        
        data = response.json() if 'application/json' in response.headers['Content-Type'] else None
        if data:
            print(f"Response: {json.dumps(data, indent=2)}")
        
        return data
    
    def test_file_upload_simulation(self):
        """Test 12: File upload"""
        # Simulate POST request for upload
        test_request = {
            "method": "POST",
            "url": "/upload/file",
            "headers": {
                "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundary"
            },
            "body": "file content here",
            "client_ip": "172.16.0.5"
        }
        
        response = requests.post(
            f"{self.base_url}/analyze",
            json=test_request
        )
        assert response.status_code == 200
        data = response.json()
        
        print(f"Category: {data['classification']['category']}")
        print(f"Recommended Action: {data['classification']['recommended_action']}")
        
        return data
    
    def run_all_tests(self):
        """Chạy tất cả các tests"""
        print("\n" + "="*60)
        print("HTTP SIMULATION SYSTEM - TEST SUITE")
        print("="*60)
        
        self.run_test("Status Check", self.test_status)
        self.run_test("Static Content - CSS", self.test_static_content_css)
        self.run_test("Static Content - Image", self.test_static_content_image)
        self.run_test("API Request", self.test_api_request)
        self.run_test("Executable Download - Low Risk", self.test_executable_download_low_risk)
        self.run_test("Executable Download - Medium Risk", self.test_executable_download_medium_risk)
        self.run_test("Malicious Request - XSS", self.test_malicious_request_xss)
        self.run_test("Malicious Request - Path Traversal", self.test_malicious_request_path_traversal)
        self.run_test("Analyze Endpoint", self.test_analyze_endpoint)
        self.run_test("Simulate Endpoint", self.test_simulate_endpoint)
        self.run_test("Authentication Request", self.test_authentication_request)
        self.run_test("File Upload Simulation", self.test_file_upload_simulation)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """In tóm tắt kết quả tests"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['status'] == 'PASSED')
        failed = total - passed
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✓")
        print(f"Failed: {failed} ✗")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        if failed > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if result['status'] == 'FAILED':
                    print(f"  - {result['name']}: {result.get('error')}")
        
        print("="*60 + "\n")


def main():
    """Main function"""
    import sys
    
    # Check if custom URL provided
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    print(f"Testing HTTP Simulation System at: {base_url}")
    
    # Create tester and run
    tester = HTTPSimulationTester(base_url)
    tester.run_all_tests()


if __name__ == "__main__":
    main()
