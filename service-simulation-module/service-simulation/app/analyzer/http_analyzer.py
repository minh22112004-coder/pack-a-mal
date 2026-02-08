"""
HTTP Request Analyzer
Phân tích các yêu cầu HTTP đến để trích xuất thông tin chi tiết
"""

import re
import json
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from typing import Dict, List, Optional, Any


class HTTPRequestAnalyzer:
    """
    Phân tích các yêu cầu HTTP để trích xuất thông tin như:
    - Method, URL, Headers
    - Query parameters
    - Body content
    - Client information
    - Potential security threats
    """
    
    def __init__(self):
        self.suspicious_patterns = [
            r'\.\./',  # Path traversal
            r'<script',  # XSS attempts
            r'union.*select',  # SQL injection
            r'cmd=',  # Command injection
            r'exec\(',  # Code execution
            r'eval\(',  # Code evaluation
        ]
        
        self.executable_extensions = [
            '.exe', '.dll', '.bat', '.cmd', '.ps1', '.sh',
            '.bin', '.elf', '.app', '.apk', '.jar',
            '.msi', '.deb', '.rpm', '.dmg'
        ]
    
    def analyze_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        body: Optional[str] = None,
        client_ip: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Phân tích một HTTP request và trả về thông tin chi tiết
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            headers: Request headers
            body: Request body (if any)
            client_ip: Client IP address
            
        Returns:
            Dict chứa thông tin phân tích chi tiết
        """
        parsed_url = urlparse(url)
        
        analysis = {
            'timestamp': datetime.utcnow().isoformat(),
            'method': method.upper(),
            'url': url,
            'parsed_url': {
                'scheme': parsed_url.scheme or 'http',
                'netloc': parsed_url.netloc,
                'path': parsed_url.path,
                'params': parsed_url.params,
                'query': parsed_url.query,
                'fragment': parsed_url.fragment
            },
            'query_params': parse_qs(parsed_url.query),
            'headers': headers,
            'body': body,
            'client_ip': client_ip,
            'content_type': headers.get('Content-Type', 'unknown'),
            'user_agent': headers.get('User-Agent', 'unknown'),
            'file_extension': self._get_file_extension(parsed_url.path),
            'is_executable_request': self._is_executable_request(parsed_url.path),
            'security_flags': self._check_security_flags(url, headers, body),
            'request_category': None  # Will be set by classifier
        }
        
        return analysis
    
    def _get_file_extension(self, path: str) -> Optional[str]:
        """Trích xuất phần mở rộng file từ path"""
        if '.' in path:
            return '.' + path.split('.')[-1].lower()
        return None
    
    def _is_executable_request(self, path: str) -> bool:
        """Kiểm tra xem request có yêu cầu tải file thực thi không"""
        ext = self._get_file_extension(path)
        return ext in self.executable_extensions if ext else False
    
    def _check_security_flags(
        self,
        url: str,
        headers: Dict[str, str],
        body: Optional[str]
    ) -> Dict[str, Any]:
        """
        Kiểm tra các dấu hiệu bảo mật đáng ngờ
        
        Returns:
            Dict chứa các cờ bảo mật và mức độ nguy hiểm
        """
        flags = {
            'suspicious_patterns_found': [],
            'risk_level': 'low',  # low, medium, high
            'has_path_traversal': False,
            'has_xss_attempt': False,
            'has_sql_injection': False,
            'has_command_injection': False,
            'unusual_headers': []
        }
        
        # Kiểm tra URL và body với các pattern đáng ngờ
        content_to_check = url
        if body:
            content_to_check += ' ' + body
        
        for pattern in self.suspicious_patterns:
            if re.search(pattern, content_to_check, re.IGNORECASE):
                flags['suspicious_patterns_found'].append(pattern)
                
                if 'traversal' in pattern or r'\.\.' in pattern:
                    flags['has_path_traversal'] = True
                elif 'script' in pattern:
                    flags['has_xss_attempt'] = True
                elif 'select' in pattern or 'union' in pattern:
                    flags['has_sql_injection'] = True
                elif 'cmd' in pattern or 'exec' in pattern:
                    flags['has_command_injection'] = True
        
        # Kiểm tra headers bất thường
        unusual_header_patterns = ['X-Forwarded-For', 'X-Custom', 'X-Hack']
        for header_key in headers:
            if any(pattern in header_key for pattern in unusual_header_patterns):
                flags['unusual_headers'].append(header_key)
        
        # Xác định mức độ nguy hiểm
        threat_count = len(flags['suspicious_patterns_found'])
        if threat_count >= 3 or flags['has_command_injection']:
            flags['risk_level'] = 'high'
        elif threat_count >= 1:
            flags['risk_level'] = 'medium'
        
        return flags
    
    def extract_download_info(self, analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Trích xuất thông tin về file download từ request
        
        Returns:
            Dict chứa thông tin về file download hoặc None
        """
        if not analysis['is_executable_request']:
            return None
        
        path = analysis['parsed_url']['path']
        filename = path.split('/')[-1] if '/' in path else path
        
        return {
            'filename': filename,
            'extension': analysis['file_extension'],
            'full_path': path,
            'is_safe': analysis['security_flags']['risk_level'] == 'low',
            'requires_sandboxing': analysis['is_executable_request']
        }
    
    def generate_summary(self, analysis: Dict[str, Any]) -> str:
        """Tạo tóm tắt ngắn gọn về request"""
        summary_parts = [
            f"{analysis['method']} request to {analysis['parsed_url']['path']}",
            f"from {analysis['client_ip'] or 'unknown'}",
        ]
        
        if analysis['is_executable_request']:
            summary_parts.append("(executable download)")
        
        risk = analysis['security_flags']['risk_level']
        if risk != 'low':
            summary_parts.append(f"[{risk.upper()} RISK]")
        
        return ' '.join(summary_parts)
