"""
Request Classifier
Phân loại yêu cầu HTTP dựa trên mục đích và nội dung
"""

from typing import Dict, Any, List
import re


class RequestClassifier:
    """
    Phân loại các HTTP request thành các loại khác nhau
    dựa trên URL pattern, headers, và nội dung
    """
    
    # Định nghĩa các loại request
    CATEGORY_STATIC_CONTENT = 'static_content'
    CATEGORY_API_CALL = 'api_call'
    CATEGORY_FILE_DOWNLOAD = 'file_download'
    CATEGORY_EXECUTABLE_DOWNLOAD = 'executable_download'
    CATEGORY_UPLOAD = 'upload'
    CATEGORY_AUTHENTICATION = 'authentication'
    CATEGORY_DATA_EXFILTRATION = 'data_exfiltration'
    CATEGORY_MALICIOUS = 'malicious'
    CATEGORY_UNKNOWN = 'unknown'
    
    def __init__(self):
        # Patterns cho các loại static content
        self.static_patterns = {
            'image': [r'\.(jpg|jpeg|png|gif|svg|ico|webp)$'],
            'stylesheet': [r'\.css$'],
            'javascript': [r'\.js$'],
            'font': [r'\.(woff|woff2|ttf|eot)$'],
            'document': [r'\.(pdf|txt|doc|docx)$']
        }
        
        # Patterns cho API endpoints
        self.api_patterns = [
            r'/api/',
            r'/v\d+/',  # versioned APIs
            r'\.json$',
            r'/graphql',
            r'/rest/'
        ]
        
        # Patterns cho authentication
        self.auth_patterns = [
            r'/login',
            r'/auth',
            r'/signin',
            r'/oauth',
            r'/token'
        ]
        
        # Patterns cho data exfiltration (đáng ngờ)
        self.exfiltration_patterns = [
            r'/upload.*\.php',
            r'/backdoor',
            r'/shell',
            r'/c2',  # Command & Control
            r'/beacon'
        ]
    
    def classify(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phân loại request dựa trên thông tin phân tích
        
        Args:
            analysis: Dict từ HTTPRequestAnalyzer
            
        Returns:
            Dict chứa phân loại và độ tin cậy
        """
        path = analysis['parsed_url']['path'].lower()
        method = analysis['method']
        headers = analysis['headers']
        
        classification = {
            'category': self.CATEGORY_UNKNOWN,
            'sub_category': None,
            'confidence': 0.0,
            'intent': 'unknown',
            'recommended_action': 'monitor'
        }
        
        # Kiểm tra theo thứ tự ưu tiên
        
        # 1. Kiểm tra executable download
        if analysis['is_executable_request']:
            classification.update({
                'category': self.CATEGORY_EXECUTABLE_DOWNLOAD,
                'sub_category': analysis['file_extension'],
                'confidence': 0.95,
                'intent': 'download_executable',
                'recommended_action': 'sandbox_and_serve'
            })
            return classification
        
        # 2. Kiểm tra malicious patterns
        if analysis['security_flags']['risk_level'] == 'high':
            classification.update({
                'category': self.CATEGORY_MALICIOUS,
                'sub_category': 'high_risk',
                'confidence': 0.9,
                'intent': 'attack_attempt',
                'recommended_action': 'block_and_log'
            })
            return classification
        
        # 3. Kiểm tra data exfiltration
        for pattern in self.exfiltration_patterns:
            if re.search(pattern, path, re.IGNORECASE):
                classification.update({
                    'category': self.CATEGORY_DATA_EXFILTRATION,
                    'sub_category': 'suspicious_endpoint',
                    'confidence': 0.85,
                    'intent': 'potential_exfiltration',
                    'recommended_action': 'log_and_monitor'
                })
                return classification
        
        # 4. Kiểm tra authentication
        for pattern in self.auth_patterns:
            if re.search(pattern, path, re.IGNORECASE):
                classification.update({
                    'category': self.CATEGORY_AUTHENTICATION,
                    'sub_category': 'login_attempt',
                    'confidence': 0.9,
                    'intent': 'authenticate',
                    'recommended_action': 'serve_fake_auth'
                })
                return classification
        
        # 5. Kiểm tra upload
        if method == 'POST' and ('multipart/form-data' in headers.get('Content-Type', '')):
            classification.update({
                'category': self.CATEGORY_UPLOAD,
                'sub_category': 'file_upload',
                'confidence': 0.9,
                'intent': 'upload_file',
                'recommended_action': 'accept_and_sandbox'
            })
            return classification
        
        # 6. Kiểm tra API calls
        for pattern in self.api_patterns:
            if re.search(pattern, path, re.IGNORECASE):
                classification.update({
                    'category': self.CATEGORY_API_CALL,
                    'sub_category': self._detect_api_type(path),
                    'confidence': 0.85,
                    'intent': 'api_request',
                    'recommended_action': 'serve_json'
                })
                return classification
        
        # 7. Kiểm tra static content
        static_type = self._detect_static_type(path)
        if static_type:
            classification.update({
                'category': self.CATEGORY_STATIC_CONTENT,
                'sub_category': static_type,
                'confidence': 0.95,
                'intent': 'fetch_resource',
                'recommended_action': 'serve_static'
            })
            return classification
        
        # 8. Kiểm tra file download
        if method == 'GET' and self._is_download_request(path, headers):
            classification.update({
                'category': self.CATEGORY_FILE_DOWNLOAD,
                'sub_category': 'general_download',
                'confidence': 0.8,
                'intent': 'download_file',
                'recommended_action': 'serve_file'
            })
            return classification
        
        # Default: unknown
        classification.update({
            'category': self.CATEGORY_UNKNOWN,
            'sub_category': None,
            'confidence': 0.5,
            'intent': 'unknown',
            'recommended_action': 'serve_default'
        })
        
        return classification
    
    def _detect_static_type(self, path: str) -> str:
        """Phát hiện loại static content"""
        for content_type, patterns in self.static_patterns.items():
            for pattern in patterns:
                if re.search(pattern, path, re.IGNORECASE):
                    return content_type
        return None
    
    def _detect_api_type(self, path: str) -> str:
        """Phát hiện loại API"""
        if 'graphql' in path.lower():
            return 'graphql'
        elif 'rest' in path.lower():
            return 'rest'
        elif '.json' in path.lower():
            return 'json'
        elif re.search(r'/v\d+/', path):
            return 'versioned_rest'
        else:
            return 'generic'
    
    def _is_download_request(self, path: str, headers: Dict[str, str]) -> bool:
        """Kiểm tra xem có phải download request không"""
        # Kiểm tra path có chứa /download/ hoặc file extension
        if '/download' in path.lower():
            return True
        
        # Kiểm tra Accept header
        accept = headers.get('Accept', '')
        if 'application/octet-stream' in accept:
            return True
        
        # Kiểm tra có extension nhưng không phải static content
        if '.' in path and not self._detect_static_type(path):
            return True
        
        return False
    
    def get_category_description(self, category: str) -> str:
        """Trả về mô tả chi tiết về category"""
        descriptions = {
            self.CATEGORY_STATIC_CONTENT: "Static resource request (images, CSS, JS, fonts)",
            self.CATEGORY_API_CALL: "API endpoint call",
            self.CATEGORY_FILE_DOWNLOAD: "General file download request",
            self.CATEGORY_EXECUTABLE_DOWNLOAD: "Executable file download (potentially dangerous)",
            self.CATEGORY_UPLOAD: "File upload request",
            self.CATEGORY_AUTHENTICATION: "Authentication/login attempt",
            self.CATEGORY_DATA_EXFILTRATION: "Suspicious data exfiltration attempt",
            self.CATEGORY_MALICIOUS: "Potentially malicious request",
            self.CATEGORY_UNKNOWN: "Unknown request type"
        }
        return descriptions.get(category, "No description available")
