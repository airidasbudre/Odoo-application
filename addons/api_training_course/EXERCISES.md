# Hands-On Exercises - API Training Course

Complete these exercises to master backend API development!

## 🎯 Beginner Exercises (Week 1-2)

### Exercise 1: Understanding Models
**Goal:** Learn how database models work

**Tasks:**
1. Open `models/api_blog_post.py`
2. Read all field definitions
3. Answer these questions:
   - What field types are used?
   - Which fields are required?
   - What are computed fields?
   - What constraints exist?

**Deliverable:** Write down 5 things you learned about Odoo models

---

### Exercise 2: First API Calls
**Goal:** Make your first successful API requests

**Tasks:**
1. Get all blog posts
2. Get a single post by ID
3. Search for posts with keyword "api"
4. Get featured posts only
5. Test pagination (page 1, limit 5)

**Commands:**
```bash
curl http://localhost:8069/api/training/blog/posts
curl http://localhost:8069/api/training/blog/posts/1
curl "http://localhost:8069/api/training/blog/posts/search?q=api"
curl http://localhost:8069/api/training/blog/posts/featured
curl "http://localhost:8069/api/training/blog/posts?page=1&limit=5"
```

**Deliverable:** Screenshot or copy the JSON responses

---

### Exercise 3: Understanding Routes
**Goal:** Learn how API routing works

**Tasks:**
1. Open `controllers/blog_api.py`
2. Find the `@http.route` decorators
3. Identify:
   - The URL pattern
   - HTTP method (GET, POST, etc.)
   - Auth type (public, user)
   - Request type (http, json)

**Question:** What's the difference between `type='http'` and `type='json'`?

**Deliverable:** Create a table of all blog endpoints with their properties

---

### Exercise 4: Read Source Code
**Goal:** Understand how data flows through the API

**Tasks:**
1. Pick one endpoint: `GET /api/training/blog/posts`
2. Trace the code flow:
   - Route definition → controller method
   - Query parameters parsing
   - Database search operation
   - Serialization to JSON
   - Response formatting

**Deliverable:** Draw a flowchart or write step-by-step explanation

---

### Exercise 5: Test with Python
**Goal:** Write Python code to interact with the API

**Task:** Create a Python script that:
1. Gets all blog posts
2. Prints the titles
3. Counts total posts
4. Finds posts with "tutorial" in title

**Starter Code:**
```python
import requests

BASE_URL = "http://localhost:8069/api/training"

def get_all_posts():
    response = requests.get(f"{BASE_URL}/blog/posts")
    data = response.json()
    # Your code here
    return data

# Call your function
posts = get_all_posts()
print(f"Total posts: {???}")
```

**Deliverable:** Working Python script

---

## 🔥 Intermediate Exercises (Week 3-4)

### Exercise 6: Create Data via API
**Goal:** Learn POST requests with authentication

**Tasks:**
1. Login to Odoo web interface
2. Create a blog post via API (use curl or Python)
3. Verify it appears in Odoo UI
4. Create 3 more posts with different statuses

**Python Template:**
```python
import requests

session = requests.Session()

# Login first
login_url = "http://localhost:8069/web/session/authenticate"
login_data = {
    "jsonrpc": "2.0",
    "params": {
        "db": "your_db",
        "login": "admin",
        "password": "admin"
    }
}
session.post(login_url, json=login_data)

# Create post
create_url = "http://localhost:8069/api/training/blog/posts"
post_data = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "title": "My First API Post",
        "content": "<p>Created via API!</p>",
        "status": "published"
    }
}
response = session.post(create_url, json=post_data)
print(response.json())
```

**Deliverable:** 4 blog posts created via API

---

### Exercise 7: Update and Delete
**Goal:** Master full CRUD operations

**Tasks:**
1. Create a blog post via API
2. Update its title and content via API
3. Mark it as featured via API
4. Try to delete it (should fail if published)
5. Archive it first, then delete

**Deliverable:** Document each step with API calls used

---

### Exercise 8: Advanced Filtering
**Goal:** Learn complex query operations

**Tasks:**
Build API calls to:
1. Get published posts by specific author
2. Get tasks with high priority that are overdue
3. Get tasks created in the last 7 days
4. Combine multiple filters (status + priority + project)

**Example:**
```bash
curl "http://localhost:8069/api/training/blog/posts?status=published&author_id=2"
curl "http://localhost:8069/api/training/tasks?priority=3&overdue=true"
```

**Deliverable:** 5 different filtered queries with results

---

### Exercise 9: Build a Mini Client
**Goal:** Create a simple command-line blog reader

**Requirements:**
- List all posts (titles only)
- Read full post by ID
- Search posts
- Create new post
- Update post

**Template:**
```python
import requests

class BlogClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()

    def list_posts(self):
        # Implement
        pass

    def get_post(self, post_id):
        # Implement
        pass

    def search(self, query):
        # Implement
        pass

    def create_post(self, title, content):
        # Implement
        pass

# Usage
client = BlogClient("http://localhost:8069/api/training")
client.list_posts()
```

**Deliverable:** Working CLI tool with all 5 features

---

### Exercise 10: Error Handling
**Goal:** Handle API errors gracefully

**Tasks:**
1. Request a post that doesn't exist (404)
2. Create a post without required fields (400)
3. Try to update someone else's post (403)
4. Handle network errors

**Code Template:**
```python
import requests

def safe_api_call(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        # Handle HTTP errors (404, 403, etc.)
        pass
    except requests.exceptions.ConnectionError:
        # Handle connection errors
        pass
    except Exception as e:
        # Handle other errors
        pass

# Test
safe_api_call("http://localhost:8069/api/training/blog/posts/9999")
```

**Deliverable:** Error handling wrapper for all API calls

---

## 🚀 Advanced Exercises (Week 5+)

### Exercise 11: Build Your Own Model
**Goal:** Create a custom API from scratch

**Task:** Create a "Product" API with:
- Model fields: name, description, price, stock, category
- CRUD endpoints
- Filter by category and price range
- Search functionality

**Steps:**
1. Create `models/api_product.py`
2. Add to `models/__init__.py`
3. Create `controllers/product_api.py`
4. Add security rules
5. Add to menu

**Deliverable:** Working Product API with all endpoints

---

### Exercise 12: Add Statistics Endpoint
**Goal:** Learn aggregation and computed data

**Task:** Add endpoint `/api/training/blog/stats` that returns:
- Total posts count
- Posts by status (draft, published, archived)
- Posts by author
- Average likes per post
- Most viewed post
- Most liked post

**Template:**
```python
@http.route('/api/training/blog/stats', type='http', auth='public')
def get_blog_stats(self):
    Post = request.env['api.blog.post'].sudo()

    stats = {
        'total': Post.search_count([]),
        'by_status': {
            # Implement
        },
        # Add more
    }

    return self._success_response(stats)
```

**Deliverable:** Working stats endpoint

---

### Exercise 13: Implement Comments API
**Goal:** Build a nested resource API

**Task:** Add comments to blog posts:
1. Create `api.blog.comment` model
2. Add Many2one to blog post
3. Create endpoints:
   - `GET /api/training/blog/posts/<id>/comments`
   - `POST /api/training/blog/posts/<id>/comments`
   - `DELETE /api/training/blog/comments/<id>`

**Deliverable:** Full comment system with API

---

### Exercise 14: Add File Upload
**Goal:** Handle binary data and file uploads

**Task:** Create avatar upload for user profiles:
1. Study existing avatar upload endpoint
2. Add validation (file type, size)
3. Add thumbnail generation
4. Return image URL in API response

**Deliverable:** Working file upload with validation

---

### Exercise 15: Build Complete Mini-Project
**Goal:** Apply everything you've learned

**Project Ideas:**

**Option A: E-Commerce API**
- Products, Categories, Orders, Cart
- CRUD for all models
- Search and filtering
- Order statistics
- Inventory management

**Option B: Social Media API**
- Posts, Comments, Likes, Followers
- Timeline/feed endpoint
- Trending posts
- User relationships
- Activity feed

**Option C: Project Management API**
- Projects, Tasks, Time Tracking, Teams
- Task dependencies
- Project progress
- Team member assignments
- Time reports

**Requirements:**
- At least 3 models with relationships
- Full CRUD for each model
- Search and filtering
- Statistics endpoints
- Proper authentication
- Error handling
- API documentation

**Deliverable:** Complete working API with documentation

---

## 📊 Self-Assessment Checklist

After completing the exercises, you should be able to:

### Models & ORM
- [ ] Create models with various field types
- [ ] Define field constraints and validations
- [ ] Use computed fields
- [ ] Create model relationships (Many2one, One2many)
- [ ] Override create/write/unlink methods
- [ ] Write business logic methods

### Controllers & Routes
- [ ] Create HTTP route handlers
- [ ] Handle GET and POST requests
- [ ] Parse query parameters
- [ ] Parse request body (JSON)
- [ ] Return JSON responses
- [ ] Handle different auth types

### CRUD Operations
- [ ] Search/read records
- [ ] Create new records
- [ ] Update existing records
- [ ] Delete records
- [ ] Use domain filters
- [ ] Implement pagination

### API Design
- [ ] Design RESTful endpoints
- [ ] Use proper HTTP methods
- [ ] Return appropriate status codes
- [ ] Create consistent response format
- [ ] Handle errors gracefully
- [ ] Validate input data

### Advanced Features
- [ ] Implement authentication
- [ ] Handle file uploads
- [ ] Create search endpoints
- [ ] Build statistics/aggregations
- [ ] Implement nested resources
- [ ] Document your APIs

## 🎓 Graduation Project

**Final Challenge:** Build a complete API-based application

**Requirements:**
1. At least 5 custom models
2. 20+ API endpoints
3. Full CRUD for all models
4. Authentication & authorization
5. Search, filter, pagination
6. File uploads
7. Statistics endpoints
8. Complete documentation
9. Postman collection
10. README with examples

**Ideas:**
- Blog platform with comments and tags
- Task management with time tracking
- E-commerce with cart and orders
- Social network with posts and friends
- Learning platform with courses and lessons

**Deliverable:** GitHub repository with working code + documentation

---

## 📚 Additional Resources

### What to Study Next:
1. **API Documentation:** Swagger/OpenAPI
2. **Testing:** pytest for API testing
3. **Authentication:** JWT tokens, OAuth
4. **Performance:** Caching, rate limiting
5. **Deployment:** Docker, Nginx, SSL

### Other Frameworks to Learn:
- Django REST Framework
- FastAPI
- Flask-RESTful
- Express.js (Node)
- Spring Boot (Java)

---

**Good luck with your exercises! Remember: Practice is the key to mastery.** 🚀

Share your completed exercises and get feedback from the community!
