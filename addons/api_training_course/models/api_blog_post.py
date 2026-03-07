# -*- coding: utf-8 -*-
"""
Blog Post Model - Training Example

This model demonstrates:
- Basic field types (Char, Text, Html, Integer, Boolean, Date)
- Computed fields
- Model constraints
- CRUD operations via ORM
- Many2one relationships (author)
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ApiBlogPost(models.Model):
    _name = 'api.blog.post'
    _description = 'Blog Post for API Training'
    _order = 'published_date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # For tracking changes

    # Basic Fields
    title = fields.Char(
        string='Title',
        required=True,
        tracking=True,
        help='The blog post title'
    )

    slug = fields.Char(
        string='URL Slug',
        compute='_compute_slug',
        store=True,
        help='URL-friendly version of title'
    )

    content = fields.Html(
        string='Content',
        required=True,
        help='The main blog post content'
    )

    excerpt = fields.Text(
        string='Excerpt',
        compute='_compute_excerpt',
        store=True,
        help='Short preview (first 200 chars)'
    )

    # Metadata
    author_id = fields.Many2one(
        'res.users',
        string='Author',
        default=lambda self: self.env.user,
        required=True,
        tracking=True
    )

    author_name = fields.Char(
        related='author_id.name',
        string='Author Name',
        readonly=True
    )

    published_date = fields.Datetime(
        string='Published Date',
        default=fields.Datetime.now,
        tracking=True
    )

    # Status & Visibility
    status = fields.Selection([
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived')
    ], string='Status', default='draft', required=True, tracking=True)

    is_featured = fields.Boolean(
        string='Featured',
        default=False,
        help='Show on homepage'
    )

    # Statistics
    view_count = fields.Integer(
        string='View Count',
        default=0,
        readonly=True
    )

    like_count = fields.Integer(
        string='Likes',
        default=0
    )

    # Categories (simplified - using tags as text)
    tags = fields.Char(
        string='Tags',
        help='Comma-separated tags (e.g., "python,api,tutorial")'
    )

    # Computed field for reading time
    reading_time_minutes = fields.Integer(
        string='Reading Time (min)',
        compute='_compute_reading_time',
        store=True,
        help='Estimated reading time in minutes'
    )

    # ========== Computed Methods ==========

    @api.depends('title')
    def _compute_slug(self):
        """Generate URL-friendly slug from title"""
        for record in self:
            if record.title:
                # Simple slug: lowercase, replace spaces with hyphens
                slug = record.title.lower()
                slug = ''.join(c if c.isalnum() or c.isspace() else '' for c in slug)
                slug = '-'.join(slug.split())
                record.slug = slug
            else:
                record.slug = False

    @api.depends('content')
    def _compute_excerpt(self):
        """Generate excerpt from content (first 200 characters)"""
        for record in self:
            if record.content:
                # Remove HTML tags (simple approach)
                import re
                clean_text = re.sub('<[^<]+?>', '', record.content)
                record.excerpt = clean_text[:200] + ('...' if len(clean_text) > 200 else '')
            else:
                record.excerpt = ''

    @api.depends('content')
    def _compute_reading_time(self):
        """Calculate reading time (average 200 words per minute)"""
        for record in self:
            if record.content:
                import re
                clean_text = re.sub('<[^<]+?>', '', record.content)
                word_count = len(clean_text.split())
                record.reading_time_minutes = max(1, word_count // 200)
            else:
                record.reading_time_minutes = 0

    # ========== Constraints ==========

    @api.constrains('title')
    def _check_title_length(self):
        """Ensure title is at least 5 characters"""
        for record in self:
            if record.title and len(record.title) < 5:
                raise ValidationError('Title must be at least 5 characters long')

    @api.constrains('view_count', 'like_count')
    def _check_positive_counts(self):
        """Ensure counts are non-negative"""
        for record in self:
            if record.view_count < 0 or record.like_count < 0:
                raise ValidationError('Counts cannot be negative')

    # ========== Business Methods ==========

    def action_publish(self):
        """Publish the blog post"""
        self.write({
            'status': 'published',
            'published_date': fields.Datetime.now()
        })
        return True

    def action_archive_post(self):
        """Archive the blog post"""
        self.write({'status': 'archived'})
        return True

    def action_increment_views(self):
        """Increment view count (for API tracking)"""
        for record in self:
            record.view_count += 1
        return True

    def action_like(self):
        """Like the post"""
        for record in self:
            record.like_count += 1
        return True

    # ========== CRUD Override Examples ==========

    @api.model
    def create(self, vals):
        """Override create to add custom logic"""
        # Auto-publish if user wants it
        if vals.get('status') == 'published' and not vals.get('published_date'):
            vals['published_date'] = fields.Datetime.now()

        return super(ApiBlogPost, self).create(vals)

    def write(self, vals):
        """Override write to add custom logic"""
        # Update published_date when publishing
        if vals.get('status') == 'published' and self.status != 'published':
            vals['published_date'] = fields.Datetime.now()

        return super(ApiBlogPost, self).write(vals)

    def unlink(self):
        """Override unlink to add custom logic"""
        # Prevent deletion of published posts
        if any(post.status == 'published' for post in self):
            raise ValidationError('Cannot delete published posts. Archive them first.')

        return super(ApiBlogPost, self).unlink()
