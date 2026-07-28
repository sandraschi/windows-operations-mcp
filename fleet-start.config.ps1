# Per-repo fleet start config for windows-operations-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'windows-operations-mcp'
    BackendPort  = 10748
    FrontendPort = 10749
    HealthPath   = '/health'
    WebRoot      = 'D:\Dev\repos\windows-operations-mcp\web_sota'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'windows_operations_mcp.server:app'
        SyncExtras    = @('dev')
        Env           = @{ WEB_PORT = '10748' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
