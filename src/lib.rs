use zed_extension_api as zed;

struct WindowsSystemOperationsExtension;

impl zed::Extension for WindowsSystemOperationsExtension {
    fn context_server_command(
        &mut self,
        id: &zed::ContextServerId,
        _project: &zed::Project,
    ) -> zed::Result<zed::Command> {
        match id.0.as_str() {
            "windows-operations-mcp" => Ok(zed::Command {
                command: "uv".to_string(),
                args: vec!["run".to_string(), "windows_operations_mcp.__main__:main".to_string()],
                env: Default::default(),
            }),
            _ => Err(format!("Unknown server: {}", id.0)),
        }
    }
}

zed::register_extension!(WindowsSystemOperationsExtension);
