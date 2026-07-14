# Examples

Runnable Python scripts demonstrating Windows Operations MCP tools.

| Example | What it shows |
|---------|---------------|
| [01_system_info.py](01_system_info.py) | OS, hardware, health metrics, uptime |
| [02_archive_creation.py](02_archive_creation.py) | ZIP archives with exclusion patterns |
| [03_powershell_automation.py](03_powershell_automation.py) | PowerShell and CMD command execution |
| [04_service_management.py](04_service_management.py) | List, filter, inspect Windows services |
| [05_event_log_query.py](05_event_log_query.py) | Query event logs by channel, level, ID, time |

## Run

```powershell
uv run python examples/01_system_info.py
```

Or run all:

```powershell
Get-ChildItem examples\*.py | ForEach-Object { uv run python $_.FullName }
```

## Notes

- Service start/stop requires Administrator
- Security log queries require Administrator
- Each script handles imports via `sys.path.insert(0, "../src")`

See [basic_usage.md](basic_usage.md) and [advanced_workflows.md](advanced_workflows.md) for detailed walkthroughs.
