# API Training Course - Complete Backend Development Training

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Odoo](https://img.shields.io/badge/odoo-18.0-purple.svg)
![License](https://img.shields.io/badge/license-LGPL--3-green.svg)

A comprehensive, hands-on training module that teaches you how to build professional REST APIs using Odoo as your backend framework. **This course covers 90% of what you need to know for backend development jobs!**

## 🎯 Why This Training?

Odoo is one of the **best platforms to learn backend development** because:

- ✅ **Built-in ORM** (like Django/SQLAlchemy)
- ✅ **Built-in Web Framework** (routing, controllers, authentication)
- ✅ **Real Database Models** (PostgreSQL)
- ✅ **Production-Ready Patterns**
- ✅ **Easy Local Testing**
- ✅ **Everything You Need** in one place

You can learn **API basics, database models, JSON handling, routing, authentication, and deployment** — all inside Odoo!

## 📚 What You'll Learn

### Core Concepts
1. **RESTful API Design Principles**
   - HTTP methods (GET, POST, PUT, DELETE)
   - Status codes and error handling
   - JSON request/response patterns
   - API versioning and documentation

2. **Database & ORM Operations**
   - Creating models with field types
   - CRUD operations (Create, Read, Update, Delete)
   - Relationships (Many2one, One2many)
   - Computed fields and constraints
   - Domain filtering and searching

3. **API Controllers & Routing**
   - Route decorators and parameters
   - Request handling (type='http' vs type='json')
   - Response formatting
   - Query parameters and URL patterns

4. **Authentication & Authorization**
   - Public vs authenticated endpoints
   - User permissions
   - Session management
   - Security best practices

5. **Advanced Features**
   - Pagination and sorting
   - Search and filtering
   - File uploads (images, documents)
   - Statistics and aggregations
   - Error handling and validation

## 🚀 Installation

### Prerequisites
- Odoo 18.0 installed and running
- Basic Python knowledge
- Basic understanding of HTTP/REST

### Install the Module

1. **Copy the module to your addons directory:**
   ```bash
   cp -r api_training_course /path/to/odoo/addons/
   ```

2. **Update your Odoo apps list:**
   - Go to Apps menu in Odoo
   - Click "Update Apps List"
   - Search for "API Training Course"

3. **Install the module:**
   - Click Install

4. **Verify installation:**
   - Open browser: `http://localhost:8069/api/training`
   - You should see the API welcome page

## 📖 Course Structure

### Module 1: Blog API (CRUD Operations)
Learn the fundamentals of REST APIs with a complete blog system.

**What You'll Build:**
- List all blog posts with pagination
- Get single blog post by ID
- Create new blog posts
- Update existing posts
- Delete posts
- Like posts
- Search and filter posts
- Featured posts endpoint

**Endpoints:**
```
GET    /api/training/blog/posts              # List posts
GET    /api/training/blog/posts/<id>         # Get single post
POST   /api/training/blog/posts              # Create post
PUT    /api/training/blog/posts/<id>         # Update post
DELETE /api/training/blog/posts/<id>         # Delete post
POST   /api/training/blog/posts/<id>/like    # Like post
GET    /api/training/blog/posts/featured     # Featured posts
GET    /api/training/blog/posts/search?q=    # Search posts
```

**Key Learning:**
- Basic CRUD patterns
- Pagination (`?page=1&limit=10`)
- Filtering (`?status=published&author_id=1`)
- Search functionality
- JSON serialization

### Module 2: Task API (Project Management)
Build a task management system with advanced features.

**What You'll Build:**
- Complete task CRUD
- Task status workflow (todo → in_progress → done)
- Priority management
- Due dates and overdue detection
- User assignment
- Task statistics

**Endpoints:**
```
GET    /api/training/tasks                   # List tasks
GET    /api/training/tasks/<id>              # Get single task
POST   /api/training/tasks                   # Create task
PUT    /api/training/tasks/<id>              # Update task
DELETE /api/training/tasks/<id>              # Delete task
POST   /api/training/tasks/<id>/start        # Start task
POST   /api/training/tasks/<id>/complete     # Complete task
GET    /api/training/tasks/my                # My tasks
GET    /api/training/tasks/overdue           # Overdue tasks
GET    /api/training/tasks/stats             # Statistics
```

**Key Learning:**
- State machines and workflows
- Business logic in models
- Computed fields
- Date handling
- Action endpoints
- User-specific queries

### Module 3: User Profile API
Learn user management and file handling.

**What You'll Build:**
- User profile management
- Avatar upload
- Profile views tracking
- User search
- Leaderboard system

**Endpoints:**
```
GET    /api/training/users/profile           # My profile
PUT    /api/training/users/profile           # Update profile
GET    /api/training/users/<id>/profile      # User profile (public)
POST   /api/training/users/profile/avatar    # Upload avatar
GET    /api/training/users/search?q=         # Search users
GET    /api/training/users/leaderboard       # Top users
```

**Key Learning:**
- File uploads (binary fields)
- Public vs private data
- Data validation (email, URL, phone)
- Profile statistics
- Image handling

## 🛠️ Hands-On Exercises

### Exercise 1: Your First API Call
```bash
# Get all blog posts
curl http://localhost:8069/api/training/blog/posts

# Get a specific post
curl http://localhost:8069/api/training/blog/posts/1

# Search for posts
curl http://localhost:8069/api/training/blog/posts/search?q=python
```

### Exercise 2: Creating Data
```python
import requests

# Create a blog post (requires authentication)
url = "http://localhost:8069/api/training/blog/posts"
headers = {"Content-Type": "application/json"}
data = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "title": "My First API Post",
        "content": "<p>Learning APIs is fun!</p>",
        "status": "published",
        "tags": "api,learning,odoo"
    }
}
response = requests.post(url, json=data)
print(response.json())
```

### Exercise 3: Filtering and Pagination
```bash
# Get published posts only
curl "http://localhost:8069/api/training/blog/posts?status=published"

# Get page 2 with 20 items per page
curl "http://localhost:8069/api/training/blog/posts?page=2&limit=20"

# Get featured posts
curl "http://localhost:8069/api/training/blog/posts/featured"
```

### Exercise 4: Working with Tasks
```bash
# Get my tasks
curl "http://localhost:8069/api/training/tasks/my"

# Get overdue tasks
curl "http://localhost:8069/api/training/tasks/overdue"

# Get task statistics
curl "http://localhost:8069/api/training/tasks/stats"
```

## 📝 Code Examples

### Example 1: Understanding Models

```python
# models/api_blog_post.py
from odoo import models, fields, api

class ApiBlogPost(models.Model):
    _name = 'api.blog.post'

    title = fields.Char(string='Title', required=True)
    content = fields.Html(string='Content')
    author_id = fields.Many2one('res.users', string='Author')
    status = fields.Selection([
        ('draft', 'Draft'),
        ('published', 'Published')
    ], default='draft')

    @api.depends('title')
    def _compute_slug(self):
        for record in self:
            record.slug = record.title.lower().replace(' ', '-')
```

**What This Teaches:**
- Field types (Char, Html, Many2one, Selection)
- Required fields
- Default values
- Computed fields with @api.depends

### Example 2: Understanding Controllers

```python
# controllers/blog_api.py
from odoo import http
from odoo.http import request

class BlogApiController(http.Controller):

    @http.route('/api/training/blog/posts', type='http', auth='public', methods=['GET'])
    def get_posts(self, **params):
        # Parse pagination
        page = int(params.get('page', 1))
        limit = int(params.get('limit', 10))
        offset = (page - 1) * limit

        # Query database
        posts = request.env['api.blog.post'].sudo().search([], limit=limit, offset=offset)

        # Serialize to JSON
        posts_data = [{
            'id': post.id,
            'title': post.title,
            'content': post.content,
        } for post in posts]

        return {'posts': posts_data}
```

**What This Teaches:**
- Route decorators
- Query parameters
- ORM search operations
- JSON serialization
- Pagination logic

## 🎓 Learning Path

### Week 1: Foundations
- [ ] Install the module
- [ ] Explore the models (read the Python code)
- [ ] Test all GET endpoints with curl
- [ ] Understand model fields and relationships

### Week 2: Reading Data
- [ ] Practice searching and filtering
- [ ] Implement pagination
- [ ] Build custom search queries
- [ ] Understand domain filters

### Week 3: Writing Data
- [ ] Create blog posts via API
- [ ] Update existing records
- [ ] Handle validation errors
- [ ] Implement proper error handling

### Week 4: Advanced Features
- [ ] Implement authentication
- [ ] Add file uploads
- [ ] Build statistics endpoints
- [ ] Create custom business logic

### Week 5: Build Your Own
- [ ] Design your own API
- [ ] Create custom models
- [ ] Build custom endpoints
- [ ] Deploy to production

## 🔥 Real-World Skills You'll Gain

### For Backend Jobs
✅ **RESTful API Design** - Industry standard
✅ **Database Operations** - CRUD with ORM
✅ **Authentication** - Securing endpoints
✅ **Data Validation** - Input sanitization
✅ **Error Handling** - Proper HTTP responses
✅ **JSON APIs** - Request/response patterns
✅ **Pagination** - Handling large datasets
✅ **Search & Filter** - Query optimization
✅ **File Uploads** - Binary data handling
✅ **API Documentation** - Developer experience

### Transferable to Other Frameworks
The patterns you learn here work in:
- **Django** (Django REST Framework)
- **Flask** (Flask-RESTful)
- **FastAPI** (Python async framework)
- **Express.js** (Node.js)
- **Spring Boot** (Java)

## 📚 API Documentation

### Full API Reference

Visit these endpoints for documentation:

- **Welcome Page:** `GET /api/training`
- **All Endpoints:** `GET /api/training/endpoints`
- **Usage Examples:** `GET /api/training/examples`
- **Health Check:** `GET /api/training/health`

### Authentication

**Public Endpoints (auth='public'):**
- No authentication required
- Accessible to anyone
- Examples: GET blog posts, search

**User Endpoints (auth='user'):**
- Requires active user session
- Login via Odoo web interface first
- Examples: Create posts, update profile

### Response Format

**Success Response:**
```json
{
  "success": true,
  "data": {
    "posts": [...],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 42,
      "pages": 5
    }
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Post not found"
}
```

### Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `404` - Not Found
- `500` - Internal Server Error

## 🚀 Next Steps

### After Completing This Course

1. **Build Your Portfolio Project**
   - Create your own API (e-commerce, social media, etc.)
   - Deploy it publicly
   - Document it well
   - Add to GitHub

2. **Learn Testing**
   - Unit tests for models
   - Integration tests for APIs
   - Test-driven development

3. **Explore Other Frameworks**
   - Try Django REST Framework
   - Experiment with FastAPI
   - Compare patterns

4. **Production Skills**
   - HTTPS and SSL
   - Rate limiting
   - Caching strategies
   - Monitoring and logging

## 🤝 Contributing

Want to improve this training course?

1. Fork the repository
2. Create a feature branch
3. Add new examples or fix issues
4. Submit a pull request

## 📄 License

This module is licensed under LGPL-3.

## 💬 Support

- **Issues:** Report bugs or request features
- **Discussions:** Ask questions and share your progress
- **Documentation:** Read the full docs at `/api/training`

## 🎉 Acknowledgments

Built with ❤️ to help developers transition from Odoo to general backend development roles.

---

**Happy Coding!** 🚀

Remember: The best way to learn is by doing. Start with the examples, experiment with the code, and build your own projects!
