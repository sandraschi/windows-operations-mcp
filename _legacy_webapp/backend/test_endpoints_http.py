"""Test all API endpoints via HTTP."""
import asyncio
import httpx
import json

BASE_URL = "http://localhost:13000"

async def test_endpoint(client, method, path, params=None, json_data=None, description=""):
    """Test an endpoint via HTTP."""
    print(f"\n{'='*60}")
    print(f"Testing: {description or f'{method} {path}'}")
    print(f"URL: {BASE_URL}{path}")
    if params:
        print(f"Params: {params}")
    if json_data:
        print(f"Body: {json.dumps(json_data, indent=2)}")
    print("-" * 60)
    
    try:
        if method == "GET":
            response = await client.get(path, params=params, timeout=10.0)
        elif method == "POST":
            response = await client.post(path, params=params, json=json_data, timeout=10.0)
        elif method == "PUT":
            response = await client.put(path, params=params, json=json_data, timeout=10.0)
        elif method == "DELETE":
            response = await client.delete(path, params=params, timeout=10.0)
        else:
            print(f"✗ Unknown method: {method}")
            return False
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"[SUCCESS]")
                print(f"Response type: {type(data)}")
                if isinstance(data, dict):
                    print(f"Keys: {list(data.keys())[:10]}")
                    # Show sample values
                    for key in list(data.keys())[:3]:
                        value = data[key]
                        if isinstance(value, (str, int, float, bool, type(None))):
                            print(f"  {key}: {value}")
                        elif isinstance(value, list):
                            print(f"  {key}: list[{len(value)} items]")
                        elif isinstance(value, dict):
                            print(f"  {key}: dict[{len(value)} keys]")
                elif isinstance(data, list):
                    print(f"List length: {len(data)}")
                return True
            except json.JSONDecodeError:
                print(f"[SUCCESS] (non-JSON response)")
                print(f"Response: {response.text[:200]}")
                return True
        else:
            print(f"[FAILED] HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {json.dumps(error_data, indent=2)[:500]}")
            except:
                print(f"Error: {response.text[:500]}")
            return False
            
    except httpx.ConnectError:
        print(f"[FAILED] Cannot connect to {BASE_URL}")
        print("Make sure the backend server is running!")
        return False
    except Exception as e:
        print(f"[FAILED] {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Test all endpoints."""
    print("="*60)
    print("HTTP ENDPOINT TESTING")
    print("="*60)
    
    async with httpx.AsyncClient(base_url=BASE_URL, follow_redirects=True) as client:
        results = []
        
        # Test basic endpoints
        results.append(("GET /", await test_endpoint(client, "GET", "/", description="Root endpoint")))
        results.append(("GET /health", await test_endpoint(client, "GET", "/health", description="Health check")))
        
        # Test books endpoints
        results.append(("GET /api/books", await test_endpoint(client, "GET", "/api/books", params={"limit": 2}, description="List books")))
        
        # Get a book ID for testing
        book_id = None
        try:
            books_response = await client.get("/api/books", params={"limit": 1}, timeout=10.0)
            if books_response.status_code == 200:
                books_data = books_response.json()
                if isinstance(books_data, dict) and "items" in books_data and books_data["items"]:
                    book_id = books_data["items"][0].get("id")
                    print(f"\nFound book_id for testing: {book_id}")
        except Exception as e:
            print(f"Warning: Could not get book_id: {e}")
        
        if book_id:
            results.append(("GET /api/books/{id}", await test_endpoint(client, "GET", f"/api/books/{book_id}", description="Get book")))
            results.append(("GET /api/books/{id}/details", await test_endpoint(client, "GET", f"/api/books/{book_id}/details", description="Get book details")))
        else:
            print("\n[WARNING] Skipping book detail tests - no book_id available")
            results.append(("GET /api/books/{id}", False))
            results.append(("GET /api/books/{id}/details", False))
        
        # Test libraries endpoints
        results.append(("GET /api/libraries", await test_endpoint(client, "GET", "/api/libraries", description="List libraries")))
        results.append(("GET /api/libraries/stats", await test_endpoint(client, "GET", "/api/libraries/stats", description="Library stats")))
        
        # Test search endpoint
        results.append(("GET /api/search", await test_endpoint(client, "GET", "/api/search", params={"query": "test", "limit": 2}, description="Search books")))
        
        # Test metadata endpoints
        results.append(("GET /api/metadata/show", await test_endpoint(client, "GET", "/api/metadata/show", params={"query": "test", "open_browser": False}, description="Show metadata")))
        results.append(("POST /api/metadata/organize-tags", await test_endpoint(client, "POST", "/api/metadata/organize-tags", description="Organize tags")))
        results.append(("POST /api/metadata/fix-issues", await test_endpoint(client, "POST", "/api/metadata/fix-issues", description="Fix metadata issues")))
        
        # Test viewer endpoints
        results.append(("POST /api/viewer/open-random", await test_endpoint(client, "POST", "/api/viewer/open-random", params={"format_preference": "EPUB"}, description="Open random book")))
        
        # Print summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        passed = sum(1 for _, success in results if success)
        total = len(results)
        print(f"\nPassed: {passed}/{total}")
        print(f"Failed: {total - passed}/{total}\n")
        
        for endpoint, success in results:
            status = "[PASS]" if success else "[FAIL]"
            print(f"{status} {endpoint}")
    
        if passed == total:
            print("\n[SUCCESS] All tests passed!")
        else:
            print(f"\n[WARNING] {total - passed} test(s) failed")

if __name__ == "__main__":
    asyncio.run(main())
