# -*- coding: utf-8 -*-
"""
Main API Controller - Training Example

This controller demonstrates:
- Welcome/documentation endpoint
- API health check
- API versioning
- Rate limiting info
- Available endpoints listing

API Endpoints:
GET /api/training                    - API documentation and welcome
GET /api/training/health             - Health check
GET /api/training/endpoints          - List all available endpoints
"""

import json
import logging
from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


class MainApiController(http.Controller):

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

    @http.route('/api/training', type='http', auth='public', methods=['GET'], csrf=False)
    def api_documentation(self):
        """
        API Training Course - Welcome and Documentation

        Example: GET /api/training
        """
        doc = {
            'name': 'API Training Course',
            'version': '1.0.0',
            'description': 'Learn backend API development with Odoo',
            'base_url': '/api/training',
            'authentication': {
                'public': 'No authentication required',
                'user': 'Requires user session authentication',
                'note': 'For type=json endpoints, send credentials via session/cookies'
            },
            'features': [
                'RESTful API Design',
                'CRUD Operations',
                'Authentication & Authorization',
                'Pagination & Filtering',
                'Search & Query',
                'File Uploads',
                'Error Handling',
                'JSON Request/Response'
            ],
            'modules': {
                'blog': {
                    'description': 'Blog post management',
                    'endpoints': '/api/training/blog/*'
                },
                'tasks': {
                    'description': 'Task management system',
                    'endpoints': '/api/training/tasks/*'
                },
                'users': {
                    'description': 'User profile management',
                    'endpoints': '/api/training/users/*'
                }
            },
            'getting_started': {
                'step_1': 'Install the api_training_course module in Odoo',
                'step_2': 'Access /api/training/endpoints to see all available endpoints',
                'step_3': 'Try GET /api/training/blog/posts to fetch blog posts',
                'step_4': 'Read the controller source code to understand implementation',
                'step_5': 'Experiment with creating your own endpoints'
            },
            'resources': {
                'health_check': '/api/training/health',
                'endpoints_list': '/api/training/endpoints',
                'blog_api': '/api/training/blog/posts',
                'tasks_api': '/api/training/tasks',
                'profile_api': '/api/training/users/profile'
            },
            'learning_path': [
                '1. Understand models (ORM, fields, constraints)',
                '2. Learn controllers (routing, request handling)',
                '3. Master CRUD operations (create, read, update, delete)',
                '4. Implement authentication & authorization',
                '5. Add pagination, filtering, and search',
                '6. Handle file uploads and binary data',
                '7. Implement proper error handling',
                '8. Write API documentation',
                '9. Test your APIs',
                '10. Deploy to production'
            ],
            'tips': [
                'Always validate input data',
                'Use proper HTTP status codes',
                'Return consistent JSON structure',
                'Implement proper error messages',
                'Add pagination for list endpoints',
                'Use sudo() carefully for permissions',
                'Log errors for debugging',
                'Document your APIs'
            ]
        }

        return self._success_response(doc)

    @http.route('/api/training/health', type='http', auth='public', methods=['GET'], csrf=False)
    def health_check(self):
        """
        API Health Check

        Example: GET /api/training/health
        """
        try:
            # Check database connection
            request.env.cr.execute("SELECT 1")

            # Check models are loaded
            blog_count = request.env['api.blog.post'].sudo().search_count([])
            task_count = request.env['api.task'].sudo().search_count([])

            health = {
                'status': 'healthy',
                'database': 'connected',
                'timestamp': http.request.httprequest.environ.get('HTTP_HOST'),
                'models': {
                    'blog_posts': blog_count,
                    'tasks': task_count,
                },
                'version': '1.0.0'
            }

            return self._success_response(health)

        except Exception as e:
            _logger.error(f'Health check failed: {str(e)}')
            return Response(
                json.dumps({
                    'success': False,
                    'status': 'unhealthy',
                    'error': str(e)
                }),
                status=500,
                mimetype='application/json'
            )

    @http.route('/api/training/endpoints', type='http', auth='public', methods=['GET'], csrf=False)
    def list_endpoints(self):
        """
        List all available API endpoints

        Example: GET /api/training/endpoints
        """
        endpoints = {
            'meta': {
                'GET /api/training': 'API documentation and welcome',
                'GET /api/training/health': 'Health check endpoint',
                'GET /api/training/endpoints': 'This endpoint - list all routes',
            },
            'blog_api': {
                'GET /api/training/blog/posts': 'List all blog posts (with pagination)',
                'GET /api/training/blog/posts/<id>': 'Get single blog post',
                'POST /api/training/blog/posts': 'Create new blog post (auth required)',
                'PUT /api/training/blog/posts/<id>': 'Update blog post (auth required)',
                'DELETE /api/training/blog/posts/<id>': 'Delete blog post (auth required)',
                'POST /api/training/blog/posts/<id>/like': 'Like a blog post',
                'GET /api/training/blog/posts/featured': 'Get featured posts',
                'GET /api/training/blog/posts/search': 'Search blog posts',
            },
            'task_api': {
                'GET /api/training/tasks': 'List all tasks (auth required)',
                'GET /api/training/tasks/<id>': 'Get single task (auth required)',
                'POST /api/training/tasks': 'Create new task (auth required)',
                'PUT /api/training/tasks/<id>': 'Update task (auth required)',
                'DELETE /api/training/tasks/<id>': 'Delete task (auth required)',
                'POST /api/training/tasks/<id>/start': 'Start task (auth required)',
                'POST /api/training/tasks/<id>/complete': 'Complete task (auth required)',
                'POST /api/training/tasks/<id>/cancel': 'Cancel task (auth required)',
                'GET /api/training/tasks/my': 'Get my tasks (auth required)',
                'GET /api/training/tasks/overdue': 'Get overdue tasks (auth required)',
                'GET /api/training/tasks/stats': 'Get task statistics (auth required)',
            },
            'user_api': {
                'GET /api/training/users/profile': 'Get my profile (auth required)',
                'PUT /api/training/users/profile': 'Update my profile (auth required)',
                'GET /api/training/users/<id>/profile': 'Get user profile (public)',
                'POST /api/training/users/profile/avatar': 'Upload avatar (auth required)',
                'GET /api/training/users/search': 'Search users',
                'GET /api/training/users/leaderboard': 'Get user leaderboard',
            },
            'notes': {
                'auth_public': 'No authentication required',
                'auth_user': 'Requires user session authentication',
                'query_params': 'Use ?param=value for query parameters',
                'json_body': 'Send JSON in request body for POST/PUT',
                'pagination': 'Use ?page=1&limit=10 for pagination',
            }
        }

        return self._success_response(endpoints)

    @http.route('/api/training/examples', type='http', auth='public', methods=['GET'], csrf=False)
    def api_examples(self):
        """
        API Usage Examples

        Example: GET /api/training/examples
        """
        examples = {
            'getting_started': {
                'description': 'Simple examples to get started',
                'examples': [
                    {
                        'title': 'List all blog posts',
                        'method': 'GET',
                        'url': '/api/training/blog/posts',
                        'curl': 'curl http://localhost:8069/api/training/blog/posts'
                    },
                    {
                        'title': 'Get a single post',
                        'method': 'GET',
                        'url': '/api/training/blog/posts/1',
                        'curl': 'curl http://localhost:8069/api/training/blog/posts/1'
                    },
                    {
                        'title': 'Search posts',
                        'method': 'GET',
                        'url': '/api/training/blog/posts/search?q=python',
                        'curl': 'curl http://localhost:8069/api/training/blog/posts/search?q=python'
                    }
                ]
            },
            'pagination': {
                'description': 'Examples using pagination',
                'examples': [
                    {
                        'title': 'Get page 2 with 20 items',
                        'method': 'GET',
                        'url': '/api/training/blog/posts?page=2&limit=20',
                        'curl': 'curl http://localhost:8069/api/training/blog/posts?page=2&limit=20'
                    }
                ]
            },
            'filtering': {
                'description': 'Examples using filters',
                'examples': [
                    {
                        'title': 'Get published posts only',
                        'method': 'GET',
                        'url': '/api/training/blog/posts?status=published',
                        'curl': 'curl http://localhost:8069/api/training/blog/posts?status=published'
                    },
                    {
                        'title': 'Get high priority tasks',
                        'method': 'GET',
                        'url': '/api/training/tasks?priority=3',
                        'curl': 'curl http://localhost:8069/api/training/tasks?priority=3',
                        'note': 'Requires authentication'
                    }
                ]
            },
            'creating_data': {
                'description': 'Examples creating data via POST',
                'note': 'These require authentication and type=json',
                'examples': [
                    {
                        'title': 'Create a blog post',
                        'method': 'POST',
                        'url': '/api/training/blog/posts',
                        'body': {
                            'title': 'My First API Post',
                            'content': '<p>Learning APIs with Odoo!</p>',
                            'status': 'published',
                            'tags': 'api,learning,odoo'
                        }
                    },
                    {
                        'title': 'Create a task',
                        'method': 'POST',
                        'url': '/api/training/tasks',
                        'body': {
                            'name': 'Complete API Training',
                            'description': 'Finish all training modules',
                            'priority': '2',
                            'status': 'todo'
                        }
                    }
                ]
            }
        }

        return self._success_response(examples)
