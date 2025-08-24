# System Administration Prompt Templates

## Server Management

### System Health Check
```
Please run a comprehensive health check of this Windows system. Include:
- Overall system information and status
- Current resource usage (CPU, memory, disk)
- Running processes and their resource consumption
- Network connectivity tests for critical services
- Any potential issues or warnings
```

### Process Monitoring
```
Monitor and analyze the current process landscape:
- List all running processes sorted by memory usage
- Identify any suspicious or resource-intensive processes
- Check for common system processes and their status
- Provide recommendations for optimization
```

### System Cleanup and Maintenance
```
Perform system maintenance tasks:
- Check disk space usage across all drives
- Identify large files and temporary directories
- List system logs and their sizes
- Suggest cleanup actions without affecting system stability
```

## PowerShell Administration

### Environment Analysis
```
Analyze the PowerShell environment and capabilities:
- Check PowerShell version and execution policy
- List installed modules and their versions
- Test connectivity to common management endpoints
- Verify administrative privileges and capabilities
```

### Registry and System Configuration
```
Examine system configuration safely:
- Check critical registry settings (read-only)
- List installed software and versions
- Review system startup programs
- Check Windows Update status and history
```

### Network Diagnostics
```
Perform comprehensive network diagnostics:
- Test connectivity to key infrastructure (DNS, domain controllers, etc.)
- Check open ports and listening services
- Analyze network adapter configuration
- Test internet connectivity and latency
```

## Security and Compliance

### Security Assessment
```
Conduct a basic security assessment:
- List running services and their status
- Check for security updates and patches
- Review user accounts and their privileges
- Identify potential security concerns (non-intrusive)
```

### Compliance Checking
```
Check system compliance with organizational policies:
- Verify security software status (antivirus, firewall)
- Check password policy enforcement
- Review audit settings and logging
- Generate compliance summary report
```

## Troubleshooting

### Performance Issues
```
Investigate system performance problems:
- Identify high CPU or memory usage processes
- Check disk I/O patterns and bottlenecks
- Analyze system event logs for errors
- Provide performance optimization recommendations
```

### Service and Application Issues
```
Diagnose service and application problems:
- Check status of critical Windows services
- Identify failed or stopped services
- Review application error logs
- Test service dependencies and connectivity
```

### Network Connectivity Issues
```
Troubleshoot network connectivity problems:
- Test basic network connectivity (ping, DNS resolution)
- Check network adapter status and configuration
- Test connectivity to specific services and ports
- Analyze network configuration for issues
```

## Automation and Scripting

### System Inventory
```
Generate a comprehensive system inventory:
- Hardware specifications and capabilities
- Installed software and license information
- Network configuration and adapters
- Storage devices and capacity
- Export results in structured format
```

### Batch Operations
```
Execute batch operations safely:
- Process multiple files with consistent naming
- Check multiple systems for specific configurations
- Generate reports across multiple data sources
- Automate repetitive administrative tasks
```

### Monitoring and Alerting
```
Set up monitoring for key system metrics:
- Monitor disk space and alert on thresholds
- Track process resource usage over time
- Monitor network connectivity to critical services
- Generate regular status reports
```

## Development and Testing

### Development Environment Setup
```
Prepare and validate development environments:
- Check installed development tools and versions
- Verify environment variables and paths
- Test connectivity to development resources
- Validate project dependencies and requirements
```

### Testing Infrastructure
```
Support testing and QA activities:
- Set up isolated testing environments
- Generate test data and configurations
- Monitor test execution and resource usage
- Clean up test artifacts and temporary files
```

## Emergency Response

### Incident Response
```
Support incident response activities:
- Quickly gather system state information
- Check for signs of compromise or unusual activity
- Document current system configuration
- Assist with evidence collection (non-destructive)
```

### Disaster Recovery
```
Support disaster recovery planning:
- Document critical system configurations
- Identify key data and application dependencies
- Test backup and recovery procedures
- Generate recovery documentation
```

## Best Practices

### Safe Operations
- Always test commands in isolated environments first
- Use read-only operations when possible
- Create backups before making changes
- Document all actions and results
- Verify changes before applying to production

### Security Considerations
- Use least-privilege principles
- Avoid storing credentials in scripts
- Sanitize and validate all input
- Log security-relevant activities
- Follow organizational security policies

### Performance Guidelines
- Monitor resource usage during operations
- Use efficient PowerShell cmdlets and techniques
- Limit batch operation sizes
- Implement proper error handling
- Provide progress feedback for long operations