import sys
import os

# Setup path
current_dir = os.path.dirname(os.path.abspath(__file__))
# debug_mcp.py is in webapp/backend
# we want windows-operations-mcp/src
src_path = os.path.abspath(os.path.join(current_dir, "../../src"))
sys.path.append(src_path)

try:
    from windows_operations_mcp.mcp_server import mcp, register_all_tools

    print("Imported mcp")
    register_all_tools()
    print("Registered tools")

    print(f"Type of mcp: {type(mcp)}")
    print(f"Dir of mcp: {dir(mcp)}")

    if hasattr(mcp, "list_tools"):
        print("Calling mcp.list_tools()...")
        # specific to FastMCP implementation; list_tools might be async
        import asyncio

        try:
            tools = asyncio.run(mcp.list_tools())
            print(f"Tools found via list_tools(): {len(tools)}")
            if len(tools) > 0:
                print(f"First tool: {tools[0]}")
        except Exception as e:
            print(f"Error calling list_tools: {e}")
            # Try sync?
            try:
                tools = mcp.list_tools()
                print(f"Tools found via list_tools() sync: {len(tools)}")
            except Exception as e2:
                print(f"Error calling list_tools sync: {e2}")

    elif hasattr(mcp, "_tool_manager"):  # Another possibility
        print("Checking _tool_manager...")
        tm = mcp._tool_manager
        print(f"Type of _tool_manager: {type(tm)}")
        print(f"Dir of _tool_manager: {dir(tm)}")

        if hasattr(tm, "_tools"):
            print(f"tm._tools keys: {list(tm._tools.keys())}")
            # Print first tool details
            if tm._tools:
                first = list(tm._tools.values())[0]
                print(f"First tool: {first}")
                print(f"First tool dir: {dir(first)}")
                if hasattr(first, "name"):
                    print(f"Name: {first.name}")
                if hasattr(first, "description"):
                    print(f"Description: {first.description}")
                if hasattr(first, "parameters"):
                    print(f"Parameters: {first.parameters}")
    else:
        print("mcp has no list_tools or _tools attribute")

except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
