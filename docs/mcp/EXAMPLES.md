# Windows Operations MCP - Examples

This document provides practical examples of using the Windows Operations MCP for common system administration tasks.

## Table of Contents
1. [System Monitoring](#system-monitoring)
2. [File Management](#file-management)
3. [Process Management](#process-management)
4. [Network Operations](#network-operations)
5. [Automation Scripts](#automation-scripts)
6. [Integration Examples](#integration-examples)

## System Monitoring

### Monitor System Resources

```python
# Monitor CPU, memory, and disk usage
resources = client.run_tool("get_system_resources")

# Print CPU usage
print(f"CPU Usage: {resources['cpu_percent']}%")

# Print memory usage
mem = resources['memory']
print(f"Memory: {mem['percent_used']}% used ({mem['used_gb']:.1f}GB / {mem['total_gb']:.1f}GB)")

# Print disk usage
for disk in resources['disks']:
    print(f"{disk['mount']}: {disk['percent_used']}% used")
```

### Check System Health

```python
# Run a health check
health = client.run_tool("health_check")

# Print health status
print(f"System Health: {health['status'].upper()}")

# Print any warnings or errors
for check in health['checks']:
    if check['status'] != 'ok':
        print(f"{check['name'].replace('_', ' ').title()}: {check['message']}")
```

## File Management

### Backup Important Files

```python
# Backup a directory
import os
from datetime import datetime

# Create a timestamped backup directory
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = f"C:\\Backups\\{timestamp}"

# Create the backup directory
os.makedirs(backup_dir, exist_ok=True)

# Copy important files
important_files = ["C:\\Important\\doc1.txt", "C:\\Important\\config.ini"]

for file_path in important_files:
    if os.path.exists(file_path):
        file_name = os.path.basename(file_path)
        dest_path = os.path.join(backup_dir, file_name)
        with open(file_path, 'rb') as src, open(dest_path, 'wb') as dst:
            dst.write(src.read())
        print(f"Backed up {file_name}")
```

### Find Large Files

```python
# Find files larger than 100MB
result = client.run_tool("find_files", {
    "directory": "C:\\",
    "min_size_mb": 100,
    "max_depth": 3
})

# Print results
for file_info in result['files']:
    print(f"{file_info['path']} - {file_info['size_mb']:.1f}MB")
```

## Process Management

### Monitor and Manage Processes

```python
# Get all Python processes
processes = client.run_tool("get_process_list", {
    "name_filter": "python"
})

# Print process information
print("Python Processes:")
print("-" * 50)
for proc in processes['processes']:
    print(f"PID: {proc['pid']}")
    print(f"Name: {proc['name']}")
    print(f"CPU: {proc['cpu_percent']}%")
    print(f"Memory: {proc['memory_mb']:.1f}MB")
    print(f"Command: {proc.get('command_line', 'N/A')}")
    print("-" * 50)

# Terminate a process if needed
if processes['processes']:
    pid_to_kill = processes['processes'][0]['pid']
    result = client.run_tool("terminate_process", {"pid": pid_to_kill})
    print(f"Terminated process {pid_to_kill}: {result['success']}")
```

## Network Operations

### Check Service Status

```python
# Common service ports to check
services = {
    "HTTP": 80,
    "HTTPS": 443,
    "SSH": 22,
    "RDP": 3389,
    "DNS": 53
}

print("Service Status:")
print("-" * 30)

for name, port in services.items():
    result = client.run_tool("test_port", {
        "host": "localhost",
        "port": port,
        "timeout_seconds": 2
    })
    status = "✓" if result.get('reachable', False) else "✗"
    print(f"{status} {name} (port {port})")
```

## Automation Scripts

### Automated Cleanup Script

```python
import time
from datetime import datetime, timedelta

# Configuration
TEMP_DIRS = ["C:\\Temp", "C:\\Windows\\Temp"]
MAX_AGE_DAYS = 7

# Calculate cutoff time (files older than this will be deleted)
cutoff_time = time.time() - (MAX_AGE_DAYS * 24 * 60 * 60)

def cleanup_directory(directory):
    print(f"\nCleaning up {directory}...")
    
    # List all files in the directory
    result = client.run_tool("list_directory", {
        "path": directory,
        "include_hidden": True,
        "recursive": True
    })
    
    if not result['success']:
        print(f"Error accessing {directory}: {result.get('error', 'Unknown error')}")
        return
    
    # Process files
    deleted_count = 0
    for item in result['files']:
        if item['is_dir']:
            continue  # Skip directories for this example
            
        file_path = item['path']
        modified_time = item['modified_time']
        
        # Check if file is older than cutoff
        if modified_time < cutoff_time:
            try:
                # Delete the file
                delete_result = client.run_tool("delete_file", {
                    "path": file_path,
                    "force": True
                })
                
                if delete_result['success']:
                    print(f"Deleted: {file_path}")
                    deleted_count += 1
                else:
                    print(f"Failed to delete {file_path}: {delete_result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"Error deleting {file_path}: {str(e)}")
    
    print(f"Deleted {deleted_count} files from {directory}")

# Run cleanup on all configured directories
for temp_dir in TEMP_DIRS:
    cleanup_directory(temp_dir)

print("\nCleanup complete!")
```

## Integration Examples

### Integration with Monitoring Systems

```python
import json
from datetime import datetime

# Configuration
MONITORING_API_URL = "https://monitoring.example.com/api/v1/metrics"
API_KEY = "your-api-key-here"

# Get system metrics
resources = client.run_tool("get_system_resources")
processes = client.run_tool("get_process_list")

# Prepare metrics payload
metrics = {
    "timestamp": datetime.utcnow().isoformat(),
    "hostname": resources['system']['hostname'],
    "metrics": {
        "cpu_percent": resources['cpu_percent'],
        "memory_used_gb": resources['memory']['used_gb'],
        "memory_total_gb": resources['memory']['total_gb'],
        "process_count": len(processes['processes']),
        "disks": [
            {"mount": disk['mount'], "used_gb": disk['used_gb'], "total_gb": disk['total_gb']}
            for disk in resources['disks']
        ]
    }
}

# Send to monitoring system (example using requests)
try:
    import requests
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    response = requests.post(
        MONITORING_API_URL,
        headers=headers,
        data=json.dumps(metrics)
    )
    
    if response.status_code == 200:
        print("Metrics sent successfully")
    else:
        print(f"Failed to send metrics: {response.status_code} - {response.text}")
        
except ImportError:
    print("Warning: 'requests' package not installed. Cannot send metrics.")
    print("Metrics data:", json.dumps(metrics, indent=2))
```

### Web Interface Example (Flask)

```python
from flask import Flask, jsonify, request
import json

app = Flask(__name__)

# Simple authentication middleware
def require_api_key(f):
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if api_key != "your-secure-api-key":
            return jsonify({"error": "Invalid API key"}), 403
        return f(*args, **kwargs)
    return decorated

@app.route('/api/system-info', methods=['GET'])
@require_api_key
def system_info():
    info = client.run_tool("get_system_info")
    return jsonify(info)

@app.route('/api/processes', methods=['GET'])
@require_api_key
def list_processes():
    name_filter = request.args.get('name', '')
    result = client.run_tool("get_process_list", {"name_filter": name_filter})
    return jsonify(result)

@app.route('/api/execute', methods=['POST'])
@require_api_key
def execute_command():
    data = request.get_json()
    command = data.get('command', '')
    
    # Basic command validation
    if not command:
        return jsonify({"error": "No command provided"}), 400
    
    # Execute the command
    result = client.run_tool("run_powershell" if data.get('use_powershell', True) else "run_cmd", {
        "command": command,
        "timeout_seconds": data.get('timeout_seconds', 30)
    })
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

These examples demonstrate just a few of the many ways you can use the Windows Operations MCP to automate and manage your Windows systems. The API is designed to be flexible and extensible, allowing you to build custom solutions tailored to your specific needs.
