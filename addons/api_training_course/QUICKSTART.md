# Quick Start Guide - API Training Course

Get started with API development in **5 minutes**!

## Step 1: Install (2 minutes)

1. **Copy module to addons:**
   ```bash
   # Already in /home/ubuntu/addons/api_training_course
   ```

2. **Restart Odoo:**
   ```bash
   # If using docker-compose
   docker-compose restart
   ```

3. **Install the module:**
   - Open Odoo: `http://localhost:8069`
   - Go to **Apps**
   - Click **Update Apps List**
   - Search for **"API Training"**
   - Click **Install**

## Step 2: Verify Installation (1 minute)

Open in your browser:
```
http://localhost:8069/api/training
```

You should see the API welcome page with documentation!

## Step 3: Your First API Call (1 minute)

### Option A: Browser (easiest)
Just visit this URL:
```
http://localhost:8069/api/training/blog/posts
```

You'll see a JSON response with blog posts! 🎉

### Option B: Command Line
```bash
curl http://localhost:8069/api/training/blog/posts
```

### Option C: Python
```python
import requests
response = requests.get('http://localhost:8069/api/training/blog/posts')
print(response.json())
```

## Step 4: Explore Demo Data (1 minute)

The module includes demo data to get you started:

- **4 Blog Posts** about API development
- **4 Tasks** showing different statuses
- **1 User Profile** with example data

Try these endpoints:

```bash
# Get all blog posts
curl http://localhost:8069/api/training/blog/posts

# Get featured posts
curl http://localhost:8069/api/training/blog/posts/featured

# Search posts
curl http://localhost:8069/api/training/blog/posts/search?q=api

# Get all endpoints list
curl http://localhost:8069/api/training/endpoints

# Health check
curl http://localhost:8069/api/training/health
```

## Step 5: What's Next?

### For Beginners:
1. Read the **README.md** for full course overview
2. Follow the **Learning Path** (Week 1-5)
3. Read the **source code** in `models/` and `controllers/`

### For Intermediate:
1. Check **TESTING_GUIDE.md** for testing all endpoints
2. Modify existing models and controllers
3. Create your own custom endpoints

### For Advanced:
1. Build your own API from scratch
2. Add authentication and authorization
3. Deploy to production

## Quick Reference

### Key Files to Study

1. **Models (Database):**
   - `models/api_blog_post.py` - Blog post model
   - `models/api_task.py` - Task management model
   - `models/api_user_profile.py` - User profile model

2. **Controllers (API Endpoints):**
   - `controllers/blog_api.py` - Blog CRUD API
   - `controllers/task_api.py` - Task management API
   - `controllers/user_api.py` - User profile API
   - `controllers/main.py` - Documentation endpoints

3. **Documentation:**
   - `README.md` - Full course guide
   - `TESTING_GUIDE.md` - Testing all endpoints
   - `QUICKSTART.md` - This file

### Essential Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/training` | API documentation |
| `GET /api/training/endpoints` | List all endpoints |
| `GET /api/training/examples` | Usage examples |
| `GET /api/training/health` | Health check |
| `GET /api/training/blog/posts` | List blog posts |
| `GET /api/training/blog/posts/<id>` | Get single post |
| `GET /api/training/blog/posts/search?q=` | Search posts |
| `GET /api/training/tasks` | List tasks (auth) |
| `GET /api/training/tasks/stats` | Task statistics (auth) |
| `GET /api/training/users/profile` | My profile (auth) |

### Odoo Menu Access

After installation, find these in Odoo:

**Apps Menu → API Training**
- Blog Posts (view/edit in Odoo UI)
- Tasks (view/edit in Odoo UI)
- User Profiles (view/edit in Odoo UI)

## Common Questions

### Q: How do I test authenticated endpoints?
**A:** Login to Odoo first, then use the same browser/session for API calls. For curl, save cookies:
```bash
curl -c cookies.txt -d "login=admin&password=admin" http://localhost:8069/web/login
curl -b cookies.txt http://localhost:8069/api/training/tasks
```

### Q: What's the difference between type='http' and type='json'?
**A:**
- `type='http'` - Returns plain HTTP response, access via GET/POST directly
- `type='json'` - Expects JSON-RPC format, returns JSON, used for POST/PUT/DELETE

### Q: Where do I find API examples?
**A:**
- Visit: `http://localhost:8069/api/training/examples`
- Read: `TESTING_GUIDE.md`
- Check: `controllers/*.py` source code

### Q: Can I use this for my portfolio?
**A:** Yes! Build on top of this:
1. Add your own models (products, orders, etc.)
2. Create custom endpoints
3. Deploy publicly
4. Add to your GitHub/resume

### Q: How is this different from Django/Flask?
**A:** Very similar! The patterns are nearly identical:
- Models = Django Models / SQLAlchemy
- Controllers = Django Views / Flask Routes
- ORM = Django ORM / SQLAlchemy
- Routes = URL patterns

## Need Help?

- **Documentation:** Visit `/api/training` in your browser
- **Source Code:** Read the Python files with comments
- **Examples:** Check `TESTING_GUIDE.md`
- **Issues:** Create issue on GitHub

---

**You're ready to go! Start with the blog API and work your way through the modules.** 🚀

Happy learning!
