; Installer hooks for windows-operations-mcp (Tauri NSIS).
; "Register in AI tools" page + register/unregister come from the vendored fleet include
; mcp-clients.nsh (copied from onenote-mcp parity; canonical pattern per MCPB_PACKAGING_STANDARDS).
!define MCP_REG_NAME "windows-operations-mcp"
!define MCP_REG_EXE "windows-operations-mcp-backend.exe"
!include "${__FILEDIR__}\mcp-clients.nsh"

!macro KillProcesses
  DetailPrint "Stopping processes..."
  ExecWait 'taskkill /F /IM "windows-operations-mcp-backend.exe" /T' $0
  ExecWait 'taskkill /F /IM "windows-operations-mcp-native.exe" /T' $0
  Sleep 2000
!macroend

!macro NSIS_HOOK_PREINSTALL
  !insertmacro KillProcesses
!macroend

!macro NSIS_HOOK_PREUNINSTALL
  !insertmacro McpClientsUnregister
  !insertmacro KillProcesses
!macroend

!macro NSIS_HOOK_POSTINSTALL
  !insertmacro McpClientsRegister
!macroend
