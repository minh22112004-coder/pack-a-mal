from flask import Flask, request, jsonify, make_response
import sys
import os

# Add parent directory to path to import analyzer and handler modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from analyzer.http_analyzer import HTTPRequestAnalyzer
from analyzer.request_classifier import RequestClassifier
from handler.response_handler import ResponseHandler
from handler.safe_executable_handler import SafeExecutableHandler

app = Flask(__name__)

# Initialize components
http_analyzer = HTTPRequestAnalyzer()
request_classifier = RequestClassifier()
safe_exec_handler = SafeExecutableHandler()
response_handler = ResponseHandler(safe_executable_handler=safe_exec_handler)

@app.route("/status")
def status():
    """Kiểm tra trạng thái service"""
    return {
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

@app.route("/analyze", methods=['POST'])
def analyze_request():
    """
    Phân tích một HTTP request (để testing/debugging)
    
    Body format:
    {
        "method": "GET",
        "url": "/path/to/resource",
        "headers": {...},
        "body": "...",
        "client_ip": "1.2.3.4"
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    # Phân tích request
    analysis = http_analyzer.analyze_request(
        method=data.get('method', 'GET'),
        url=data.get('url', '/'),
        headers=data.get('headers', {}),
        body=data.get('body'),
        client_ip=data.get('client_ip')
    )
    
    # Phân loại request
    classification = request_classifier.classify(analysis)
    analysis['request_category'] = classification['category']
    
    # Trả về kết quả phân tích
    result = {
        "analysis": analysis,
        "classification": classification,
        "summary": http_analyzer.generate_summary(analysis),
        "category_description": request_classifier.get_category_description(
            classification['category']
        )
    }
    
    return jsonify(result), 200

@app.route("/simulate", methods=['POST'])
def simulate_request():
    """
    Simulate một HTTP request và trả về response phù hợp
    
    Body format giống /analyze
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    # Phân tích request
    analysis = http_analyzer.analyze_request(
        method=data.get('method', 'GET'),
        url=data.get('url', '/'),
        headers=data.get('headers', {}),
        body=data.get('body'),
        client_ip=data.get('client_ip')
    )
    
    # Phân loại request
    classification = request_classifier.classify(analysis)
    analysis['request_category'] = classification['category']
    
    # Tạo response
    content, status_code, headers = response_handler.generate_response(
        analysis, classification
    )
    
    # Tạo Flask response
    response = make_response(content, status_code)
    for key, value in headers.items():
        response.headers[key] = value
    
    return response

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'])
def catch_all(path):
    """
    Catch-all route để xử lý mọi HTTP request
    Phân tích và trả về response phù hợp
    """
    # Xây dựng full URL
    full_url = request.url
    
    # Phân tích request
    analysis = http_analyzer.analyze_request(
        method=request.method,
        url=full_url,
        headers=dict(request.headers),
        body=request.get_data(as_text=True) if request.data else None,
        client_ip=request.remote_addr
    )
    
    # Phân loại request
    classification = request_classifier.classify(analysis)
    analysis['request_category'] = classification['category']
    
    # Tạo response
    content, status_code, headers = response_handler.generate_response(
        analysis, classification
    )
    
    # Tạo Flask response
    response = make_response(content, status_code)
    for key, value in headers.items():
        response.headers[key] = value
    
    # Thêm custom headers để tracking
    response.headers['X-Simulated'] = 'true'
    response.headers['X-Category'] = classification['category']
    response.headers['X-Risk-Level'] = analysis['security_flags']['risk_level']
    
    return response

@app.route("/stats")
def get_stats():
    """Lấy thống kê về các request đã xử lý"""
    # TODO: Implement statistics tracking
    return jsonify({
        "message": "Statistics endpoint",
        "note": "Statistics tracking to be implemented"
    }), 200

@app.route("/logs/executables")
def list_executable_logs():
    """Liệt kê các executable request đã được log"""
    try:
        sandbox_dir = safe_exec_handler.sandbox_dir
        log_file = os.path.join(sandbox_dir, 'executable_requests.log')
        
        if not os.path.exists(log_file):
            return jsonify({"logs": [], "count": 0}), 200
        
        logs = []
        with open(log_file, 'r') as f:
            for line in f:
                if line.strip():
                    logs.append(eval(line.strip()))  # Parse JSON line
        
        return jsonify({
            "logs": logs,
            "count": len(logs)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500