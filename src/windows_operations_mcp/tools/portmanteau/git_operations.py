"""Git Operations — DEPRECATED 2026-04-06.

Consolidated into gitops (git-github-mcp).
Use gitops:git_ops for all local git operations (44 actions).

This stub replaces the full implementation to remove the git_operations_async
tool from winops's MCP surface. The register_git_operations function is kept
as a no-op so mcp_server.py's dynamic loader doesn't crash.
"""

from typing import Any


def register_git_operations(mcp: Any) -> None:
    """No-op stub — git tools removed from winops.

    All git operations: use gitops:git_ops (git-github-mcp server).
      status:         git_ops(operation='status', repo_path='...')
      commit:         git_ops(operation='commit', message='...', all_files=True, repo_path='...')
      push:           git_ops(operation='push', repo_path='...')
      branch_rename:  git_ops(operation='branch_rename', branch='old', source_branch='new', repo_path='...')
    """
