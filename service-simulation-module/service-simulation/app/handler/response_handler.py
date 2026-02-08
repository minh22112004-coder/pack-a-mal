"""
Response Handler
Tạo và trả về các phản hồi HTTP phù hợp dựa trên phân loại request
"""

import json
import base64
from typing import Dict, Any, Optional, Tuple
from datetime import datetime


class ResponseHandler:
    """
    Xử lý và tạo các HTTP response phù hợp với từng loại request
    """
    
    def __init__(self, safe_executable_handler=None):
        self.safe_executable_handler = safe_executable_handler
        self.response_templates = self._init_templates()
    
    def _init_templates(self) -> Dict[str, Any]:
        """Khởi tạo các template response"""
        return {
            'static_content': {
                'image': self._generate_placeholder_image,
                'stylesheet': self._generate_placeholder_css,
                'javascript': self._generate_placeholder_js,
                'font': self._generate_placeholder_font,
                'document': self._generate_placeholder_document
            },
            'api_call': self._generate_api_response,
            'authentication': self._generate_auth_response,
            'file_download': self._generate_file_response,
            'executable_download': self._generate_safe_executable_response,
            'upload': self._generate_upload_response,
            'malicious': self._generate_blocked_response,
            'unknown': self._generate_default_response
        }
    
    def generate_response(
        self,
        analysis: Dict[str, Any],
        classification: Dict[str, Any]
    ) -> Tuple[bytes, int, Dict[str, str]]:
        """
        Tạo HTTP response phù hợp
        
        Args:
            analysis: Kết quả phân tích từ HTTPRequestAnalyzer
            classification: Kết quả phân loại từ RequestClassifier
            
        Returns:
            Tuple (content, status_code, headers)
        """
        category = classification['category']
        sub_category = classification.get('sub_category')
        
        # Log request
        self._log_request(analysis, classification)
        
        # Xử lý theo recommended action
        action = classification['recommended_action']
        
        if action == 'block_and_log':
            return self._generate_blocked_response(analysis, classification)
        elif action == 'sandbox_and_serve':
            return self._generate_safe_executable_response(analysis, classification)
        elif action == 'serve_fake_auth':
            return self._generate_auth_response(analysis, classification)
        elif action == 'serve_json':
            return self._generate_api_response(analysis, classification)
        elif action == 'serve_static':
            handler = self.response_templates['static_content'].get(sub_category)
            if handler:
                return handler(analysis, classification)
            return self._generate_default_response(analysis, classification)
        elif action == 'serve_file':
            return self._generate_file_response(analysis, classification)
        elif action == 'accept_and_sandbox':
            return self._generate_upload_response(analysis, classification)
        else:
            return self._generate_default_response(analysis, classification)
    
    def _generate_placeholder_image(self, analysis, classification) -> Tuple[bytes, int, Dict]:
        """Tạo placeholder image"""
        # Simple 1x1 transparent PNG
        png_data = base64.b64decode(
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
        )
        headers = {
            'Content-Type': 'image/png',
            'Content-Length': str(len(png_data)),
            'Cache-Control': 'public, max-age=3600'
        }
        return png_data, 200, headers
    
    def _generate_placeholder_css(self, analysis, classification) -> Tuple[bytes, int, Dict]:
        """Tạo placeholder CSS"""
        css_content = "/* Simulated CSS file */\nbody { font-family: Arial, sans-serif; }"
        content = css_content.encode('utf-8')
        headers = {
            'Content-Type': 'text/css',
            'Content-Length': str(len(content))
        }
        return content, 200, headers
    
    def _generate_placeholder_js(self, analysis, classification) -> Tuple[bytes, int, Dict]:
        """Tạo placeholder JavaScript"""
        js_content = "/* Simulated JavaScript file */\nconsole.log('Simulated script loaded');"
        content = js_content.encode('utf-8')
        headers = {
            'Content-Type': 'application/javascript',
            'Content-Length': str(len(content))
        }
        return content, 200, headers
    
    def _generate_placeholder_font(self, analysis, classification) -> Tuple[bytes, int, Dict]:
        """Tạo placeholder font"""
        # Return empty binary data
        content = b''
        headers = {
            'Content-Type': 'font/woff2',
            'Content-Length': '0'
        }
        return content, 200, headers
    
    def _generate_placeholder_document(self, analysis, classification) -> Tuple[bytes, int, Dict]:
        """Tạo placeholder document"""
        doc_content = "Simulated document content.\n\nThis is a placeholder file."
        content = doc_content.encode('utf-8')
        headers = {
            'Content-Type': 'text/plain',
            'Content-Length': str(len(content)),
            'Content-Disposition': 'attachment; filename="document.txt"'
        }
        return content, 200, headers
    
    def _generate_api_response(self, analysis, classification) -> Tuple[bytes, int, Dict]:
        """Tạo API response giả"""
        response_data = {
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat(),
            'data': {
                'message': 'API simulation response',
                'request_path': analysis['parsed_url']['path'],
                'simulated': True
            }
        }
        
        content = json.dumps(response_data, indent=2).encode('utf-8')
        headers = {
            'Content-Type': 'application/json',
            'Content-Length': str(len(content))
        }
        return content, 200, headers
    
    def _generate_auth_response(self, analysis, classification) -> Tuple[bytes, int, Dict]:
        """Tạo authentication response giả"""
        if analysis['method'] == 'POST':
            # Fake successful login
            response_data = {
                'status': 'success',
                'message': 'Authentication successful',
                'token': 'fake_token_' + base64.b64encode(b'simulated').decode('utf-8'),
                'user': {
                    'id': 12345,
                    'username': 'simulated_user',
                    'email': 'user@simulated.local'
                }
            }
        else:
            # Return login form
            response_data = {
                'status': 'ready',
                'message': 'Please provide credentials',
                'fields': ['username', 'password']
            }
        
        content = json.dumps(response_data, indent=2).encode('utf-8')
        headers = {
            'Content-Type': 'application/json',
            'Content-Length': str(len(content))
        }
        return content, 200, headers
    
    def _generate_file_response(self, analysis, classification) -> Tuple[bytes, int, Dict]:
        """Tạo file download response"""
        path = analysis['parsed_url']['path']
        filename = path.split('/')[-1] if '/' in path else 'file.bin'
        
        # Tạo file giả với metadata
        file_content = f"Simulated file: {filename}\n".encode('utf-8')
        file_content += b"This is a safe simulated file content.\n"
        file_content += f"Requested at: {datetime.utcnow().isoformat()}\n".encode('utf-8')
        
        headers = {
            'Content-Type': 'application/octet-stream',
            'Content-Length': str(len(file_content)),
            'Content-Disposition': f'attachment; filename="{filename}"'
        }
        return file_content, 200, headers
    
    def _generate_safe_executable_response(self, analysis, classification) -> Tuple[bytes, int, Dict]:
        """Tạo safe executable response - delegate to SafeExecutableHandler"""
        if self.safe_executable_handler:
            return self.safe_executable_handler.handle_executable_request(analysis, classification)
        
        # Fallback: return safe placeholder
        warning = (
            "# EXECUTABLE FILE REQUEST DETECTED\n"
            f"# Requested file: {analysis['parsed_url']['path']}\n"
            f"# Extension: {analysis['file_extension']}\n"
            "# This is a safe placeholder. Actual executable not served.\n"
            "# For analysis purposes only.\n"
        ).encode('utf-8')
        
        headers = {
            'Content-Type': 'text/plain',
            'Content-Length': str(len(warning)),
            'X-Simulated': 'true',
            'X-Original-Type': 'executable'
        }
        return warning, 200, headers
    
    def _generate_upload_response(self, analysis, classification) -> Tuple[bytes, int, Dict]:
        """Tạo upload response"""
        response_data = {
            'status': 'success',
            'message': 'File upload accepted (sandboxed)',
            'upload_id': f'upload_{int(datetime.utcnow().timestamp())}',
            'sandboxed': True
        }
        
        content = json.dumps(response_data, indent=2).encode('utf-8')
        headers = {
            'Content-Type': 'application/json',
            'Content-Length': str(len(content))
        }
        return content, 200, headers
    
    def _generate_blocked_response(self, analysis, classification) -> Tuple[bytes, int, Dict]:
        """Tạo blocked response cho malicious requests"""
        response_data = {
            'error': 'Request blocked',
            'reason': 'Security policy violation',
            'risk_level': analysis['security_flags']['risk_level'],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        content = json.dumps(response_data, indent=2).encode('utf-8')
        headers = {
            'Content-Type': 'application/json',
            'Content-Length': str(len(content))
        }
        return content, 403, headers
    
    def _generate_default_response(self, analysis, classification) -> Tuple[bytes, int, Dict]:
        """Tạo default response"""
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Simulated Response</title>
</head>
<body>
    <h1>HTTP Simulation Service</h1>
    <p>This is a simulated response for analysis purposes.</p>
    <p>Request received and logged.</p>
</body>
</html>
"""
        content = html_content.encode('utf-8')
        headers = {
            'Content-Type': 'text/html',
            'Content-Length': str(len(content))
        }
        return content, 200, headers
    
    def _log_request(self, analysis: Dict[str, Any], classification: Dict[str, Any]):
        """Log request details"""
        log_entry = {
            'timestamp': analysis['timestamp'],
            'method': analysis['method'],
            'path': analysis['parsed_url']['path'],
            'category': classification['category'],
            'intent': classification['intent'],
            'risk_level': analysis['security_flags']['risk_level'],
            'client_ip': analysis['client_ip']
        }
        
        # TODO: Write to log file or database
        print(f"[HTTP-SIM] {json.dumps(log_entry)}")
