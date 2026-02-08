"""
Safe Executable Handler
Xử lý an toàn các yêu cầu tải file thực thi
"""

import os
import hashlib
import json
from typing import Dict, Any, Tuple, Optional
from datetime import datetime
import base64


class SafeExecutableHandler:
    """
    Xử lý an toàn các yêu cầu tải file thực thi bằng cách:
    1. Tạo file giả lưu đến sandbox thay vì file thực
    2. Log chi tiết về yêu cầu để phân tích
    3. Trả về response an toàn cho mục đích phân tích
    """
    
    def __init__(self, sandbox_dir: str = '/logs/executables'):
        self.sandbox_dir = sandbox_dir
        self._ensure_sandbox_dir()
        
        # Executable signatures (các đặc trưng nhận dạng)
        self.executable_signatures = {
            '.exe': {
                'magic_bytes': b'MZ',  # DOS/Windows executable
                'mime_type': 'application/x-msdownload',
                'platform': 'windows'
            },
            '.dll': {
                'magic_bytes': b'MZ',
                'mime_type': 'application/x-msdownload',
                'platform': 'windows'
            },
            '.elf': {
                'magic_bytes': b'\x7fELF',
                'mime_type': 'application/x-elf',
                'platform': 'linux'
            },
            '.sh': {
                'magic_bytes': b'#!/bin/',
                'mime_type': 'application/x-sh',
                'platform': 'unix'
            },
            '.bat': {
                'magic_bytes': b'@echo',
                'mime_type': 'application/x-bat',
                'platform': 'windows'
            },
            '.ps1': {
                'magic_bytes': b'#',
                'mime_type': 'application/x-powershell',
                'platform': 'windows'
            },
            '.apk': {
                'magic_bytes': b'PK\x03\x04',  # ZIP-based
                'mime_type': 'application/vnd.android.package-archive',
                'platform': 'android'
            },
            '.jar': {
                'magic_bytes': b'PK\x03\x04',  # ZIP-based
                'mime_type': 'application/java-archive',
                'platform': 'java'
            }
        }
    
    def _ensure_sandbox_dir(self):
        """Đảm bảo thư mục sandbox tồn tại"""
        os.makedirs(self.sandbox_dir, exist_ok=True)
    
    def handle_executable_request(
        self,
        analysis: Dict[str, Any],
        classification: Dict[str, Any]
    ) -> Tuple[bytes, int, Dict[str, str]]:
        """
        Xử lý yêu cầu tải file thực thi một cách an toàn
        
        Args:
            analysis: Kết quả phân tích request
            classification: Kết quả phân loại request
            
        Returns:
            Tuple (content, status_code, headers)
        """
        file_ext = analysis['file_extension']
        path = analysis['parsed_url']['path']
        filename = path.split('/')[-1] if '/' in path else 'executable.bin'
        
        # Tạo metadata chi tiết về request
        metadata = self._create_metadata(analysis, classification, filename)
        
        # Quyết định chiến lược phản hồi
        strategy = self._determine_response_strategy(analysis, metadata)
        
        if strategy == 'sandbox_fake':
            return self._serve_sandboxed_fake(metadata, file_ext)
        elif strategy == 'honeypot':
            return self._serve_honeypot_executable(metadata, file_ext)
        elif strategy == 'block':
            return self._serve_blocked_response(metadata)
        else:
            return self._serve_safe_placeholder(metadata, file_ext)
    
    def _create_metadata(
        self,
        analysis: Dict[str, Any],
        classification: Dict[str, Any],
        filename: str
    ) -> Dict[str, Any]:
        """Tạo metadata chi tiết về executable request"""
        metadata = {
            'request_id': self._generate_request_id(analysis),
            'timestamp': datetime.utcnow().isoformat(),
            'filename': filename,
            'extension': analysis['file_extension'],
            'full_path': analysis['parsed_url']['path'],
            'client_ip': analysis['client_ip'],
            'user_agent': analysis['user_agent'],
            'method': analysis['method'],
            'headers': analysis['headers'],
            'query_params': analysis['query_params'],
            'category': classification['category'],
            'intent': classification['intent'],
            'risk_assessment': {
                'level': analysis['security_flags']['risk_level'],
                'flags': analysis['security_flags'],
                'is_suspicious': analysis['security_flags']['risk_level'] != 'low'
            },
            'platform': self._detect_platform(analysis['file_extension']),
            'handling_strategy': None  # Will be set later
        }
        
        # Log metadata
        self._log_executable_request(metadata)
        
        return metadata
    
    def _generate_request_id(self, analysis: Dict[str, Any]) -> str:
        """Tạo unique ID cho request"""
        data = f"{analysis['timestamp']}{analysis['url']}{analysis['client_ip']}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _detect_platform(self, file_ext: str) -> str:
        """Phát hiện platform dựa trên file extension"""
        sig = self.executable_signatures.get(file_ext, {})
        return sig.get('platform', 'unknown')
    
    def _determine_response_strategy(
        self,
        analysis: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> str:
        """
        Xác định chiến lược phản hồi dựa trên risk level
        
        Returns:
            'sandbox_fake': Trả về file giả an toàn
            'honeypot': Trả về honeypot executable để thu thập thêm thông tin
            'block': Block request
            'placeholder': Trả về placeholder
        """
        risk_level = metadata['risk_assessment']['level']
        
        if risk_level == 'high':
            # High risk: block hoặc honeypot
            if metadata['risk_assessment']['flags'].get('has_command_injection'):
                return 'block'
            else:
                return 'honeypot'
        elif risk_level == 'medium':
            # Medium risk: honeypot để gather intelligence
            return 'honeypot'
        else:
            # Low risk: serve safe fake
            return 'sandbox_fake'
    
    def _serve_sandboxed_fake(
        self,
        metadata: Dict[str, Any],
        file_ext: str
    ) -> Tuple[bytes, int, Dict[str, str]]:
        """
        Tạo và trả về file giả an toàn
        File này chỉ chứa metadata và marker, không có code thực thi
        """
        metadata['handling_strategy'] = 'sandbox_fake'
        
        # Tạo fake executable content
        fake_content = self._generate_fake_executable(metadata, file_ext)
        
        # Lưu vào sandbox để phân tích sau
        self._save_to_sandbox(metadata, fake_content)
        
        # Get signature info
        sig = self.executable_signatures.get(file_ext, {})
        mime_type = sig.get('mime_type', 'application/octet-stream')
        
        headers = {
            'Content-Type': mime_type,
            'Content-Length': str(len(fake_content)),
            'Content-Disposition': f'attachment; filename="{metadata["filename"]}"',
            'X-Simulated': 'true',
            'X-Sandboxed': 'true',
            'X-Request-ID': metadata['request_id'],
            'X-Platform': metadata['platform']
        }
        
        return fake_content, 200, headers
    
    def _serve_honeypot_executable(
        self,
        metadata: Dict[str, Any],
        file_ext: str
    ) -> Tuple[bytes, int, Dict[str, str]]:
        """
        Trả về honeypot executable - file có thể tracking được
        """
        metadata['handling_strategy'] = 'honeypot'
        
        # Tạo honeypot content với tracking code
        honeypot_content = self._generate_honeypot_executable(metadata, file_ext)
        
        # Lưu vào sandbox
        self._save_to_sandbox(metadata, honeypot_content)
        
        sig = self.executable_signatures.get(file_ext, {})
        mime_type = sig.get('mime_type', 'application/octet-stream')
        
        headers = {
            'Content-Type': mime_type,
            'Content-Length': str(len(honeypot_content)),
            'Content-Disposition': f'attachment; filename="{metadata["filename"]}"',
            'X-Simulated': 'true',
            'X-Honeypot': 'true',
            'X-Request-ID': metadata['request_id'],
            'X-Tracking-Enabled': 'true'
        }
        
        return honeypot_content, 200, headers
    
    def _serve_blocked_response(
        self,
        metadata: Dict[str, Any]
    ) -> Tuple[bytes, int, Dict[str, str]]:
        """Trả về blocked response"""
        metadata['handling_strategy'] = 'blocked'
        
        error_data = {
            'error': 'Executable download blocked',
            'reason': 'High-risk request detected',
            'request_id': metadata['request_id'],
            'timestamp': metadata['timestamp']
        }
        
        content = json.dumps(error_data, indent=2).encode('utf-8')
        
        headers = {
            'Content-Type': 'application/json',
            'Content-Length': str(len(content))
        }
        
        return content, 403, headers
    
    def _serve_safe_placeholder(
        self,
        metadata: Dict[str, Any],
        file_ext: str
    ) -> Tuple[bytes, int, Dict[str, str]]:
        """Trả về safe placeholder"""
        metadata['handling_strategy'] = 'placeholder'
        
        placeholder = self._generate_fake_executable(metadata, file_ext)
        
        headers = {
            'Content-Type': 'text/plain',
            'Content-Length': str(len(placeholder)),
            'X-Simulated': 'true',
            'X-Placeholder': 'true'
        }
        
        return placeholder, 200, headers
    
    def _generate_fake_executable(
        self,
        metadata: Dict[str, Any],
        file_ext: str
    ) -> bytes:
        """Tạo fake executable content"""
        sig = self.executable_signatures.get(file_ext, {})
        magic_bytes = sig.get('magic_bytes', b'FAKE')
        
        # Create minimal fake structure
        fake_content = magic_bytes
        
        # Add metadata as comment/data section
        metadata_section = f"\n# SIMULATED EXECUTABLE\n"
        metadata_section += f"# Request ID: {metadata['request_id']}\n"
        metadata_section += f"# Timestamp: {metadata['timestamp']}\n"
        metadata_section += f"# Original file: {metadata['filename']}\n"
        metadata_section += f"# Platform: {metadata['platform']}\n"
        metadata_section += f"# SAFE FOR ANALYSIS - NO REAL CODE\n"
        
        fake_content += metadata_section.encode('utf-8')
        
        return fake_content
    
    def _generate_honeypot_executable(
        self,
        metadata: Dict[str, Any],
        file_ext: str
    ) -> bytes:
        """
        Tạo honeypot executable với tracking capabilities
        Đây là file an toàn nhưng có thể tracking hành vi
        """
        sig = self.executable_signatures.get(file_ext, {})
        magic_bytes = sig.get('magic_bytes', b'HPOT')
        
        # Create honeypot structure
        honeypot_content = magic_bytes
        
        # Add tracking code (as comments/data - not actual code)
        tracking_section = f"\n# HONEYPOT EXECUTABLE\n"
        tracking_section += f"# Tracking ID: {metadata['request_id']}\n"
        tracking_section += f"# Callback URL: http://tracking.simulated.local/callback\n"
        tracking_section += f"# This file is instrumented for behavior analysis\n"
        tracking_section += f"# All execution attempts will be logged\n"
        
        honeypot_content += tracking_section.encode('utf-8')
        
        # Add base64-encoded metadata
        metadata_json = json.dumps(metadata, indent=2)
        metadata_b64 = base64.b64encode(metadata_json.encode('utf-8'))
        honeypot_content += b'\n# METADATA: ' + metadata_b64 + b'\n'
        
        return honeypot_content
    
    def _save_to_sandbox(self, metadata: Dict[str, Any], content: bytes):
        """Lưu file và metadata vào sandbox"""
        # Save file content
        file_path = os.path.join(
            self.sandbox_dir,
            f"{metadata['request_id']}_{metadata['filename']}"
        )
        
        try:
            with open(file_path, 'wb') as f:
                f.write(content)
            
            # Save metadata
            metadata_path = file_path + '.metadata.json'
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            print(f"[ERROR] Failed to save to sandbox: {e}")
    
    def _log_executable_request(self, metadata: Dict[str, Any]):
        """Log executable request"""
        log_entry = {
            'type': 'executable_request',
            'request_id': metadata['request_id'],
            'timestamp': metadata['timestamp'],
            'filename': metadata['filename'],
            'extension': metadata['extension'],
            'platform': metadata['platform'],
            'client_ip': metadata['client_ip'],
            'risk_level': metadata['risk_assessment']['level'],
            'is_suspicious': metadata['risk_assessment']['is_suspicious']
        }
        
        # Write to log file
        log_file = os.path.join(self.sandbox_dir, 'executable_requests.log')
        try:
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"[ERROR] Failed to write log: {e}")
        
        # Also print to console
        print(f"[EXEC-REQ] {json.dumps(log_entry)}")
