# Task Request: {task_title}

## Objective
{task_objective}

## Context and Background
*What is the bigger picture? Why does this task matter, and what breaks if it goes wrong?*
{task_context}

## System Environment
```yaml
Operating System: {os_version}
Architecture: {system_architecture}
User Context: {user_context}
Admin Rights: {admin_status}
PowerShell Version: {powershell_version}
```

## Environment Recon (run first, paste results)
```powershell
$env:COMPUTERNAME
$PSVersionTable.PSVersion
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsHardwareAbstractionLayer
```

## Specific Requirements
1. **Primary Goal**: {primary_goal}
2. **Success Criteria**:
   - {success_criteria_1}
   - {success_criteria_2}
   - {success_criteria_3}
3. **Technical Requirements**:
   - {tech_requirement_1}
   - {tech_requirement_2}
   - {tech_requirement_3}

## Domain Playbooks (copy the one that fits, fill the values)

### Service triage
```python
# 1. Current state (no change yet)
status = winops_svc.status(service_name="Spooler")
# 2. Recent errors from the System log
errs = winops_evtlog.query(log_name="System", max_events=20, time_range_hours=24)
# 3. Only after confirmation: start, then prove it
winops_svc.start(service_name="Spooler")
winops_svc.status(service_name="Spooler")
```

### Event-log hunt
```python
channels = winops_evtlog.list_channels()
hits = winops_evtlog.query(log_name="Application", max_events=50, time_range_hours=24)
# Narrow by ID once you see a repeating one:
hits = winops_evtlog.query(log_name="Application", max_events=50, time_range_hours=72, event_id=1000)
winops_evtlog.export(log_name="Application", event_id=1000)  # keep evidence before it rolls
```

### Registry change with undo
```python
before = winops_reg.read(hive="HKLM", key_path=r"SOFTWARE\MyApp", value_name="Flag")
winops_reg.export(key_path=r"SOFTWARE\MyApp", output_path="C:\\Backups\\myapp.reg", hive="HKLM")  # .reg path is the undo
winops_reg.write(key_path=r"SOFTWARE\MyApp", value_name="Flag", value_data=1, value_type="REG_DWORD", hive="HKLM")
after = winops_reg.read(hive="HKLM", key_path=r"SOFTWARE\MyApp", value_name="Flag")
```

### Firewall rule with rollback stated
```python
before = winops_net.firewall_list()
winops_net.firewall_add(rule_name="Allow App 8080", direction="in", action="allow", port="8080")
after = winops_net.firewall_list()
# Rollback: winops_net.firewall_delete(rule_name="Allow App 8080")
```

### Disk pressure without data loss
```python
perf = winops_perf.system()
tree = winops_file.list_contents(path="D:\\Logs")
# Archive (do not delete) candidates, confirm each with age + size first:
winops_archive.create(path="D:\\Archive\\logs-2026-10.zip", source_files=["D:\\Logs\\old"], archive_type="zip")
```

### Archive round-trip (ZIP, TAR, TAR.GZ only)
```python
winops_archive.create(path="backup.zip", source_files=["path/to/directory"], archive_type="zip")
# List before extracting blind
items = winops_archive.list_contents(path="backup.zip")
winops_archive.extract(path="backup.zip", target_dir="output/directory")
# Windows CAB needs the dedicated op
winops_archive.expand_cab(archive_path="patch.cab", extract_dir="output/cab")
```

### JSON surgery (deep-merge patch, not RFC patch)
```python
data = winops_json.read(path="config.json")
winops_json.validate(text=open("config.json").read())
winops_json.patch(path="config.json", data={"retries": 5})
winops_json.validate(text=open("config.json").read())
# Rescue structured data from messy logs:
found = winops_json.extract_from_text(text=winops_cmd.powershell(command="Get-WinEvent -MaxEvents 5 | ConvertTo-Json")["stdout"])
```

### Command execution (know the semantics)
```python
ok = winops_cmd.powershell(command="$PSVersionTable.PSVersion.ToString()")
# exit_code 0 + stderr text == non-terminating error (unknown cmdlet). Real failure needs throw:
bad = winops_cmd.powershell(command='throw "SOTA_2026_FAIL"')  # success=false, exit_code=1
# Stdin: use [Console]::In, never $input (empty inside the scriptblock wrap)
up = winops_cmd.powershell(command="[Console]::In.ReadToEnd().ToUpper()", stdin_data="hello\n")
```

## Constraints and Limitations
- **Technical Constraints**:
  - {tech_constraint_1}
  - {tech_constraint_2}
  - {tech_constraint_3}
- **Business Constraints**:
  - {business_constraint_1}
  - {business_constraint_2}
- **Standing rules**: confirm destructive ops with target + undo named; smallest scope that fixes it; secrets by name only, never values; admin-gated ops fail access-denied when not elevated — report that, do not escalate alone.

## Expected Output Format
```markdown
# Solution: [Brief Description]

## Verdict
[One sentence: healthy / degraded / failed + what]

## What was run
[Tool calls with key results: exit codes, counts, names — including empty results]

## Implementation
```powershell
# Well-commented code here
Get-Service | Where-Object Status -eq 'Running'
```

## Verification Steps
1. [Step 1 to verify the solution]
2. [Step 2 to verify the solution]

## Undo
[Exact rollback: .reg path, firewall delete, service start, or 'no change was made']

## Alternative Approaches
- [Alternative 1]
- [Alternative 2]
```

## Additional Context
- **Related Systems**: {related_systems}
- **Dependencies**: {dependencies}
- **Previous Attempts**: {previous_attempts}
- **Stakeholders**: {stakeholders}

## Special Instructions
- {special_instruction_1}
- {special_instruction_2}
- {special_instruction_3}

## Success Metrics
- {metric_1}: {target_value}
- {metric_2}: {target_value}
- {metric_3}: {target_value}

## Questions for Clarification
1. {question_1}?
2. {question_2}?
3. {question_3}?
