# Windows Operations MCP — User Guide

This guide teaches you how to use every capability of the Windows Operations MCP server. Each section covers one tool domain with practical, real-world scenarios.

---

## 1. Windows Services (winops_svc)

### Listing Services

Start by discovering what services are on the system. Use `winops_svc/list` to see all services with their display names and current status. Filter by `running` to see only active services, or `stopped` to find what is not running. Set `include_system=False` to exclude Windows system services and focus on third-party software. The tool returns a structured list with name, display_name, and status for each service, plus a total count. Use this as your first step before any service operation — it gives you the exact service name needed by the other tools.

### Checking a Single Service

When you know the service name (e.g. `wuauserv` for Windows Update, `spooler` for Print Spooler), call `winops_svc/status` to see its current state. The response includes the service name and one of: running, stopped, starting, stopping. This is useful before and after making changes to confirm the operation succeeded.

### Starting and Stopping

Use `winops_svc/start` to bring a stopped service online. Specify the service name and an optional `wait_timeout` (default 30 seconds) — the tool polls until the service reaches running state and reports back. Use `winops_svc/stop` similarly to halt a service. Both require the service name (not display name) and can wait up to 120 seconds. These operations typically need Administrator elevation.

### Restarting Services

`winops_svc/restart` stops then starts a service automatically. This is the most common operation for applying configuration changes (e.g. after modifying a service's config file or installing an update). The tool waits for the running state and reports success or timeout.

### Understanding Service States

Windows services can be in one of several states: running (actively executing), stopped (inactive), start pending (transitioning to running), stop pending (transitioning to stopped), or paused (suspended, supported by some services). The tools map these numeric states to human-readable strings automatically. Knowing the current state helps decide the next action — for example, calling start on a service that is already running returns success immediately, while calling stop on a stopped service may produce a warning.

### Error Handling and Recovery

When a service operation fails, common causes include: incorrect service name (use the name from list, not the display name), insufficient privileges (run the MCP server as Administrator), or a dependency that is itself stopped. The error response includes suggestions to help diagnose the issue, such as checking the service status first or verifying the service name with list.

### Workflow: Diagnose and Fix a Stuck Service

1. `winops_svc/list(filter_status="running")` — confirm which services are up
2. `winops_svc/status(service_name="spooler")` — check the print spooler
3. `winops_svc/restart(service_name="spooler", wait_timeout=45)` — restart if hung
4. `winops_svc/status(service_name="spooler")` — verify it came back

---

## 2. Process Management (winops_process)

### Listing Processes

`winops_process/list` shows running processes with PID, name, user, CPU percentage, and memory percentage. Filter by `name_filter` to find specific processes (e.g. `"python"`, `"chrome"`, `"sqlservr"`). Set `include_system=True` to also show SYSTEM and LOCAL SERVICE processes. The result is bounded by `limit` (max 500) — when the count matches the limit, `has_more` is true meaning there are additional processes not shown.

### Getting Process Details

For deep inspection of a single process, use `winops_process/info` with its PID. Returns the process status (running, sleeping, etc.), creation time as ISO timestamp, full command line, CPU percentage, detailed memory breakdown (rss, vms, pfaults, pageins), and thread count. This is invaluable for identifying memory leaks or hung processes.

### System Resources Snapshot

`winops_process/resources` gives you a quick CPU percentage (across all cores, averaged) and virtual memory breakdown including total, available, percent used, and swap details. Use this for lightweight health checks without the overhead of full performance monitoring.

### Killing a Process

`winops_process/kill` sends a SIGTERM to the specified PID. This is for misbehaving processes that won't close normally. The tool reports success or failure (process not found, access denied). Run as Administrator to terminate system-level processes.

### Understanding Process Metrics

The CPU percentage shown by list and info represents the process's CPU usage as a percentage of a single core. On a multi-core system, a single process can exceed 100% — for example, a well-optimised multithreaded process might show 400% on a 4-core machine. Memory percentage is relative to total physical RAM. The status field shows the process state: running (actively executing on a CPU), sleeping (waiting for I/O or a timer), or zombie (terminated but not yet waited for by parent).

### Access Denied on System Processes

When listing processes, SYSTEM and LOCAL SERVICE processes are excluded by default to reduce noise. Set `include_system=True` to include them. However, even with this flag, some protected system processes may return AccessDenied when reading their details — this is normal and the tool skips these gracefully. Killing a system process always requires Administrator privileges and may destabilise the system.

### Workflow: Investigate High CPU Usage

1. `winops_process/resources()` — check if CPU is elevated
2. `winops_process/list(limit=20)` — sort by CPU to find the culprit
3. `winops_process/info(pid=1234)` — inspect the heavy process
4. `winops_process/kill(pid=1234)` — terminate if it is unresponsive

---

## 3. Firewall and Network (winops_net)

### Listing Firewall Rules

`winops_net/firewall_list` dumps all Windows Firewall rules via netsh. The output includes rule name, enabled status, action (allow/block), direction (in/out), program path, local port, protocol, and profile. Use this to audit what is allowed through the firewall. Requires Administrator.

### Adding a Firewall Rule

`winops_net/firewall_add` creates a new rule. Specify a unique `rule_name`, `direction` (in/out), `action` (allow/block), and optionally a `program` path or `port` number. For example, allow SSH on port 22 inbound, or block an executable from outbound access. The tool uses netsh advfirewall under the hood and requires elevation.

### Deleting a Firewall Rule

`winops_net/firewall_delete` removes a rule by its exact name. List rules first with `firewall_list` to get the correct name. Deleting a rule cannot be undone — be certain before calling.

### Network Diagnostics

`winops_net/diag` flushes the DNS resolver cache (ipconfig /flushdns) and then returns the full ipconfig /all output: all network adapters, IP addresses, DNS servers, DHCP status, MAC addresses, and more. Use this as the first step in any network troubleshooting.

### netsh Output Format

The firewall list command returns raw netsh output which includes rule name, enabled status, direction, protocol, local port, remote port, program path, profiles it applies to, and action. Rules are listed alphabetically. Parsing this output is straightforward: rule blocks are separated by two or more dashes. Each block contains key: value pairs with the rule name appearing first. Use this raw output when you need full detail — all rule attributes are present.

### Diagnostics Best Practices

When troubleshooting network issues, follow this order: first flush DNS with diag to clear stale cache entries, then review the full ipconfig output for incorrect IP configuration, missing DHCP leases, or wrong DNS servers. The ipconfig output shows every adapter — ignore disconnected or media-disconnected adapters and focus on the active Ethernet or Wi-Fi interface.

### Workflow: Open a Port for a Service

1. `winops_net/firewall_list()` — audit existing rules
2. `winops_net/firewall_add(rule_name="Allow MyApp", direction="in", action="allow", port="9000")` — open the port
3. `winops_net/diag()` — flush DNS and confirm network config

---

## 4. Environment Variables (winops_env)

### Listing Variables

`winops_env/list` shows all persistent environment variables for a scope (user or system). Returns a dictionary of name-value pairs and a count. User scope shows variables from HKCU\Environment; system scope shows HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment.

### Reading a Variable

`winops_env/get` returns the value of a single variable by name. Specify `scope` (user is default). Useful for checking PATH, JAVA_HOME, or custom variables before and after changes.

### Setting a Variable

`winops_env/set` persists a variable to the registry and broadcasts a WM_SETTINGCHANGE message so running applications see the change. Uses REG_EXPAND_SZ when the value contains `%` (for path variables that reference other variables), REG_SZ otherwise. System scope requires Administrator. After setting, the change is immediately visible to new processes.

### Deleting a Variable

`winops_env/delete` removes a variable from the registry and broadcasts the change. Use with caution — deleted variables cannot be recovered. System scope requires elevation.

### REG_EXPAND_SZ vs REG_SZ

When setting environment variables, the tool automatically detects whether to use REG_EXPAND_SZ or REG_SZ. REG_EXPAND_SZ is used when the value contains `%` characters (e.g. `%USERPROFILE%\AppData\Local\MyApp`), which tells Windows to expand embedded references to other environment variables. Plain strings like version numbers or paths without variables use REG_SZ. After setting, the WM_SETTINGCHANGE message is broadcast so File Explorer and new command prompts see the change immediately. Existing processes (including the MCP server itself) do not automatically pick up the change — only newly launched processes see the updated environment.

### Scope Selection

User-scope variables are stored in HKCU\Environment and apply only to the current user. System-scope variables are stored in HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment and apply to all users. System scope requires Administrator elevation. The PATH variable is a special case: it is typically a concatenation of the system PATH and user PATH at runtime, but each scope stores its own separate value in the registry. When modifying PATH, be careful not to overwrite existing entries — read first with get, append with a semicolon separator, then write back.

### Workflow: Configure JAVA_HOME

1. `winops_env/get(name="JAVA_HOME", scope="system")` — check current value
2. `winops_env/set(name="JAVA_HOME", value="C:\\Program Files\\Java\\jdk-21", scope="system")` — update
3. `winops_env/get(name="PATH", scope="system")` — verify PATH includes %JAVA_HOME%\bin

---

## 5. Event Logs (winops_evtlog)

### Listing Available Channels

`winops_evtlog/list` returns every available event log channel on the system — hundreds of them including Application, System, Security, Windows PowerShell, and many more specific to installed roles and features. Use this to find the correct channel name before querying.

### Querying Events

`winops_evtlog/query` is the workhorse. Specify a `log_name` (default Application), `max_events` (max 500), `time_range_hours` (default 24), and optionally `event_id` to filter by a specific Event ID. Each event returns timestamp, id, source name, level (Error, Warning, Info, AuditSuccess, AuditFailure), and message text. Results are ordered newest-first. When count equals max_events, `has_more` signals that older events exist.

Example queries:
- Recent System errors: `query(log_name="System", max_events=20, time_range_hours=1)`
- Application Event ID 1000: `query(log_name="Application", event_id=1000)`
- Security audit failures: `query(log_name="Security", max_events=50, time_range_hours=48)`

### Exporting Logs

`winops_evtlog/export` saves a log channel to a .evtx file at the specified path. This is useful for archival, offline analysis, or sending logs to a SIEM. Requires write permission on the output directory.

### Clearing Logs

`winops_evtlog/clear` removes all events from a channel. This is a destructive operation and requires Administrator privileges, especially for the Security log. Always export before clearing if the data has future value.

### Event Log Structure and Levels

Windows Event Log channels are organised by source: the Application log (program-level events, crashes, successes), the System log (driver, service, and OS-level events), and the Security log (login attempts, privilege use, object access). Each event carries a level: Error (1, significant failure), Warning (2, potential problem), Information (4, successful operation), Audit Success (8), and Audit Failure (16). The query tool returns these levels as human-readable strings. Each event also includes a numeric Event ID, which is the primary identifier for the event type — Event 1074 means system shutdown, Event 4624 means successful logon, Event 1000 means application error.

### Using Event IDs for Efficient Filtering

Instead of scanning through hundreds of events, filter by Event ID to find relevant entries instantly. Common useful IDs: 1074 (initiated shutdown), 6008 (unexpected shutdown), 41 (Kernel-Power unexpected shutdown), 7031/7032 (service crash), 4624 (logon success), 4625 (logon failure), 4648 (logon with explicit credentials), 1000/1001 (application error), 20 (WMI error). Filtering by event_id reduces result size and response time significantly. Always set time_range_hours to a sensible window — looking back 720 hours (30 days) on a busy server can return thousands of events.

### Export for Forensics

When investigating security incidents, export the relevant log channels to .evtx files before clearing them. The .evtx format preserves all event metadata including the original timestamps and binary data. Exported files can be opened in Event Viewer on any Windows machine or ingested into SIEM tools like Splunk or ELK.

### Workflow: Investigate a Crash

1. `winops_evtlog/query(log_name="System", max_events=30, time_range_hours=6)` — see recent system events
2. Filter by level Error in the response to identify crashes
3. `winops_evtlog/query(log_name="Application", event_id=1000, time_range_hours=6)` — check for app crashes
4. `winops_evtlog/export(log_name="System", output_path="D:\\logs\\crash_export.evtx")` — preserve evidence

---

## 6. Scheduled Tasks (winops_auto)

### Listing Tasks

`winops_auto/task_list` shows all scheduled tasks via schtasks.exe /query in LIST format. The output includes task names, schedules, next run times, status, and last run results. Use this to audit what automation is running on the system.

### Creating a Task

`winops_auto/task_create` registers a new scheduled task. Specify a unique `task_name`, the full `task_path` to the executable, the `schedule` type (MINUTE, HOURLY, DAILY, WEEKLY, MONTHLY, ONCE, ONLOGON, ONIDLE, ONEVENT), and the `start_time` in HH:mm format. The /f flag suppresses confirmation prompts. Example: creating a daily backup script that runs at 2 AM.

### Deleting a Task

`winops_auto/task_delete` removes a scheduled task by name. This is permanent — verify the task name first with task_list.

### Running a Task Immediately

`winops_auto/task_run` triggers a task to execute now, regardless of its schedule. Useful for testing a new task or forcing an out-of-cycle run.

### WMI Queries

`winops_auto/wmi_query` runs a WMI query against any class. Specify the `wmi_class` (e.g. Win32_Processor, Win32_BIOS, Win32_LogicalDisk, Win32_Service) and optionally the `wmi_namespace` (default root\cimv2). The output is the raw formatted list. Use this for deep system interrogation beyond what the dedicated tools provide.

Common WMI classes:
- Win32_OperatingSystem — OS version, last boot, free memory
- Win32_Processor — CPU name, cores, speed
- Win32_LogicalDisk — disk size, free space, filesystem
- Win32_NetworkAdapterConfiguration — IP, DNS, DHCP config
- Win32_BIOS — serial number, manufacturer, version

### Schedule Types Explained

The schedule parameter controls when the task runs. ONCE runs the task at the specified start time and never again — useful for one-off maintenance scripts. MINUTE, HOURLY, DAILY, WEEKLY, and MONTHLY provide recurring intervals. The start_time is always required for time-based schedules. ONLOGON triggers the task every time any user logs in, ONIDLE triggers when the system is idle for a period, and ONEVENT responds to specific Event Log entries. For most administrative automation, DAILY is the safest choice — it runs at a predictable low-usage time.

### WMI Query Power

WMI (Windows Management Instrumentation) is one of the most powerful system interrogation tools on Windows. With winops_auto/wmi_query, you can query hundreds of WMI classes across dozens of namespaces. Common classes: Win32_Service (all services with startup type and state), Win32_Process (every running process with full command line), Win32_NetworkAdapterConfiguration (IP config), Win32_Product (installed software), Win32_QuickFixEngineering (installed updates), Win32_StartupCommand (autostart programs). The result is formatted as key=value pairs per instance.

### Workflow: Automate a Daily Backup

1. `winops_auto/task_create(task_name="DailyBackup", task_path="C:\\scripts\\backup.bat", schedule="DAILY", start_time="02:00")`
2. `winops_auto/task_run(task_name="DailyBackup")` — test immediately
3. `winops_auto/task_list()` — verify it shows in the task list

---

## 7. File ACLs (winops_acl)

### Viewing ACLs

`winops_acl/get` displays the full Access Control List for any file or directory using icacls. Shows each user/group with their permission entries including inheritance flags (I), access type (F=Full, M=Modify, RX=Read&Execute, R=Read, W=Write), and whether the entry is explicit or inherited.

### Granting Permissions

`winops_acl/grant` adds an access control entry. Specify the `path`, `user` (username or group name), and `permission` level (F, M, RX, R, W). The tool runs icacls /grant and confirms success. Use M (Modify) for write access, RX for execute capabilities, R for read-only access.

### Revoking Permissions

`winops_acl/revoke` removes all explicit permissions for a user or group on a path using icacls /remove. Note this does not affect inherited permissions — it only targets entries explicitly added to this path.

### Managing Inheritance

`winops_acl/inheritance` toggles whether a folder inherits permissions from its parent. Set `enable=False` to disable inheritance (converting inherited entries to explicit ones for editing), or `enable=True` to re-enable it.

### Workflow: Secure a Shared Folder

1. `winops_acl/get(path="D:\\Shared")` — view current permissions
2. `winops_acl/inheritance(path="D:\\Shared", enable=False)` — break inheritance
3. `winops_acl/grant(path="D:\\Shared", user="Domain Users", permission="R")` — read for everyone
4. `winops_acl/grant(path="D:\\Shared", user="Managers", permission="M")` — modify for managers
5. `winops_acl/revoke(path="D:\\Shared", user="Guests")` — remove guest access

---

## 8. System Monitoring (winops_perf + winops_sys)

### System Performance Snapshot

`winops_perf/system` captures CPU percentage per core, virtual memory breakdown (total, available, percent, used, swap), disk I/O counters (read/write bytes, ops, queue), and optionally network I/O counters. The `sample_interval` parameter (default 1.0s, range 0.1-5.0) controls how long CPU sampling waits. This is the primary tool for performance diagnostics.

### Per-Process Performance

`winops_perf/process` drills into a single PID. Returns CPU percentage (sampled over `sample_interval`), memory info (rss, vms, pfaults, pageins), thread count, and I/O counters (read/write bytes, ops). Use this after identifying a suspect process via winops_process/list.

### System Information

`winops_sys/info` returns OS platform string, Python version, machine architecture, CPU core count (physical), and total memory. With `detailed=True`, also includes boot time, logged-in users, and CPU frequency.

### Health Check

`winops_sys/health` compares current CPU, memory, and disk usage against thresholds: healthy (CPU<70%, mem<80%, disk<85%), degraded (CPU<90%, mem<90%, disk<95%), or unhealthy (any exceeds). With `detailed=True`, includes full disk usage breakdown. When unhealthy and sampling is available, the LLM provides quick-fix suggestions.

### Port Testing

`winops_sys/test_port` checks TCP connectivity to a host:port. Specify `host`, `port`, and optional `timeout_seconds` (default 5, max 30). Returns reachable true/false. Use for checking if a service is listening or if a remote host is accessible.

### Workflow: Full System Health Audit

1. `winops_sys/info(detailed=True)` — baseline system info
2. `winops_sys/health(detailed=True)` — health assessment
3. `winops_perf/system(sample_interval=2.0)` — detailed performance counters
4. `winops_sys/test_port(host="localhost", port=3389)` — check RDP port

---

## 9. PowerShell and CMD Execution (winops_cmd)

### Executing PowerShell

`winops_cmd/powershell` runs any PowerShell command and captures stdout, stderr, exit code, and execution time. Specify the `command` string, optional `working_directory`, `timeout_seconds` (default 30, max 300), and `stdin_data` to pipe input to the command. Output is truncated at `max_output_size` (default 10,000 chars).

Examples:
- Get running services: `powershell(command="Get-Service | Where-Object Status -eq 'Running'")`
- Top CPU processes: `powershell(command="Get-Process | Sort-Object CPU -Descending | Select -First 10")`

When the command fails and the host supports sampling, the tool automatically asks the LLM to suggest a fix and includes the advice in the response.

### Executing CMD

`winops_cmd/cmd` runs a cmd.exe command with identical parameters. Use for legacy batch commands, dir, ipconfig, ping, tracert, etc.

Examples:
- Find log files: `cmd(command="dir /s /b *.log", working_directory="C:\\Logs")`
- Network config: `cmd(command="ipconfig /all")`

### Workflow: Custom Automation Script

1. `winops_cmd/powershell(command="Get-Volume | Where-Object DriveType -eq 'Fixed' | Select-Object DriveLetter, SizeRemaining, Size")` — check disk space
2. `winops_cmd/cmd(command="ping -n 4 8.8.8.8")` — test connectivity
3. Chain the results for a full system status report.

---

## 10. User and Group Management (winops_accounts)

### Listing Users

`winops_accounts/list_users` returns all local user accounts via net user. Shows usernames, full names, account status, and group memberships.

### Adding and Removing Users

`winops_accounts/add_user` creates a new local user. Specify `username` and `password`. The /add flag is appended automatically. Requires Administrator.

`winops_accounts/remove_user` deletes a user account. This is irreversible — the user profile remains on disk but the account cannot log in. Requires Administrator.

### Setting Passwords

`winops_accounts/set_password` changes a user's password. Specify `username` and `password`. The net user command is used without /add, so the password is updated on the existing account.

### Managing Groups

`winops_accounts/list_groups` shows all local groups. `winops_accounts/group_members` lists members of a specific group (e.g. Administrators, Remote Desktop Users). `winops_accounts/manage_group` adds or removes a user from a group using `action="add"` or `action="remove"`.

### Workflow: Onboard a New User

1. `winops_accounts/add_user(username="jdoe", password="TemporaryP@ss1")` — create account
2. `winops_accounts/manage_group(group="Remote Desktop Users", username="jdoe", action="add")` — grant RDP access
3. `winops_accounts/group_members(group="Remote Desktop Users")` — verify

---

## 11. JSON Operations (winops_json)

### Reading JSON Files

`winops_json/read` loads and parses a JSON file from disk, returning the parsed data structure. Handles FileNotFoundError and JSONDecodeError gracefully with clear error messages.

### Writing JSON Files

`winops_json/write` serialises data to a JSON file, creating parent directories automatically. Specify the file `path`, the `data` (any JSON-serialisable object), and optional `indent` (default 2, max 8).

### Validating JSON Strings

`winops_json/validate` checks whether a string is valid JSON without loading it into an application. Returns valid: true/false and the parse error if invalid. Use this before feeding user-provided or scraped JSON to other tools.

### Deep-Merge Patching

`winops_json/patch` is the most powerful JSON tool. It reads the existing file (if any), deep-merges the provided `data` dict into it, and writes the result. Deep merge means nested dicts are merged recursively rather than overwritten. This is perfect for updating config files: patch a config file with just the changed keys, and the rest is preserved. Creates the file if it does not exist.

### Extracting JSON from Text

`winops_json/extract_from_text` scans unstructured text for all valid JSON objects `{...}` and arrays `[...]`, parsing each one. Returns a list of found items. Use this to extract structured data from log files, API responses embedded in text, or mixed-format output.

### Formatting JSON

`winops_json/format` pretty-prints a JSON string. Specify the `text` and an `indent` value. If the string is not valid JSON, the error message suggests using validate first.

### Workflow: Update Application Config

1. `winops_json/read(path="D:\\app\\config.json")` — read existing config
2. `winops_json/patch(path="D:\\app\\config.json", data={"logging": {"level": "DEBUG", "max_size_mb": 100}})` — update only the logging section
3. `winops_json/read(path="D:\\app\\config.json")` — verify the result

---

## 12. Archive Operations (winops_archive)

### Listing Archive Contents

`winops_archive/list` shows all files inside a ZIP or TAR archive without extracting. Returns a sorted list of filenames and a count. Use this to preview what is inside before extracting.

### Creating Archives

`winops_archive/create` builds a new archive from source files or directories. Specify the output `path`, `source_files` (list of file and/or directory paths), and `archive_type` (zip, tar, or gztar). Directories are included recursively. ZIP uses ZIP_DEFLATED compression.

### Extracting Archives

`winops_archive/extract` extracts an archive to a target directory, creating the directory if it does not exist. Supports ZIP and TAR formats (including .tar.gz).

### Adding Files to an Archive

`winops_archive/add` appends files to an existing ZIP archive. Only ZIP is supported for append — use create for TAR. Files are added at the archive root.

### Expanding CAB Files

`winops_archive/expand_cab` extracts a Windows CAB cabinet file using the built-in expand.exe. This is needed for Windows driver packages, update files, and some installer formats. Specify the `.cab` file path and target directory.

### Workflow: Backup and Archive Logs

1. `winops_archive/create(path="D:\\backups\\logs.zip", source_files=["C:\\Logs\\app.log", "C:\\Logs\\error.log"])`
2. `winops_archive/list(path="D:\\backups\\logs.zip")` — verify contents
3. `winops_archive/extract(path="D:\\backups\\logs.zip", target_dir="D:\\restored")` — test extraction

---

## 13. Docker Container Operations (winops_container)

### Executing Commands in a Container

`winops_container/exec` runs a command inside a Docker container. Specify `container` (name or ID), the `command` string, optional `workdir` and `user`, and `stdin_data` to pipe text to stdin. Uses docker exec -i via subprocess directly (not through PowerShell) to avoid quoting issues on Windows.

Examples:
- Query a PostgreSQL database: `exec(container="postgres", command="psql -U admin -d mydb -c 'SELECT * FROM users'")`
- Run a Python script: `exec(container="python-app", command="python /tmp/run.py", stdin_data="input data")`
- Test nginx config: `exec(container="nginx", command="nginx -t", timeout_seconds=10)`

### Copying Files to and from Containers

`winops_container/cp` copies files between the host and a container. The direction is determined by the source prefix:
- `source="container:/tmp/data.json", destination="host:./out/"` — copy FROM container TO host
- `source="host:./script.py", destination="container:/tmp/"` — copy FROM host TO container

Exactly one of source/destination must have the `container:` prefix. The other must have the `host:` prefix.

### Workflow: Debug a Container

1. `winops_container/exec(container="web-app", command="cat /var/log/app.log | tail -50")` — read logs inside container
2. `winops_container/cp(container="web-app", source="container:/var/log/app.log", destination="host:./app.log")` — copy log to host for analysis

---

## 14. AppX Package Management (winops_apps)

### Listing Installed Apps

`winops_apps/list` queries Get-AppxPackage to list installed Windows Store/AppX packages. Filter by `name_filter` substring (e.g. "Xbox", "Microsoft.Office") to narrow results. Set `all_users=True` to see packages for all users (requires elevation). Returns package name, PackageFullName, version, and install location.

### Uninstalling Apps

`winops_apps/uninstall` removes an AppX package by its PackageFullName. Get the full name first from `winops_apps/list`. System packages require Administrator elevation. Use with caution — some built-in apps may be needed for system functionality.

### Workflow: Clean Up Bloatware

1. `winops_apps/list(name_filter="Xbox")` — find Xbox-related packages
2. `winops_apps/list(name_filter="Bing")` — find Bing-related packages
3. `winops_apps/uninstall(package_name="Microsoft.XboxApp_48.49.31001.0_x64__8wekyb3d8bbwe")` — remove specific package

---

## 15. Agentic Operations

### Autonomous System Hardening

`agentic_system_hardening` performs a three-phase security audit on a chosen subsystem (services, registry, or accounts). Phase 1 inventories the target. Phase 2 uses LLM sampling to generate hardening recommendations prioritised HIGH/MED/LOW. Phase 3 (when `dry_run=False`) queues up to 5 HIGH-priority actions for execution. Always start with `dry_run=True` to review recommendations before applying them.

### Autonomous Troubleshooting

`autonomous_troubleshooter` diagnoses a Windows operation failure by collecting recent System event log errors and a snapshot of running processes, then uses LLM sampling to identify the most probable root cause, verification steps, and fix commands. Describe the failure in natural language (e.g. "Could not start WinRM service — access denied").

---

## Quick Reference: All Tool Prefixes

| Prefix | Domain | Key Operations |
|--------|--------|---------------|
| winops_svc | Services | list, status, start, stop, restart |
| winops_process | Processes | list, info, resources, kill |
| winops_net | Network | firewall_list, firewall_add, firewall_delete, diag |
| winops_env | Environment | list, get, set, delete |
| winops_evtlog | Event Logs | query, list, export, clear |
| winops_auto | Automation | task_list, task_create, task_delete, task_run, wmi_query |
| winops_acl | Permissions | get, grant, revoke, inheritance |
| winops_perf | Performance | system, process |
| winops_cmd | Commands | powershell, cmd |
| winops_accounts | Accounts | list_users, add_user, remove_user, set_password, list_groups, group_members, manage_group |
| winops_json | JSON | read, write, validate, patch, extract_from_text, format |
| winops_archive | Archives | list, extract, create, add, expand_cab |
| winops_container | Docker | exec, cp |
| winops_apps | AppX | list, uninstall |
| winops_sys | System | info, health, test_port |
| (direct) | Agentic | agentic_system_hardening, autonomous_troubleshooter |
