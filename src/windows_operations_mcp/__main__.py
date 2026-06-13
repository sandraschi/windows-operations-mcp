import sys
from pathlib import Path

# Add the package root to sys.path for proper relative imports when run as a script
if __name__ == "__main__":
    PACKAGE_ROOT = Path(__file__).parent.parent.absolute()
    if str(PACKAGE_ROOT) not in sys.path:
        sys.path.insert(0, str(PACKAGE_ROOT))

# Import and run the industrialized server
from windows_operations_mcp.mcp_server import main

if __name__ == "__main__":
    main()
