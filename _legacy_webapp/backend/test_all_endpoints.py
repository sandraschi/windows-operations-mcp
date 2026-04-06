"""Test all API endpoints to verify they work."""
import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app.mcp.client import mcp_client

async def test_endpoint(name: str, tool_name: str, args: dict):
    """Test a single endpoint."""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"Tool: {tool_name}")
    print(f"Args: {args}")
    print("-" * 60)
    try:
        result = await mcp_client.call_tool(tool_name, args)
        print(f"[SUCCESS]")
        print(f"Result type: {type(result)}")
        if isinstance(result, dict):
            print(f"Keys: {list(result.keys())[:10]}")
            # Show first few values
            for key in list(result.keys())[:5]:
                value = result[key]
                if isinstance(value, (str, int, float, bool, type(None))):
                    print(f"  {key}: {value}")
                elif isinstance(value, list):
                    print(f"  {key}: list[{len(value)} items]")
                elif isinstance(value, dict):
                    print(f"  {key}: dict[{len(value)} keys]")
        return True, None
    except Exception as e:
        print(f"[FAILED] {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, str(e)

async def main():
    """Test all endpoints."""
    print("="*60)
    print("COMPREHENSIVE ENDPOINT TESTING")
    print("="*60)
    
    results = []
    
    # Test 1: List books
    success, error = await test_endpoint(
        "GET /api/books (list)",
        "query_books",
        {"operation": "search", "limit": 2}
    )
    results.append(("GET /api/books", success, error))
    
    # Get a book ID for subsequent tests
    book_id = None
    try:
        books_result = await mcp_client.call_tool(
            "query_books",
            {"operation": "search", "limit": 1}
        )
        if isinstance(books_result, dict) and "items" in books_result:
            if books_result["items"]:
                book_id = books_result["items"][0].get("id")
                print(f"\nFound book_id for testing: {book_id}")
    except Exception as e:
        print(f"Warning: Could not get book_id: {e}")
    
    # Test 2: Get book
    if book_id:
        success, error = await test_endpoint(
            "GET /api/books/{book_id}",
            "manage_books",
            {"operation": "get", "book_id": str(book_id), "include_metadata": True}
        )
        results.append(("GET /api/books/{book_id}", success, error))
        
        # Test 3: Get book details
        success, error = await test_endpoint(
            "GET /api/books/{book_id}/details",
            "manage_books",
            {"operation": "details", "book_id": str(book_id)}
        )
        results.append(("GET /api/books/{book_id}/details", success, error))
    else:
        print("\n[WARNING] Skipping book detail tests - no book_id available")
        results.append(("GET /api/books/{book_id}", False, "No book_id"))
        results.append(("GET /api/books/{book_id}/details", False, "No book_id"))
    
    # Test 4: List libraries
    success, error = await test_endpoint(
        "GET /api/libraries",
        "manage_libraries",
        {"operation": "list"}
    )
    results.append(("GET /api/libraries", success, error))
    
    # Test 5: Library stats
    success, error = await test_endpoint(
        "GET /api/libraries/stats",
        "manage_libraries",
        {"operation": "stats"}
    )
    results.append(("GET /api/libraries/stats", success, error))
    
    # Test 6: Search books
    success, error = await test_endpoint(
        "GET /api/search",
        "query_books",
        {"operation": "search", "text": "test", "limit": 2}
    )
    results.append(("GET /api/search", success, error))
    
    # Test 7: Show metadata
    success, error = await test_endpoint(
        "GET /api/metadata/show",
        "manage_metadata",
        {"operation": "show", "query": "test", "open_browser": False}
    )
    results.append(("GET /api/metadata/show", success, error))
    
    # Test 8: Organize tags
    success, error = await test_endpoint(
        "POST /api/metadata/organize-tags",
        "manage_metadata",
        {"operation": "organize_tags"}
    )
    results.append(("POST /api/metadata/organize-tags", success, error))
    
    # Test 9: Fix issues
    success, error = await test_endpoint(
        "POST /api/metadata/fix-issues",
        "manage_metadata",
        {"operation": "fix_issues"}
    )
    results.append(("POST /api/metadata/fix-issues", success, error))
    
    # Test 10: Open random book
    success, error = await test_endpoint(
        "POST /api/viewer/open-random",
        "manage_viewer",
        {"operation": "open_random", "format_preference": "EPUB"}
    )
    results.append(("POST /api/viewer/open-random", success, error))
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}\n")
    
    for endpoint, success, error in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} {endpoint}")
        if error:
            print(f"    Error: {error}")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed!")
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")

if __name__ == "__main__":
    asyncio.run(main())
