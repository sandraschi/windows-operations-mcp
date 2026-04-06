import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path("src").absolute()))

from windows_operations_mcp.tools.portmanteau.git_operations import git_operations


async def test():
    print("Testing git_operations(action='status')...")
    # Test on the current repo
    repo_path = os.getcwd()
    result = git_operations(action="status", repo_path=repo_path)
    print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(test())
