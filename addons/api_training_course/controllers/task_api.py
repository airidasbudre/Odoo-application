# -*- coding: utf-8 -*-
"""
Task API Controller - Training Example

This controller demonstrates:
- Task management API
- Complex filtering (status, priority, overdue)
- Action endpoints (start, complete, cancel)
- User-specific queries (my tasks)
- Statistics endpoints

API Endpoints:
GET    /api/training/tasks                    - List all tasks
GET    /api/training/tasks/<int:id>           - Get single task
POST   /api/training/tasks                    - Create new task
PUT    /api/training/tasks/<int:id>           - Update task
DELETE /api/training/tasks/<int:id>           - Delete task
POST   /api/training/tasks/<int:id>/start     - Start task
POST   /api/training/tasks/<int:id>/complete  - Complete task
GET    /api/training/tasks/my                 - Get my tasks
GET    /api/training/tasks/overdue            - Get overdue tasks
GET    /api/training/tasks/stats              - Get task statistics
"""

import json
import logging
from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


class TaskApiController(http.Controller):

    # ========== Helper Methods ==========

    def _get_task(self, task_id):
        """Helper to get task or return None"""
        return request.env['api.task'].sudo().browse(task_id)

    def _serialize_task(self, task):
        """Convert task record to dictionary"""
        return {
            'id': task.id,
            'name': task.name,
            'description': task.description,
            'assigned_to': {
                'id': task.assigned_to.id,
                'name': task.assigned_to_name,
            } if task.assigned_to else None,
            'created_by': {
                'id': task.created_by.id,
                'name': task.created_by.name,
            } if task.created_by else None,
            'project_name': task.project_name,
            'status': task.status,
            'priority': task.priority,
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'completed_date': task.completed_date.isoformat() if task.completed_date else None,
            'is_overdue': task.is_overdue,
            'days_until_due': task.days_until_due,
            'estimated_hours': task.estimated_hours,
            'actual_hours': task.actual_hours,
            'progress': task.progress,
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

    def _error_response(self, message, status=400):
        """Return error JSON response"""
        return Response(
            json.dumps({
                'success': False,
                'error': message
            }),
            status=status,
            mimetype='application/json'
        )

    # ========== CRUD Endpoints ==========

    @http.route('/api/training/tasks', type='http', auth='user', methods=['GET'], csrf=False)
    def get_tasks(self, **params):
        """
        Get list of tasks with filtering

        Query Parameters:
        - page: Page number (default: 1)
        - limit: Items per page (default: 20)
        - status: Filter by status (todo/in_progress/review/done/cancelled)
        - priority: Filter by priority (0/1/2/3)
        - assigned_to: Filter by assigned user ID
        - project: Filter by project name
        - overdue: Show only overdue tasks (true/false)

        Example: GET /api/training/tasks?status=in_progress&priority=3
        """
        try:
            # Parse pagination
            page = int(params.get('page', 1))
            limit = min(int(params.get('limit', 20)), 100)
            offset = (page - 1) * limit

            # Build domain
            domain = []

            if params.get('status'):
                domain.append(('status', '=', params['status']))

            if params.get('priority'):
                domain.append(('priority', '=', params['priority']))

            if params.get('assigned_to'):
                domain.append(('assigned_to', '=', int(params['assigned_to'])))

            if params.get('project'):
                domain.append(('project_name', 'ilike', params['project']))

            if params.get('overdue'):
                is_overdue = params['overdue'].lower() == 'true'
                domain.append(('is_overdue', '=', is_overdue))

            # Get tasks
            Task = request.env['api.task'].sudo()
            total_count = Task.search_count(domain)
            tasks = Task.search(domain, limit=limit, offset=offset)

            # Serialize
            tasks_data = [self._serialize_task(task) for task in tasks]

            return self._success_response({
                'tasks': tasks_data,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total_count,
                    'pages': (total_count + limit - 1) // limit,
                }
            })

        except Exception as e:
            _logger.error(f'Error fetching tasks: {str(e)}')
            return self._error_response('Internal server error', status=500)

    @http.route('/api/training/tasks/<int:task_id>', type='http', auth='user', methods=['GET'], csrf=False)
    def get_task(self, task_id):
        """
        Get single task by ID

        Example: GET /api/training/tasks/1
        """
        try:
            task = self._get_task(task_id)

            if not task.exists():
                return self._error_response('Task not found', status=404)

            return self._success_response({
                'task': self._serialize_task(task)
            })

        except Exception as e:
            _logger.error(f'Error fetching task {task_id}: {str(e)}')
            return self._error_response('Internal server error', status=500)

    @http.route('/api/training/tasks', type='json', auth='user', methods=['POST'], csrf=False)
    def create_task(self, **params):
        """
        Create new task

        Request Body (JSON):
        {
            "name": "Task name",
            "description": "Task description",  // optional
            "assigned_to": 1,  // user ID, optional
            "project_name": "Project Alpha",  // optional
            "status": "todo",  // optional
            "priority": "1",  // optional: 0=Low, 1=Normal, 2=High, 3=Urgent
            "due_date": "2024-12-31",  // optional, format: YYYY-MM-DD
            "estimated_hours": 8.5  // optional
        }
        """
        try:
            # Validate
            if not params.get('name'):
                return {'success': False, 'error': 'Task name is required'}

            # Prepare values
            vals = {
                'name': params['name'],
                'description': params.get('description', ''),
                'created_by': request.env.user.id,
                'status': params.get('status', 'todo'),
                'priority': params.get('priority', '1'),
                'project_name': params.get('project_name', ''),
            }

            if params.get('assigned_to'):
                vals['assigned_to'] = params['assigned_to']

            if params.get('due_date'):
                vals['due_date'] = params['due_date']

            if params.get('estimated_hours'):
                vals['estimated_hours'] = float(params['estimated_hours'])

            # Create task
            task = request.env['api.task'].create(vals)

            return {
                'success': True,
                'data': {
                    'task': self._serialize_task(task),
                    'message': 'Task created successfully'
                }
            }

        except Exception as e:
            _logger.error(f'Error creating task: {str(e)}')
            return {'success': False, 'error': str(e)}

    @http.route('/api/training/tasks/<int:task_id>', type='json', auth='user', methods=['PUT'], csrf=False)
    def update_task(self, task_id, **params):
        """
        Update existing task

        Request Body (JSON): Same as create, all fields optional
        """
        try:
            task = self._get_task(task_id)

            if not task.exists():
                return {'success': False, 'error': 'Task not found'}

            # Prepare update values
            vals = {}
            updateable_fields = ['name', 'description', 'assigned_to', 'project_name',
                                 'status', 'priority', 'due_date', 'estimated_hours',
                                 'actual_hours', 'progress']

            for field in updateable_fields:
                if field in params:
                    vals[field] = params[field]

            # Update task
            task.write(vals)

            return {
                'success': True,
                'data': {
                    'task': self._serialize_task(task),
                    'message': 'Task updated successfully'
                }
            }

        except Exception as e:
            _logger.error(f'Error updating task {task_id}: {str(e)}')
            return {'success': False, 'error': str(e)}

    @http.route('/api/training/tasks/<int:task_id>', type='json', auth='user', methods=['DELETE'], csrf=False)
    def delete_task(self, task_id):
        """
        Delete task

        Example: DELETE /api/training/tasks/1
        """
        try:
            task = self._get_task(task_id)

            if not task.exists():
                return {'success': False, 'error': 'Task not found'}

            task.unlink()

            return {
                'success': True,
                'data': {'message': 'Task deleted successfully'}
            }

        except Exception as e:
            _logger.error(f'Error deleting task {task_id}: {str(e)}')
            return {'success': False, 'error': str(e)}

    # ========== Action Endpoints ==========

    @http.route('/api/training/tasks/<int:task_id>/start', type='json', auth='user', methods=['POST'], csrf=False)
    def start_task(self, task_id):
        """
        Start working on task (sets status to 'in_progress')

        Example: POST /api/training/tasks/1/start
        """
        try:
            task = self._get_task(task_id)

            if not task.exists():
                return {'success': False, 'error': 'Task not found'}

            task.action_start()

            return {
                'success': True,
                'data': {
                    'task': self._serialize_task(task),
                    'message': 'Task started successfully'
                }
            }

        except Exception as e:
            _logger.error(f'Error starting task {task_id}: {str(e)}')
            return {'success': False, 'error': str(e)}

    @http.route('/api/training/tasks/<int:task_id>/complete', type='json', auth='user', methods=['POST'], csrf=False)
    def complete_task(self, task_id):
        """
        Mark task as complete

        Example: POST /api/training/tasks/1/complete
        """
        try:
            task = self._get_task(task_id)

            if not task.exists():
                return {'success': False, 'error': 'Task not found'}

            task.action_complete()

            return {
                'success': True,
                'data': {
                    'task': self._serialize_task(task),
                    'message': 'Task completed successfully'
                }
            }

        except Exception as e:
            _logger.error(f'Error completing task {task_id}: {str(e)}')
            return {'success': False, 'error': str(e)}

    @http.route('/api/training/tasks/<int:task_id>/cancel', type='json', auth='user', methods=['POST'], csrf=False)
    def cancel_task(self, task_id):
        """
        Cancel task

        Example: POST /api/training/tasks/1/cancel
        """
        try:
            task = self._get_task(task_id)

            if not task.exists():
                return {'success': False, 'error': 'Task not found'}

            task.action_cancel()

            return {
                'success': True,
                'data': {
                    'task': self._serialize_task(task),
                    'message': 'Task cancelled successfully'
                }
            }

        except Exception as e:
            _logger.error(f'Error cancelling task {task_id}: {str(e)}')
            return {'success': False, 'error': str(e)}

    # ========== Query Endpoints ==========

    @http.route('/api/training/tasks/my', type='http', auth='user', methods=['GET'], csrf=False)
    def get_my_tasks(self, **params):
        """
        Get tasks assigned to current user

        Query Parameters:
        - status: Filter by status (optional)

        Example: GET /api/training/tasks/my?status=in_progress
        """
        try:
            domain = [('assigned_to', '=', request.env.user.id)]

            if params.get('status'):
                domain.append(('status', '=', params['status']))

            Task = request.env['api.task'].sudo()
            tasks = Task.search(domain)

            tasks_data = [self._serialize_task(task) for task in tasks]

            return self._success_response({
                'tasks': tasks_data,
                'count': len(tasks_data)
            })

        except Exception as e:
            _logger.error(f'Error fetching my tasks: {str(e)}')
            return self._error_response('Internal server error', status=500)

    @http.route('/api/training/tasks/overdue', type='http', auth='user', methods=['GET'], csrf=False)
    def get_overdue_tasks(self):
        """
        Get all overdue tasks

        Example: GET /api/training/tasks/overdue
        """
        try:
            Task = request.env['api.task'].sudo()
            tasks = Task.search([('is_overdue', '=', True)])

            tasks_data = [self._serialize_task(task) for task in tasks]

            return self._success_response({
                'tasks': tasks_data,
                'count': len(tasks_data)
            })

        except Exception as e:
            _logger.error(f'Error fetching overdue tasks: {str(e)}')
            return self._error_response('Internal server error', status=500)

    @http.route('/api/training/tasks/stats', type='http', auth='user', methods=['GET'], csrf=False)
    def get_task_stats(self):
        """
        Get task statistics

        Example: GET /api/training/tasks/stats
        """
        try:
            Task = request.env['api.task'].sudo()

            stats = {
                'total': Task.search_count([]),
                'by_status': {
                    'todo': Task.search_count([('status', '=', 'todo')]),
                    'in_progress': Task.search_count([('status', '=', 'in_progress')]),
                    'review': Task.search_count([('status', '=', 'review')]),
                    'done': Task.search_count([('status', '=', 'done')]),
                    'cancelled': Task.search_count([('status', '=', 'cancelled')]),
                },
                'by_priority': {
                    'low': Task.search_count([('priority', '=', '0')]),
                    'normal': Task.search_count([('priority', '=', '1')]),
                    'high': Task.search_count([('priority', '=', '2')]),
                    'urgent': Task.search_count([('priority', '=', '3')]),
                },
                'overdue': Task.search_count([('is_overdue', '=', True)]),
                'my_tasks': Task.search_count([('assigned_to', '=', request.env.user.id)]),
            }

            return self._success_response(stats)

        except Exception as e:
            _logger.error(f'Error fetching task stats: {str(e)}')
            return self._error_response('Internal server error', status=500)
