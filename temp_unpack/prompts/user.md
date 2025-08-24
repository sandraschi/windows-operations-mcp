# 🎯 Task Request: {task_title}

## 🌟 Objective
{task_objective}

## 🏗️ Context & Background
*What's the bigger picture? Why is this task important?*
{task_context}

## 🖥️ System Environment
```yaml
Operating System: {os_version}
Architecture: {system_architecture}
User Context: {user_context}
Admin Rights: {admin_status}
PowerShell Version: {powershell_version}
```

## 🔧 Technical Details
```powershell
# Relevant system information
$env:COMPUTERNAME
$PSVersionTable.PSVersion
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsHardwareAbstractionLayer
```

## 🎯 Specific Requirements
1. **Primary Goal**: {primary_goal}
2. **Success Criteria**: 
   - {success_criteria_1}
   - {success_criteria_2}
   - {success_criteria_3}
3. **Technical Requirements**:
   - {tech_requirement_1}
   - {tech_requirement_2}
   - {tech_requirement_3}

## 📦 Archive Tools Examples

### Create a ZIP Archive
```python
# Create a ZIP archive of a directory
archive.create(
    archive_path="backup.zip",
    source_paths=["path/to/directory"],
    compression_level=6  # 0-9 where 0 is no compression, 9 is maximum
)

# Create a password-protected ZIP
archive.create(
    archive_path="secure_backup.zip",
    source_paths=["sensitive/files"],
    password="your_secure_password"
)
```

### Extract an Archive
```python
# Extract a ZIP file
archive.extract(
    archive_path="archive.zip",
    extract_dir="output/directory"
)

# Extract specific files from an archive
archive.extract(
    archive_path="archive.rar",
    extract_dir="output/directory",
    members=["file1.txt", "folder/file2.txt"],
    password="archive_password"  # For password-protected archives
)
```

### List Archive Contents
```python
# List contents of an archive
contents = archive.list("archive.tar.gz")
for item in contents:
    print(f"{item['filename']} - {item['size']} bytes")

# Check if a file exists in an archive
contents = archive.list("archive.rar")
file_exists = any(item['filename'] == 'important.txt' for item in contents)
```

### Supported Archive Formats
- ZIP (`.zip`)
- RAR (`.rar`) - Requires external `rar`/`unrar` tools
- TAR (`.tar`)
- TAR.GZ (`.tar.gz`, `.tgz`)

## ⚠️ Constraints & Limitations
- **Technical Constraints**:
  - {tech_constraint_1}
  - {tech_constraint_2}
  - {tech_constraint_3}
- **Business Constraints**:
  - {business_constraint_1}
  - {business_constraint_2}

## 🎨 Expected Output Format
```markdown
# Solution: [Brief Description]

## Approach
[High-level explanation of the solution]

## Implementation
```powershell
# Well-commented code here
Get-Service | Where-Object Status -eq 'Running'
```

## Verification Steps
1. [Step 1 to verify the solution]
2. [Step 2 to verify the solution]

## Alternative Approaches
- [Alternative 1]
- [Alternative 2]
```

## 🔍 Additional Context
- **Related Systems**: {related_systems}
- **Dependencies**: {dependencies}
- **Previous Attempts**: {previous_attempts}
- **Stakeholders**: {stakeholders}

## 📝 Special Instructions
- {special_instruction_1}
- {special_instruction_2}
- {special_instruction_3}

## 📊 Success Metrics
- {metric_1}: {target_value}
- {metric_2}: {target_value}
- {metric_3}: {target_value}

## ❓ Questions for Clarification
1. {question_1}?
2. {question_2}?
3. {question_3}?
