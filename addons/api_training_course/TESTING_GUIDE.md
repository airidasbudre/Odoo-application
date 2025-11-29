# API Testing Guide

This guide shows you how to test all the API endpoints in this training module.

## Prerequisites

- Module installed and running
- Odoo accessible at `http://localhost:8069` (or your server URL)
- `curl` installed (for command-line testing)
- Optional: Postman or Insomnia (GUI tools)

## Testing with curl

### Blog API Tests

#### 1. List All Blog Posts
```bash
curl -X GET "http://localhost:8069/api/training/blog/posts"
```

#### 2. List Posts with Pagination
```bash
curl -X GET "http://localhost:8069/api/training/blog/posts?page=1&limit=5"
```

#### 3. Filter Published Posts
```bash
curl -X GET "http://localhost:8069/api/training/blog/posts?status=published"
```

#### 4. Get Featured Posts
```bash
curl -X GET "http://localhost:8069/api/training/blog/posts/featured"
```

#### 5. Search Posts
```bash
curl -X GET "http://localhost:8069/api/training/blog/posts/search?q=api&limit=10"
```

#### 6. Get Single Post
```bash
curl -X GET "http://localhost:8069/api/training/blog/posts/1"
```

#### 7. Like a Post
```bash
curl -X POST "http://localhost:8069/api/training/blog/posts/1/like" \
  -H "Content-Type: application/json" \
  -d '{}'
```

#### 8. Create a Blog Post (requires authentication)
```bash
curl -X POST "http://localhost:8069/api/training/blog/posts" \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "title": "My Test Post",
      "content": "<p>This is a test post created via API</p>",
      "status": "published",
      "tags": "test,api"
    }
  }'
```

#### 9. Update a Blog Post (requires authentication)
```bash
curl -X POST "http://localhost:8069/api/training/blog/posts/1" \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "title": "Updated Title",
      "is_featured": true
    }
  }'
```

### Task API Tests

#### 1. List All Tasks (requires authentication)
```bash
curl -X GET "http://localhost:8069/api/training/tasks" \
  -b cookies.txt
```

#### 2. Filter Tasks by Status
```bash
curl -X GET "http://localhost:8069/api/training/tasks?status=in_progress" \
  -b cookies.txt
```

#### 3. Filter by Priority
```bash
curl -X GET "http://localhost:8069/api/training/tasks?priority=3" \
  -b cookies.txt
```

#### 4. Get My Tasks
```bash
curl -X GET "http://localhost:8069/api/training/tasks/my" \
  -b cookies.txt
```

#### 5. Get Overdue Tasks
```bash
curl -X GET "http://localhost:8069/api/training/tasks/overdue" \
  -b cookies.txt
```

#### 6. Get Task Statistics
```bash
curl -X GET "http://localhost:8069/api/training/tasks/stats" \
  -b cookies.txt
```

#### 7. Get Single Task
```bash
curl -X GET "http://localhost:8069/api/training/tasks/1" \
  -b cookies.txt
```

#### 8. Create a Task
```bash
curl -X POST "http://localhost:8069/api/training/tasks" \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "name": "Complete API Tutorial",
      "description": "Finish all API training modules",
      "priority": "2",
      "status": "todo",
      "due_date": "2024-12-31"
    }
  }'
```

#### 9. Start a Task
```bash
curl -X POST "http://localhost:8069/api/training/tasks/1/start" \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{}'
```

#### 10. Complete a Task
```bash
curl -X POST "http://localhost:8069/api/training/tasks/1/complete" \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{}'
```

### User Profile API Tests

#### 1. Get My Profile (requires authentication)
```bash
curl -X GET "http://localhost:8069/api/training/users/profile" \
  -b cookies.txt
```

#### 2. Get Public User Profile
```bash
curl -X GET "http://localhost:8069/api/training/users/2/profile"
```

#### 3. Update My Profile
```bash
curl -X POST "http://localhost:8069/api/training/users/profile" \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "bio": "Backend developer learning APIs",
      "job_title": "Software Engineer",
      "company": "Tech Corp",
      "years_of_experience": 3,
      "skills": "Python,JavaScript,SQL,REST APIs",
      "city": "San Francisco",
      "country": "USA"
    }
  }'
```

#### 4. Search Users
```bash
curl -X GET "http://localhost:8069/api/training/users/search?q=developer&limit=5"
```

#### 5. Get Leaderboard
```bash
curl -X GET "http://localhost:8069/api/training/users/leaderboard?limit=10"
```

### Meta Endpoints

#### 1. API Documentation
```bash
curl -X GET "http://localhost:8069/api/training"
```

#### 2. Health Check
```bash
curl -X GET "http://localhost:8069/api/training/health"
```

#### 3. List All Endpoints
```bash
curl -X GET "http://localhost:8069/api/training/endpoints"
```

#### 4. API Examples
```bash
curl -X GET "http://localhost:8069/api/training/examples"
```

## Testing with Python

Create a file `test_api.py`:

```python
import requests
import json

BASE_URL = "http://localhost:8069"
session = requests.Session()

# Login first (for authenticated endpoints)
def login(db, username, password):
    """Login to Odoo and get session"""
    url = f"{BASE_URL}/web/session/authenticate"
    payload = {
        "jsonrpc": "2.0",
        "params": {
            "db": db,
            "login": username,
            "password": password
        }
    }
    response = session.post(url, json=payload)
    return response.json()

# Test Blog API
def test_get_posts():
    """Get all blog posts"""
    url = f"{BASE_URL}/api/training/blog/posts"
    response = requests.get(url)
    print("Blog Posts:", json.dumps(response.json(), indent=2))

def test_create_post():
    """Create a new blog post"""
    url = f"{BASE_URL}/api/training/blog/posts"
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "title": "Python API Test",
            "content": "<p>Created from Python script</p>",
            "status": "published",
            "tags": "python,api,test"
        }
    }
    response = session.post(url, json=payload)
    print("Created Post:", json.dumps(response.json(), indent=2))

def test_search_posts(query):
    """Search blog posts"""
    url = f"{BASE_URL}/api/training/blog/posts/search"
    response = requests.get(url, params={"q": query, "limit": 5})
    print(f"Search Results for '{query}':", json.dumps(response.json(), indent=2))

# Test Task API
def test_get_tasks():
    """Get all tasks"""
    url = f"{BASE_URL}/api/training/tasks"
    response = session.get(url)
    print("Tasks:", json.dumps(response.json(), indent=2))

def test_create_task():
    """Create a new task"""
    url = f"{BASE_URL}/api/training/tasks"
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "name": "Test Task from Python",
            "description": "Created via Python script",
            "priority": "2",
            "status": "todo"
        }
    }
    response = session.post(url, json=payload)
    print("Created Task:", json.dumps(response.json(), indent=2))

def test_task_stats():
    """Get task statistics"""
    url = f"{BASE_URL}/api/training/tasks/stats"
    response = session.get(url)
    print("Task Stats:", json.dumps(response.json(), indent=2))

# Test User Profile API
def test_get_profile():
    """Get my profile"""
    url = f"{BASE_URL}/api/training/users/profile"
    response = session.get(url)
    print("My Profile:", json.dumps(response.json(), indent=2))

def test_update_profile():
    """Update my profile"""
    url = f"{BASE_URL}/api/training/users/profile"
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "bio": "Updated from Python script",
            "skills": "Python,REST,APIs,Testing"
        }
    }
    response = session.post(url, json=payload)
    print("Updated Profile:", json.dumps(response.json(), indent=2))

# Main execution
if __name__ == "__main__":
    print("=== Testing API Training Course ===\n")

    # Login (replace with your credentials)
    print("1. Logging in...")
    login("your_database", "admin", "admin")

    print("\n2. Testing Blog API...")
    test_get_posts()
    test_search_posts("api")
    test_create_post()

    print("\n3. Testing Task API...")
    test_get_tasks()
    test_task_stats()
    test_create_task()

    print("\n4. Testing User Profile API...")
    test_get_profile()
    test_update_profile()

    print("\n=== All tests completed! ===")
```

Run the script:
```bash
python test_api.py
```

## Testing with Postman

### Import Collection

1. **Create New Collection:** "API Training Course"

2. **Add Environment Variables:**
   - `base_url`: `http://localhost:8069`
   - `api_base`: `{{base_url}}/api/training`

3. **Add Requests:**

#### GET All Posts
- Method: GET
- URL: `{{api_base}}/blog/posts`
- Params:
  - `page`: 1
  - `limit`: 10

#### POST Create Post
- Method: POST
- URL: `{{api_base}}/blog/posts`
- Headers: `Content-Type: application/json`
- Body (JSON-RPC):
```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "title": "Postman Test",
    "content": "<p>Created from Postman</p>",
    "status": "published"
  }
}
```

## Common Issues

### Issue 1: Authentication Required
**Error:** "You can only edit your own posts"
**Solution:** Login to Odoo web interface first, then copy cookies

### Issue 2: CORS Errors
**Error:** CORS policy blocking request
**Solution:** Make requests from same domain or configure CORS in Odoo

### Issue 3: JSON-RPC Format
**Error:** Invalid request format
**Solution:** For `type='json'` endpoints, wrap params in JSON-RPC:
```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": { ... }
}
```

## Best Practices

1. **Test Public Endpoints First**
   - Start with GET requests
   - No authentication needed
   - Easy to verify results

2. **Use Pagination**
   - Always test with `?page=1&limit=10`
   - Verify pagination metadata in response

3. **Test Error Cases**
   - Invalid IDs (404 errors)
   - Missing required fields (400 errors)
   - Unauthorized access (403 errors)

4. **Check Response Format**
   - Verify success/error structure
   - Check data types
   - Validate nested objects

5. **Test Edge Cases**
   - Empty results
   - Large datasets
   - Special characters in input
   - Invalid data types

## Next Steps

After testing:

1. **Read the Source Code**
   - Understand controller implementation
   - Study model definitions
   - Learn serialization patterns

2. **Modify and Experiment**
   - Add new fields to models
   - Create new endpoints
   - Implement custom filters

3. **Build Your Own API**
   - Design your own models
   - Create custom controllers
   - Apply what you've learned

Happy Testing! 🚀
