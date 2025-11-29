# -*- coding: utf-8 -*-
"""
Task Model - Training Example

This model demonstrates:
- Many2one relationships (project, assigned user)
- Selection fields with states
- Priority fields
- Date handling
- Search and filtering patterns
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class ApiTask(models.Model):
    _name = 'api.task'
    _description = 'Task for API Training'
    _order = 'priority desc, due_date asc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Basic Fields
    name = fields.Char(
        string='Task Name',
        required=True,
        tracking=True
    )

    description = fields.Text(
        string='Description'
    )

    # Assignment
    assigned_to = fields.Many2one(
        'res.users',
        string='Assigned To',
        tracking=True
    )

    assigned_to_name = fields.Char(
        related='assigned_to.name',
        string='Assignee Name',
        readonly=True
    )

    created_by = fields.Many2one(
        'res.users',
        string='Created By',
        default=lambda self: self.env.user,
        readonly=True
    )

    # Project (simplified - could be a separate model)
    project_name = fields.Char(
        string='Project',
        help='Project name this task belongs to'
    )

    # Status & Priority
    status = fields.Selection([
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'In Review'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='todo', required=True, tracking=True)

    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent')
    ], string='Priority', default='1', tracking=True)

    # Dates
    due_date = fields.Date(
        string='Due Date',
        tracking=True
    )

    completed_date = fields.Datetime(
        string='Completed Date',
        readonly=True
    )

    # Computed Fields
    is_overdue = fields.Boolean(
        string='Overdue',
        compute='_compute_is_overdue',
        search='_search_is_overdue'
    )

    days_until_due = fields.Integer(
        string='Days Until Due',
        compute='_compute_days_until_due'
    )

    # Statistics
    estimated_hours = fields.Float(
        string='Estimated Hours',
        help='Estimated time to complete in hours'
    )

    actual_hours = fields.Float(
        string='Actual Hours',
        help='Actual time spent in hours'
    )

    # Progress
    progress = fields.Integer(
        string='Progress (%)',
        default=0,
        help='Task completion percentage (0-100)'
    )

    # ========== Computed Methods ==========

    @api.depends('due_date', 'status')
    def _compute_is_overdue(self):
        """Check if task is overdue"""
        today = fields.Date.today()
        for record in self:
            record.is_overdue = (
                record.due_date and
                record.due_date < today and
                record.status not in ['done', 'cancelled']
            )

    def _search_is_overdue(self, operator, value):
        """Enable searching by overdue status"""
        today = fields.Date.today()
        if (operator == '=' and value) or (operator == '!=' and not value):
            # Search for overdue tasks
            return [
                ('due_date', '<', today),
                ('status', 'not in', ['done', 'cancelled'])
            ]
        else:
            # Search for not overdue tasks
            return [
                '|', '|',
                ('due_date', '>=', today),
                ('due_date', '=', False),
                ('status', 'in', ['done', 'cancelled'])
            ]

    @api.depends('due_date')
    def _compute_days_until_due(self):
        """Calculate days until due date"""
        today = fields.Date.today()
        for record in self:
            if record.due_date:
                delta = record.due_date - today
                record.days_until_due = delta.days
            else:
                record.days_until_due = 0

    # ========== Constraints ==========

    @api.constrains('progress')
    def _check_progress(self):
        """Ensure progress is between 0 and 100"""
        for record in self:
            if record.progress < 0 or record.progress > 100:
                raise ValidationError('Progress must be between 0 and 100')

    @api.constrains('estimated_hours', 'actual_hours')
    def _check_hours(self):
        """Ensure hours are non-negative"""
        for record in self:
            if record.estimated_hours < 0 or record.actual_hours < 0:
                raise ValidationError('Hours cannot be negative')

    @api.constrains('due_date')
    def _check_due_date(self):
        """Warn if due date is in the past for new tasks"""
        today = fields.Date.today()
        for record in self:
            if record.due_date and record.due_date < today and record.status == 'todo':
                # This is a warning, not a hard constraint
                # In real apps, you might log this or notify the user
                pass

    # ========== Business Methods ==========

    def action_start(self):
        """Start working on the task"""
        self.write({'status': 'in_progress'})
        return True

    def action_complete(self):
        """Mark task as done"""
        self.write({
            'status': 'done',
            'completed_date': fields.Datetime.now(),
            'progress': 100
        })
        return True

    def action_cancel(self):
        """Cancel the task"""
        self.write({'status': 'cancelled'})
        return True

    def action_reopen(self):
        """Reopen a completed/cancelled task"""
        self.write({
            'status': 'todo',
            'completed_date': False
        })
        return True

    # ========== CRUD Override Examples ==========

    @api.model
    def create(self, vals):
        """Override create to set default due date if not provided"""
        if not vals.get('due_date'):
            # Default to 7 days from now
            vals['due_date'] = fields.Date.today() + timedelta(days=7)

        return super(ApiTask, self).create(vals)

    def write(self, vals):
        """Override write to auto-update progress based on status"""
        if vals.get('status') == 'done' and 'progress' not in vals:
            vals['progress'] = 100
            vals['completed_date'] = fields.Datetime.now()
        elif vals.get('status') == 'todo' and 'progress' not in vals:
            vals['progress'] = 0

        return super(ApiTask, self).write(vals)

    # ========== Search/Filter Helper Methods ==========

    @api.model
    def get_my_tasks(self):
        """Get tasks assigned to current user"""
        return self.search([('assigned_to', '=', self.env.user.id)])

    @api.model
    def get_overdue_tasks(self):
        """Get all overdue tasks"""
        return self.search([('is_overdue', '=', True)])

    @api.model
    def get_tasks_by_priority(self, priority):
        """Get tasks by priority level"""
        return self.search([('priority', '=', str(priority))])
