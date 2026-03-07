# -*- coding: utf-8 -*-
"""
Blog API Controller - Training Example

This controller demonstrates:
- RESTful API design (GET, POST, PUT, DELETE)
- JSON request/response handling
- Route decorators and parameters
- Error handling
- Pagination
- Filtering and searching
- Authentication types (public, user)

API Endpoints:
GET    /api/training/blog/posts              - List all posts (with pagination)
GET    /api/training/blog/posts/<int:id>     - Get single post
POST   /api/training/blog/posts              - Create new post
PUT    /api/training/blog/posts/<int:id>     - Update post
DELETE /api/training/blog/posts/<int:id>     - Delete post
POST   /api/training/blog/posts/<int:id>/like   - Like a post
GET    /api/training/blog/posts/featured     - Get featured posts
GET    /api/training/blog/posts/search       - Search posts
"""

import json
import logging
from odoo import http
from odoo.http import request, Response
from datetime import datetime

_logger = logging.getLogger(__name__)


class BlogApiController(http.Controller):

    # ========== Helper Methods ==========

    def _get_blog_post(self, post_id):
        """Helper to get blog post or return None"""
        return request.env['api.blog.post'].sudo().browse(post_id)

    def _serialize_post(self, post):
        """Convert blog post record to dictionary"""
        return {
            'id': post.id,
            'title': post.title,
            'slug': post.slug,
            'content': post.content,
            'excerpt': post.excerpt,
            'author': {
                'id': post.author_id.id,
                'name': post.author_name,
            },
            'published_date': post.published_date.isoformat() if post.published_date else None,
            'status': post.status,
            'is_featured': post.is_featured,
            'view_count': post.view_count,
            'like_count': post.like_count,
            'tags': post.tags.split(',') if post.tags else [],
            'reading_time_minutes': post.reading_time_minutes,
        }

    def _success_response(self, data, status=200):
        """Return successful JSON response"""
        return Response(
            json.dumps({
                'success': True,
                'data': data
            }, default=str),
            status=status,
            mimetype='application/json'
        )

    def _error_response(self, message, status=400, errors=None):
        """Return error JSON response"""
        response_data = {
            'success': False,
            'error': message
        }
        if errors:
            response_data['errors'] = errors

        return Response(
            json.dumps(response_data),
            status=status,
            mimetype='application/json'
        )

    # ========== CRUD Endpoints ==========

    @http.route('/api/training/blog/posts', type='http', auth='public', methods=['GET'], csrf=False)
    def get_posts(self, **params):
        """
        Get list of blog posts with pagination and filtering

        Query Parameters:
        - page: Page number (default: 1)
        - limit: Items per page (default: 10, max: 100)
        - status: Filter by status (draft/published/archived)
        - author_id: Filter by author ID
        - featured: Filter featured posts (true/false)

        Example: GET /api/training/blog/posts?page=1&limit=10&status=published
        """
        try:
            # Parse pagination parameters
            page = int(params.get('page', 1))
            limit = min(int(params.get('limit', 10)), 100)  # Max 100 items per page
            offset = (page - 1) * limit

            # Build domain (search filters)
            domain = []

            if params.get('status'):
                domain.append(('status', '=', params['status']))

            if params.get('author_id'):
                domain.append(('author_id', '=', int(params['author_id'])))

            if params.get('featured'):
                is_featured = params['featured'].lower() == 'true'
                domain.append(('is_featured', '=', is_featured))

            # Get posts with pagination
            Post = request.env['api.blog.post'].sudo()
            total_count = Post.search_count(domain)
            posts = Post.search(domain, limit=limit, offset=offset, order='published_date desc')

            # Serialize posts
            posts_data = [self._serialize_post(post) for post in posts]

            # Build response with pagination metadata
            return self._success_response({
                'posts': posts_data,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total_count,
                    'pages': (total_count + limit - 1) // limit,  # Ceiling division
                }
            })

        except ValueError as e:
            return self._error_response(f'Invalid parameter: {str(e)}', status=400)
        except Exception as e:
            _logger.error(f'Error fetching posts: {str(e)}')
            return self._error_response('Internal server error', status=500)

    @http.route('/api/training/blog/posts/<int:post_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_post(self, post_id):
        """
        Get single blog post by ID

        Example: GET /api/training/blog/posts/1
        """
        try:
            post = self._get_blog_post(post_id)

            if not post.exists():
                return self._error_response('Post not found', status=404)

            # Increment view count
            post.action_increment_views()

            return self._success_response({
                'post': self._serialize_post(post)
            })

        except Exception as e:
            _logger.error(f'Error fetching post {post_id}: {str(e)}')
            return self._error_response('Internal server error', status=500)

    @http.route('/api/training/blog/posts', type='json', auth='user', methods=['POST'], csrf=False)
    def create_post(self, **params):
        """
        Create new blog post (requires authentication)

        Request Body (JSON):
        {
            "title": "My Blog Post",
            "content": "<p>Post content here</p>",
            "status": "published",  // optional: draft, published, archived
            "is_featured": false,   // optional
            "tags": "python,api,tutorial"  // optional
        }

        Example:
        POST /api/training/blog/posts
        Content-Type: application/json
        """
        try:
            # Validate required fields
            if not params.get('title'):
                return {'success': False, 'error': 'Title is required'}

            if not params.get('content'):
                return {'success': False, 'error': 'Content is required'}

            # Prepare values
            vals = {
                'title': params['title'],
                'content': params['content'],
                'author_id': request.env.user.id,
                'status': params.get('status', 'draft'),
                'is_featured': params.get('is_featured', False),
                'tags': params.get('tags', ''),
            }

            # Create post
            post = request.env['api.blog.post'].create(vals)

            return {
                'success': True,
                'data': {
                    'post': self._serialize_post(post),
                    'message': 'Post created successfully'
                }
            }

        except Exception as e:
            _logger.error(f'Error creating post: {str(e)}')
            return {'success': False, 'error': str(e)}

    @http.route('/api/training/blog/posts/<int:post_id>', type='json', auth='user', methods=['PUT'], csrf=False)
    def update_post(self, post_id, **params):
        """
        Update existing blog post (requires authentication)

        Request Body (JSON):
        {
            "title": "Updated Title",  // optional
            "content": "Updated content",  // optional
            "status": "published",  // optional
            "is_featured": true,  // optional
            "tags": "updated,tags"  // optional
        }

        Example:
        PUT /api/training/blog/posts/1
        Content-Type: application/json
        """
        try:
            post = self._get_blog_post(post_id)

            if not post.exists():
                return {'success': False, 'error': 'Post not found'}

            # Check if user owns the post
            if post.author_id.id != request.env.user.id:
                return {'success': False, 'error': 'You can only edit your own posts'}

            # Prepare update values (only include provided fields)
            vals = {}
            if 'title' in params:
                vals['title'] = params['title']
            if 'content' in params:
                vals['content'] = params['content']
            if 'status' in params:
                vals['status'] = params['status']
            if 'is_featured' in params:
                vals['is_featured'] = params['is_featured']
            if 'tags' in params:
                vals['tags'] = params['tags']

            # Update post
            post.write(vals)

            return {
                'success': True,
                'data': {
                    'post': self._serialize_post(post),
                    'message': 'Post updated successfully'
                }
            }

        except Exception as e:
            _logger.error(f'Error updating post {post_id}: {str(e)}')
            return {'success': False, 'error': str(e)}

    @http.route('/api/training/blog/posts/<int:post_id>', type='json', auth='user', methods=['DELETE'], csrf=False)
    def delete_post(self, post_id):
        """
        Delete blog post (requires authentication)

        Example:
        DELETE /api/training/blog/posts/1
        """
        try:
            post = self._get_blog_post(post_id)

            if not post.exists():
                return {'success': False, 'error': 'Post not found'}

            # Check if user owns the post
            if post.author_id.id != request.env.user.id:
                return {'success': False, 'error': 'You can only delete your own posts'}

            # Delete post (will fail if published due to model constraint)
            try:
                post.unlink()
            except Exception as e:
                return {'success': False, 'error': str(e)}

            return {
                'success': True,
                'data': {
                    'message': 'Post deleted successfully'
                }
            }

        except Exception as e:
            _logger.error(f'Error deleting post {post_id}: {str(e)}')
            return {'success': False, 'error': str(e)}

    # ========== Additional Endpoints ==========

    @http.route('/api/training/blog/posts/<int:post_id>/like', type='json', auth='public', methods=['POST'], csrf=False)
    def like_post(self, post_id):
        """
        Like a blog post

        Example:
        POST /api/training/blog/posts/1/like
        """
        try:
            post = self._get_blog_post(post_id)

            if not post.exists():
                return {'success': False, 'error': 'Post not found'}

            post.action_like()

            return {
                'success': True,
                'data': {
                    'like_count': post.like_count,
                    'message': 'Post liked successfully'
                }
            }

        except Exception as e:
            _logger.error(f'Error liking post {post_id}: {str(e)}')
            return {'success': False, 'error': str(e)}

    @http.route('/api/training/blog/posts/featured', type='http', auth='public', methods=['GET'], csrf=False)
    def get_featured_posts(self):
        """
        Get all featured blog posts

        Example: GET /api/training/blog/posts/featured
        """
        try:
            Post = request.env['api.blog.post'].sudo()
            posts = Post.search([
                ('is_featured', '=', True),
                ('status', '=', 'published')
            ], order='published_date desc')

            posts_data = [self._serialize_post(post) for post in posts]

            return self._success_response({
                'posts': posts_data,
                'count': len(posts_data)
            })

        except Exception as e:
            _logger.error(f'Error fetching featured posts: {str(e)}')
            return self._error_response('Internal server error', status=500)

    @http.route('/api/training/blog/posts/search', type='http', auth='public', methods=['GET'], csrf=False)
    def search_posts(self, **params):
        """
        Search blog posts by title or content

        Query Parameters:
        - q: Search query (searches in title and content)
        - limit: Maximum results (default: 20)

        Example: GET /api/training/blog/posts/search?q=python&limit=10
        """
        try:
            query = params.get('q', '')
            limit = min(int(params.get('limit', 20)), 100)

            if not query:
                return self._error_response('Search query (q) is required', status=400)

            # Search in title and content
            Post = request.env['api.blog.post'].sudo()
            posts = Post.search([
                '|',
                ('title', 'ilike', query),
                ('content', 'ilike', query),
                ('status', '=', 'published')
            ], limit=limit, order='published_date desc')

            posts_data = [self._serialize_post(post) for post in posts]

            return self._success_response({
                'posts': posts_data,
                'count': len(posts_data),
                'query': query
            })

        except Exception as e:
            _logger.error(f'Error searching posts: {str(e)}')
            return self._error_response('Internal server error', status=500)
