# Advanced Workflows

## System Administration Workflows

### Complete System Health Assessment
```
# Step 1: Check server health and basic info
health_check()
system_info = get_system_info()

# Step 2: Analyze resource usage
resources = get_system_resources()

# Step 3: Check critical processes
processes = get_process_list(max_processes=20)

# Step 4: Test network connectivity
test_port("8.8.8.8", 53, protocol="udp")  # DNS
test_port("google.com", 443, protocol="tcp")  # Internet

# Step 5: Check disk space and usage
run_powershell("Get-WmiObject Win32_LogicalDisk | Select-Object DeviceID, @{n='Size(GB)';e={[math]::Round($_.Size/1GB,2)}}, @{n='FreeSpace(GB)';e={[math]::Round($_.FreeSpace/1GB,2)}}, @{n='%Free';e={[math]::Round(($_.FreeSpace/$_.Size)*100,2)}}")

# Step 6: Check Windows services status
run_powershell("Get-Service | Where-Object {$_.Status -eq 'Stopped' -and $_.StartType -eq 'Automatic'} | Select-Object Name, Status, StartType")
```

### Log Analysis and Monitoring Workflow
```
# Step 1: Find all log directories
log_dirs = [
    "C:\\Windows\\Logs",
    "C:\\inetpub\\logs",
    "C:\\logs",
    "C:\\ProgramData\\logs"
]

for log_dir in log_dirs:
    result = list_directory(log_dir, file_pattern="*.log", max_items=100)
    if result["success"]:
        print(f"Found {result['files_count']} log files in {log_dir}")

# Step 2: Analyze recent log files for errors
run_powershell("Get-WinEvent -FilterHashtable @{LogName='System'; Level=1,2,3} -MaxEvents 50 | Select-Object TimeCreated, Id, LevelDisplayName, Message | Format-Table -Wrap")

# Step 3: Check application event logs
run_powershell("Get-WinEvent -FilterHashtable @{LogName='Application'; Level=1,2} -MaxEvents 50 | Select-Object TimeCreated, Id, LevelDisplayName, Message | Format-Table -Wrap")

# Step 4: Search for specific error patterns in custom logs
run_powershell("Get-ChildItem -Path 'C:\\logs' -Filter '*.log' | ForEach-Object { Select-String -Path $_.FullName -Pattern 'ERROR|FATAL|EXCEPTION' -SimpleMatch | Select-Object -First 10 }")
```

### Performance Monitoring Workflow
```
# Step 1: Baseline system performance
baseline = get_system_resources()

# Step 2: Identify resource-intensive processes
heavy_processes = get_process_list(max_processes=10)

# Step 3: Monitor specific processes over time
for process in heavy_processes["processes"][:5]:
    process_details = get_process_info(process["pid"])
    print(f"Process {process['name']} (PID: {process['pid']}) using {process['memory_mb']} MB")

# Step 4: Check for performance counters
run_powershell("Get-Counter '\\Processor(_Total)\\% Processor Time', '\\Memory\\Available MBytes', '\\PhysicalDisk(_Total)\\% Disk Time' -SampleInterval 2 -MaxSamples 3")

# Step 5: Analyze network performance
run_powershell("Get-Counter '\\Network Interface(*)\\Bytes Total/sec' | Select-Object -ExpandProperty CounterSamples | Where-Object {$_.CookedValue -gt 0}")
```

## Development Environment Workflows

### Project Setup and Validation
```
# Step 1: Validate development environment
dev_tools = [
    "python --version",
    "node --version", 
    "npm --version",
    "git --version",
    "docker --version"
]

for tool in dev_tools:
    result = run_powershell(tool)
    if result["success"]:
        print(f"✓ {tool}: {result['stdout'].strip()}")
    else:
        print(f"✗ {tool}: Not found or error")

# Step 2: Check project structure
project_path = "C:\\projects\\myapp"
project_structure = list_directory(project_path, max_items=50)

# Step 3: Validate configuration files
config_files = ["package.json", "requirements.txt", ".env.example", "docker-compose.yml"]
for config_file in config_files:
    result = read_file_content(f"{project_path}\\{config_file}")
    if result["success"]:
        print(f"✓ {config_file}: {result['lines_count']} lines")
    else:
        print(f"✗ {config_file}: Not found")

# Step 4: Test development services
dev_services = [
    ("localhost", 3000, "tcp"),  # Development server
    ("localhost", 5432, "tcp"),  # PostgreSQL
    ("localhost", 6379, "tcp"),  # Redis
    ("localhost", 9200, "tcp"),  # Elasticsearch
]

for host, port, protocol in dev_services:
    result = test_port(host, port, protocol=protocol)
    service_name = f"{host}:{port}"
    if result["accessible"]:
        print(f"✓ {service_name}: Available ({result['response_time_ms']}ms)")
    else:
        print(f"✗ {service_name}: Not accessible")
```

### Code Quality and Analysis Workflow
```
# Step 1: Analyze project structure
project_files = list_directory("C:\\projects\\myapp", file_pattern="*.py")
print(f"Python files found: {project_files['files_count']}")

# Step 2: Check for common files and standards
required_files = ["README.md", "requirements.txt", ".gitignore", "setup.py"]
for file_name in required_files:
    result = read_file_content(f"C:\\projects\\myapp\\{file_name}")
    if result["success"]:
        print(f"✓ {file_name}: Present ({result['size_bytes']} bytes)")

# Step 3: Run code quality checks
run_powershell("python -m flake8 --statistics --count", working_directory="C:\\projects\\myapp")
run_powershell("python -m pylint --score=yes *.py", working_directory="C:\\projects\\myapp")

# Step 4: Check dependencies for security issues
run_powershell("python -m safety check", working_directory="C:\\projects\\myapp")

# Step 5: Generate code metrics
run_powershell("python -c \"import os; print(f'Lines of code: {sum(1 for line in open(f) for f in os.listdir('.') if f.endswith('.py'))}')\"", working_directory="C:\\projects\\myapp")
```

### Build and Deployment Workflow
```
# Step 1: Clean build environment
run_powershell("Remove-Item -Path '.\\dist' -Recurse -Force -ErrorAction SilentlyContinue", working_directory="C:\\projects\\myapp")
run_powershell("Remove-Item -Path '.\\build' -Recurse -Force -ErrorAction SilentlyContinue", working_directory="C:\\projects\\myapp")

# Step 2: Install dependencies
run_powershell("pip install -r requirements.txt", working_directory="C:\\projects\\myapp", timeout_seconds=300)

# Step 3: Run tests
run_powershell("python -m pytest --verbose --tb=short", working_directory="C:\\projects\\myapp", timeout_seconds=120)

# Step 4: Build application
run_powershell("python setup.py sdist bdist_wheel", working_directory="C:\\projects\\myapp", timeout_seconds=120)

# Step 5: Validate build artifacts
build_files = list_directory("C:\\projects\\myapp\\dist")
if build_files["success"]:
    print(f"Build artifacts: {build_files['files_count']} files created")
    for file_info in build_files["items"]:
        print(f"  - {file_info['name']} ({file_info['size']} bytes)")

# Step 6: Test deployment configuration
deployment_config = read_file_content("C:\\projects\\myapp\\deploy.yml")
if deployment_config["success"]:
    print("Deployment configuration validated")
```

## Security and Compliance Workflows

### Security Assessment Workflow
```
# Step 1: Check for running security services
security_services = ["Windows Defender", "Windows Firewall"]
for service in security_services:
    run_powershell(f"Get-Service | Where-Object {{$_.DisplayName -like '*{service}*'}} | Select-Object Name, Status, StartType")

# Step 2: Check Windows Update status
run_powershell("Get-WULastResults | Select-Object LastSearchSuccessDate, LastInstallationSuccessDate")

# Step 3: Review user accounts and groups
run_powershell("Get-LocalUser | Where-Object {$_.Enabled -eq $true} | Select-Object Name, LastLogon, PasswordLastSet")
run_powershell("Get-LocalGroup | Select-Object Name, Description")

# Step 4: Check network security
run_powershell("Get-NetFirewallRule | Where-Object {$_.Enabled -eq 'True' -and $_.Direction -eq 'Inbound'} | Select-Object DisplayName, Action, Direction | Sort-Object DisplayName")

# Step 5: Scan for sensitive files (example patterns)
run_powershell("Get-ChildItem -Path 'C:\\' -Recurse -Include '*.key', '*.pem', '*.p12', '*.pfx' -ErrorAction SilentlyContinue | Select-Object FullName, Length, LastWriteTime")
```

### Compliance Monitoring Workflow
```
# Step 1: Check system configuration compliance
run_powershell("Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, TotalPhysicalMemory, CsProcessors")

# Step 2: Verify security policies
run_powershell("secedit /export /cfg C:\\temp\\security_policy.inf")
policy_content = read_file_content("C:\\temp\\security_policy.inf")

# Step 3: Check installed software for compliance
run_powershell("Get-WmiObject -Class Win32_Product | Select-Object Name, Version, Vendor | Sort-Object Name")

# Step 4: Audit file permissions on sensitive directories
sensitive_dirs = ["C:\\Program Files", "C:\\Windows\\System32", "C:\\Users"]
for directory in sensitive_dirs:
    run_powershell(f"Get-Acl '{directory}' | Select-Object Path, Owner, Group")

# Step 5: Generate compliance report
compliance_data = {
    "system_info": get_system_info(),
    "security_services": run_powershell("Get-Service | Where-Object {$_.Name -like '*defender*' -or $_.Name -like '*firewall*'} | Select-Object Name, Status"),
    "updates": run_powershell("Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 10")
}
```

## Backup and Recovery Workflows

### Backup Validation Workflow
```
# Step 1: Check backup directories and schedules
backup_locations = ["C:\\Backups", "D:\\Backups", "\\\\server\\backups"]
for location in backup_locations:
    backup_files = list_directory(location, file_pattern="*.bak")
    if backup_files["success"]:
        print(f"Backup location {location}: {backup_files['files_count']} backup files")

# Step 2: Validate recent backups
run_powershell("Get-ScheduledTask | Where-Object {$_.TaskName -like '*backup*'} | Select-Object TaskName, State, LastRunTime, NextRunTime")

# Step 3: Test backup integrity (example for database backups)
run_powershell("sqlcmd -Q \"RESTORE VERIFYONLY FROM DISK = 'C:\\Backups\\database.bak'\"", timeout_seconds=300)

# Step 4: Check backup storage capacity
for location in backup_locations:
    run_powershell(f"Get-WmiObject -Class Win32_LogicalDisk | Where-Object {{$_.DeviceID -eq '{location[0]}:'}} | Select-Object DeviceID, Size, FreeSpace")
```

### Disaster Recovery Testing Workflow
```
# Step 1: Document current system state
current_state = {
    "system_info": get_system_info(),
    "running_services": run_powershell("Get-Service | Where-Object {$_.Status -eq 'Running'} | Select-Object Name, Status"),
    "network_config": run_cmd("ipconfig /all"),
    "installed_software": run_powershell("Get-WmiObject Win32_Product | Select-Object Name, Version")
}

# Step 2: Test backup restoration procedures (dry run)
run_powershell("Test-Path 'C:\\Backups\\system_backup.zip'")
run_powershell("Test-Path 'C:\\Backups\\data_backup.zip'")

# Step 3: Validate recovery environment
recovery_checklist = [
    "Network connectivity",
    "Storage availability", 
    "Required software presence",
    "Configuration files accessibility"
]

# Step 4: Test communication systems
test_port("mail.company.com", 25, protocol="tcp")
test_port("alerts.company.com", 443, protocol="tcp")
```

## Best Practices for Advanced Workflows

### Error Handling and Resilience
```python
def robust_operation(operation_func, *args, max_retries=3, **kwargs):
    for attempt in range(max_retries):
        result = operation_func(*args, **kwargs)
        if result["success"]:
            return result
        print(f"Attempt {attempt + 1} failed: {result.get('error', 'Unknown error')}")
        if attempt < max_retries - 1:
            time.sleep(2)  # Wait before retry
    return result
```

### Logging and Auditing
```python
def log_operation(operation_name, result):
    timestamp = datetime.now().isoformat()
    log_entry = f"{timestamp} - {operation_name}: {'SUCCESS' if result['success'] else 'FAILED'}"
    if not result["success"]:
        log_entry += f" - {result.get('error', 'Unknown error')}"
    
    write_file_content("C:\\logs\\mcp_operations.log", log_entry + "\\n", 
                      create_directories=True, backup_existing=False)
```

### Progress Tracking
```python
def multi_step_workflow(steps):
    total_steps = len(steps)
    completed_steps = 0
    
    for i, (step_name, step_func, step_args) in enumerate(steps):
        print(f"Step {i+1}/{total_steps}: {step_name}")
        result = step_func(*step_args)
        
        if result["success"]:
            completed_steps += 1
            print(f"✓ Completed: {step_name}")
        else:
            print(f"✗ Failed: {step_name} - {result.get('error', 'Unknown error')}")
            break
    
    print(f"Workflow completed: {completed_steps}/{total_steps} steps successful")
```
