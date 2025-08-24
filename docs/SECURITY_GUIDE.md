# Windows Operations MCP - Security Guide

This guide provides comprehensive security best practices and recommendations for deploying and using the Windows Operations MCP in production environments.

## Table of Contents
1. [Security Model](#security-model)
2. [Authentication & Authorization](#authentication--authorization)
3. [Network Security](#network-security)
4. [Command Execution Safety](#command-execution-safety)
5. [File System Security](#file-system-security)
6. [Data Protection](#data-protection)
7. [Audit Logging](#audit-logging)
8. [Hardening Guide](#hardening-guide)
9. [Incident Response](#incident-response)
10. [Compliance](#compliance)

## Security Model

The Windows Operations MCP follows a security-first approach with these key principles:

1. **Least Privilege**: All operations run with the minimum required permissions
2. **Defense in Depth**: Multiple layers of security controls
3. **Zero Trust**: Verify explicitly, assume breach
4. **Secure by Default**: Secure configurations out of the box
5. **Auditability**: Comprehensive logging of all operations

## Authentication & Authorization

### API Key Security

1. **Generate Strong API Keys**:
   ```python
   import secrets
   api_key = secrets.token_urlsafe(32)  # 256-bit key
   ```

2. **Secure Storage**:
   - Never hardcode API keys in source code
   - Use environment variables or secure secret management
   - Rotate keys regularly (every 90 days recommended)

3. **Key Management**:
   - Use different keys for different environments
   - Implement key versioning
   - Provide a way to revoke compromised keys

### JWT Authentication

1. **Secure JWT Configuration**:
   ```python
   # In config.toml
   [auth]
   jwt_secret = "your-256-bit-secret"  # In production, use environment variable
   jwt_algorithm = "HS256"
   access_token_expire_minutes = 30
   refresh_token_expire_days = 7
   ```

2. **Token Best Practices**:
   - Use short-lived access tokens (15-30 minutes)
   - Implement refresh token rotation
   - Store tokens securely (httpOnly, Secure, SameSite=Strict cookies)
   - Invalidate tokens on logout

### Role-Based Access Control (RBAC)

```python
# Example RBAC configuration
[roles]
admin = ["*"]  # All permissions
operator = [
    "run_powershell",
    "run_cmd",
    "list_directory",
    "read_file_content"
]
reader = [
    "list_directory",
    "read_file_content"
]

[users]
admin@example.com = "admin"
operator@example.com = "operator"
```

## Network Security

### Secure Communication

1. **Always Use HTTPS**:
   ```nginx
   # Nginx configuration example
   server {
       listen 443 ssl http2;
       server_name mcp.example.com;
       
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
       ssl_protocols TLSv1.2 TLSv1.3;
       ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
       ssl_prefer_server_ciphers on;
       
       location / {
           proxy_pass http://localhost:8080;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```

2. **Network Segmentation**:
   - Place MCP server in a DMZ or private network
   - Use VPCs and security groups to restrict access
   - Implement network ACLs to limit source IP addresses

3. **Firewall Rules**:
   ```powershell
   # Windows Firewall example
   New-NetFirewallRule -DisplayName "MCP Server" `
       -Direction Inbound `
       -LocalPort 8080 `
       -Protocol TCP `
       -Action Allow `
       -RemoteAddress 192.168.1.0/24
   ```

## Command Execution Safety

### Input Validation

1. **Command Validation**:
   ```python
   # Example of command validation
   def validate_command_safety(command: str) -> bool:
       # Block command chaining
       if any(sep in command for sep in [';', '&', '|', '`', '$']):
           return False
           
       # Block dangerous commands
       dangerous_commands = ['rm ', 'del ', 'format ', 'shutdown', 'restart']
       if any(cmd in command.lower() for cmd in dangerous_commands):
           return False
           
       return True
   ```

2. **Safe Command Execution**:
   - Use parameterized commands
   - Run commands with restricted privileges
   - Implement timeouts to prevent hanging
   - Limit command length and complexity

### Process Sandboxing

```python
# Example of running commands in a restricted environment
import subprocess
from pathlib import Path

def run_sandboxed(command: str, working_dir: str = None) -> dict:
    # Create a restricted environment
    env = {
        'PATH': '/usr/sbin:/usr/bin:/sbin:/bin',
        'HOME': str(Path.home()),
        'USER': 'restricted_user'
    }
    
    # Run with restricted permissions
    result = subprocess.run(
        command,
        shell=True,
        cwd=working_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=300,  # 5 minute timeout
        user='nobody',  # Run as unprivileged user
        group='nogroup'
    )
    
    return {
        'exit_code': result.returncode,
        'stdout': result.stdout,
        'stderr': result.stderr
    }
```

## File System Security

### Secure File Operations

1. **Path Traversal Protection**:
   ```python
   from pathlib import Path
   
   def safe_join(base_path: str, user_path: str) -> Path:
       """Safely join base path with user-provided path"""
       base = Path(base_path).resolve()
       full_path = (base / user_path).resolve()
       
       # Ensure the final path is within the base directory
       try:
           full_path.relative_to(base)
       except ValueError:
           raise ValueError("Invalid path")
           
       return full_path
   ```

2. **File Permissions**:
   - Set restrictive file permissions (600 for files, 700 for directories)
   - Use ACLs to restrict access
   - Regularly audit file permissions

### Secure File Uploads

```python
import hashlib
import magic
from pathlib import Path

def save_uploaded_file(uploaded_file, upload_dir: Path) -> Path:
    """Safely save an uploaded file"""
    # Create upload directory if it doesn't exist
    upload_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    
    # Generate a safe filename
    file_hash = hashlib.sha256(uploaded_file.read()).hexdigest()
    ext = Path(uploaded_file.filename).suffix.lower()
    safe_filename = f"{file_hash}{ext}"
    
    # Save the file
    file_path = upload_dir / safe_filename
    uploaded_file.seek(0)  # Reset file pointer
    
    # Verify file type
    file_content = uploaded_file.read()
    file_type = magic.from_buffer(file_content, mime=True)
    
    # Only allow certain file types
    allowed_types = ['text/plain', 'application/json', 'image/jpeg', 'image/png']
    if file_type not in allowed_types:
        raise ValueError(f"File type {file_type} not allowed")
    
    # Write file with secure permissions
    with open(file_path, 'wb') as f:
        f.write(file_content)
    
    # Set restrictive permissions (owner read/write only)
    file_path.chmod(0o600)
    
    return file_path
```

## Data Protection

### Encryption at Rest

1. **Encrypt Sensitive Data**:
   ```python
   from cryptography.fernet import Fernet
   import os
   
   # Generate a key (do this once and store securely)
   key = Fernet.generate_key()
   
   def encrypt_data(data: str) -> bytes:
       f = Fernet(key)
       return f.encrypt(data.encode())
   
   def decrypt_data(encrypted_data: bytes) -> str:
       f = Fernet(key)
       return f.decrypt(encrypted_data).decode()
   ```

2. **Secure Configuration**:
   - Encrypt sensitive configuration values
   - Use environment variables for secrets
   - Consider using a secrets management service

### Secure Credential Storage

```python
import keyring
from getpass import getpass

def store_credential(service_name: str, username: str, password: str = None):
    if password is None:
        password = getpass(f"Enter password for {username}@{service_name}: ")
    keyring.set_password(service_name, username, password)

def get_credential(service_name: str, username: str) -> str:
    return keyring.get_password(service_name, username)
```

## Audit Logging

### Comprehensive Logging

1. **Log Configuration**:
   ```python
   import logging
   from logging.handlers import RotatingFileHandler
   import json
   import sys
   
   def setup_logging(log_file: str = 'mcp.log'):
       # Create formatter
       formatter = logging.Formatter(
           '{"timestamp": "%(asctime)s", '
           '"level": "%(levelname)s", '
           '"module": "%(module)s", '
           '"function": "%(funcName)s", '
           '"line": %(lineno)d, '
           '"message": %(message)s}'
       )
       
       # File handler with rotation
       file_handler = RotatingFileHandler(
           log_file,
           maxBytes=10*1024*1024,  # 10MB
           backupCount=5
       )
       file_handler.setFormatter(formatter)
       
       # Console handler
       console_handler = logging.StreamHandler(sys.stdout)
       console_handler.setFormatter(formatter)
       
       # Configure root logger
       root_logger = logging.getLogger()
       root_logger.setLevel(logging.INFO)
       root_logger.addHandler(file_handler)
       root_logger.addHandler(console_handler)
   ```

2. **Sensitive Data Redaction**:
   ```python
   import re
   
   def redact_sensitive_data(message: str) -> str:
       """Redact sensitive information from log messages"""
       # Redact API keys
       message = re.sub(r'(?i)api[_-]?key[=:][^\s,;\'\"]+', '[REDACTED]', message)
       # Redact passwords
       message = re.sub(r'(?i)password[=:][^\s,;\'\"]+', '[REDACTED]', message)
       return message
   ```

## Hardening Guide

### System Hardening

1. **Operating System**:
   - Apply latest security patches
   - Disable unnecessary services
   - Enable Windows Defender and firewall
   - Configure AppLocker or Software Restriction Policies

2. **Python Environment**:
   ```bash
   # Update pip and check for vulnerabilities
   python -m pip install --upgrade pip
   pip install safety
   safety check
   
   # Use virtual environments
   python -m venv venv
   .\venv\Scripts\activate
   
   # Pin dependencies
   pip freeze > requirements.txt
   ```

### Application Hardening

1. **Run as Non-Privileged User**:
   ```powershell
   # Create a service account
   New-LocalUser -Name "mcpservice" -Description "MCP Service Account" -NoPassword
   
   # Deny interactive login
   $user = [ADSI]"WinNT://$env:COMPUTERNAME/mcpservice,user"
   $user.UserFlags = 65536  # DONT_EXPIRE_PASSWORD
   $user.SetInfo()
   ```

2. **Service Hardening**:
   ```powershell
   # Create a service with minimal privileges
   New-Service -Name "WindowsMCP" `
       -BinaryPathName "C:\path\to\python.exe -m windows_operations_mcp.mcp_server" `
       -DisplayName "Windows Operations MCP" `
       -StartupType Automatic `
       -Credential "$env:COMPUTERNAME\mcpservice"
   ```

## Incident Response

### Detection

1. **Monitor Logs**:
   - Set up log aggregation
   - Configure alerts for suspicious activities
   - Monitor for failed login attempts

2. **Intrusion Detection**:
   ```powershell
   # Example: Monitor for failed login attempts
   Get-WinEvent -FilterHashtable @{
       LogName='Security';
       ID=4625;  # Failed login
   } -MaxEvents 10 | Format-List TimeCreated, Message
   ```

### Response

1. **Containment**:
   - Isolate affected systems
   - Revoke compromised credentials
   - Block malicious IP addresses

2. **Forensics**:
   - Preserve logs and evidence
   - Document the incident timeline
   - Conduct a root cause analysis

## Compliance

### GDPR

1. **Data Protection**:
   - Implement data minimization
   - Provide data portability
   - Support right to be forgotten

2. **Documentation**:
   - Maintain a data processing register
   - Document security measures
   - Conduct DPIAs for high-risk processing

### HIPAA

1. **Access Controls**:
   - Implement role-based access
   - Enforce strong authentication
   - Log all access to ePHI

2. **Audit Controls**:
   - Enable detailed audit logging
   - Regularly review audit logs
   - Implement automatic alerts for suspicious activities

### NIST Cybersecurity Framework

1. **Identify**:
   - Maintain an asset inventory
   - Identify and document risks

2. **Protect**:
   - Implement access control
   - Protect sensitive data
   - Maintain security policies

3. **Detect**:
   - Monitor for anomalies
   - Maintain detection processes

4. **Respond**:
   - Develop an incident response plan
   - Conduct response planning

5. **Recover**:
   - Implement recovery planning
   - Improve resilience

## Security Checklist

Before going to production, verify:

- [ ] All default passwords have been changed
- [ ] HTTPS is enabled with valid certificates
- [ ] Rate limiting is properly configured
- [ ] Input validation is in place
- [ ] Error messages don't leak sensitive information
- [ ] All dependencies are up to date
- [ ] Regular backups are configured
- [ ] Monitoring and alerting are set up
- [ ] An incident response plan is in place
- [ ] Security testing has been performed

## Reporting Security Issues

If you discover a security vulnerability in Windows Operations MCP, please report it to security@example.com. Include:

1. A description of the vulnerability
2. Steps to reproduce
3. Any proof-of-concept code
4. Your contact information

We take all security issues seriously and will respond as quickly as possible.
