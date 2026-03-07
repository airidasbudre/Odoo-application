# -*- coding: utf-8 -*-
"""
User Profile Model - Training Example

This model demonstrates:
- One2one relationship (extending res.users)
- Binary fields (for images/files)
- JSON fields
- Email validation
- Complex data structures
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re
import json


class ApiUserProfile(models.Model):
    _name = 'api.user.profile'
    _description = 'Extended User Profile for API Training'
    _order = 'user_id'

    # Link to system user (one-to-one relationship)
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        ondelete='cascade',
        index=True
    )

    # Basic Profile Info
    display_name = fields.Char(
        related='user_id.name',
        string='Name',
        readonly=True
    )

    bio = fields.Text(
        string='Biography',
        help='Short bio about the user'
    )

    avatar = fields.Binary(
        string='Avatar',
        attachment=True,
        help='Profile picture'
    )

    avatar_url = fields.Char(
        string='Avatar URL',
        help='External URL for avatar if not using binary field'
    )

    # Contact Information
    phone = fields.Char(
        string='Phone Number',
        help='Contact phone number'
    )

    website = fields.Char(
        string='Website',
        help='Personal or professional website'
    )

    linkedin_url = fields.Char(
        string='LinkedIn Profile'
    )

    github_username = fields.Char(
        string='GitHub Username'
    )

    twitter_handle = fields.Char(
        string='Twitter Handle'
    )

    # Professional Info
    job_title = fields.Char(
        string='Job Title',
        help='Current job title or role'
    )

    company = fields.Char(
        string='Company',
        help='Current company'
    )

    years_of_experience = fields.Integer(
        string='Years of Experience',
        default=0
    )

    # Skills & Interests (stored as JSON for flexibility)
    skills = fields.Text(
        string='Skills',
        help='Comma-separated list of skills (e.g., "Python,JavaScript,SQL")'
    )

    interests = fields.Text(
        string='Interests',
        help='Comma-separated list of interests'
    )

    # Location
    city = fields.Char(
        string='City'
    )

    country = fields.Char(
        string='Country'
    )

    timezone = fields.Selection(
        [
            ('UTC-12', 'UTC-12:00'),
            ('UTC-11', 'UTC-11:00'),
            ('UTC-10', 'UTC-10:00'),
            ('UTC-9', 'UTC-09:00'),
            ('UTC-8', 'UTC-08:00'),
            ('UTC-7', 'UTC-07:00'),
            ('UTC-6', 'UTC-06:00'),
            ('UTC-5', 'UTC-05:00'),
            ('UTC-4', 'UTC-04:00'),
            ('UTC-3', 'UTC-03:00'),
            ('UTC-2', 'UTC-02:00'),
            ('UTC-1', 'UTC-01:00'),
            ('UTC', 'UTC±00:00'),
            ('UTC+1', 'UTC+01:00'),
            ('UTC+2', 'UTC+02:00'),
            ('UTC+3', 'UTC+03:00'),
            ('UTC+4', 'UTC+04:00'),
            ('UTC+5', 'UTC+05:00'),
            ('UTC+6', 'UTC+06:00'),
            ('UTC+7', 'UTC+07:00'),
            ('UTC+8', 'UTC+08:00'),
            ('UTC+9', 'UTC+09:00'),
            ('UTC+10', 'UTC+10:00'),
            ('UTC+11', 'UTC+11:00'),
            ('UTC+12', 'UTC+12:00'),
        ],
        string='Timezone',
        default='UTC'
    )

    # Preferences
    preferred_language = fields.Selection(
        [
            ('en', 'English'),
            ('es', 'Spanish'),
            ('fr', 'French'),
            ('de', 'German'),
            ('pt', 'Portuguese'),
            ('zh', 'Chinese'),
            ('ja', 'Japanese'),
        ],
        string='Preferred Language',
        default='en'
    )

    email_notifications = fields.Boolean(
        string='Email Notifications',
        default=True,
        help='Receive email notifications'
    )

    newsletter_subscription = fields.Boolean(
        string='Newsletter Subscription',
        default=False,
        help='Subscribe to newsletter'
    )

    # Statistics
    profile_views = fields.Integer(
        string='Profile Views',
        default=0,
        readonly=True
    )

    posts_count = fields.Integer(
        string='Blog Posts',
        compute='_compute_posts_count'
    )

    tasks_count = fields.Integer(
        string='Tasks',
        compute='_compute_tasks_count'
    )

    # Metadata
    last_login = fields.Datetime(
        string='Last Login',
        readonly=True
    )

    account_created = fields.Datetime(
        string='Account Created',
        default=fields.Datetime.now,
        readonly=True
    )

    is_verified = fields.Boolean(
        string='Verified Account',
        default=False,
        help='Account has been verified (email, etc.)'
    )

    is_active = fields.Boolean(
        string='Active',
        default=True,
        help='Is the profile active?'
    )

    # ========== Computed Methods ==========

    @api.depends('user_id')
    def _compute_posts_count(self):
        """Count blog posts by this user"""
        for record in self:
            record.posts_count = self.env['api.blog.post'].search_count([
                ('author_id', '=', record.user_id.id)
            ])

    @api.depends('user_id')
    def _compute_tasks_count(self):
        """Count tasks assigned to this user"""
        for record in self:
            record.tasks_count = self.env['api.task'].search_count([
                ('assigned_to', '=', record.user_id.id)
            ])

    # ========== Constraints ==========

    @api.constrains('user_id')
    def _check_unique_user(self):
        """Ensure one profile per user"""
        for record in self:
            if self.search_count([('user_id', '=', record.user_id.id)]) > 1:
                raise ValidationError('Each user can only have one profile')

    @api.constrains('phone')
    def _check_phone_format(self):
        """Basic phone number validation"""
        for record in self:
            if record.phone:
                # Remove common separators
                cleaned = re.sub(r'[\s\-\(\)]', '', record.phone)
                # Check if it's digits (and optionally starts with +)
                if not re.match(r'^\+?\d{7,15}$', cleaned):
                    raise ValidationError('Please enter a valid phone number')

    @api.constrains('website', 'linkedin_url')
    def _check_url_format(self):
        """Validate URL formats"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE
        )

        for record in self:
            if record.website and not url_pattern.match(record.website):
                raise ValidationError('Please enter a valid website URL (must start with http:// or https://)')
            if record.linkedin_url and not url_pattern.match(record.linkedin_url):
                raise ValidationError('Please enter a valid LinkedIn URL')

    @api.constrains('years_of_experience')
    def _check_experience(self):
        """Ensure reasonable years of experience"""
        for record in self:
            if record.years_of_experience < 0:
                raise ValidationError('Years of experience cannot be negative')
            if record.years_of_experience > 70:
                raise ValidationError('Years of experience seems unrealistic')

    # ========== Business Methods ==========

    def action_increment_views(self):
        """Increment profile view count"""
        for record in self:
            record.profile_views += 1
        return True

    def action_verify_account(self):
        """Mark account as verified"""
        self.write({'is_verified': True})
        return True

    def action_update_last_login(self):
        """Update last login timestamp"""
        self.write({'last_login': fields.Datetime.now()})
        return True

    def get_skills_list(self):
        """Parse skills string into list"""
        self.ensure_one()
        if self.skills:
            return [s.strip() for s in self.skills.split(',') if s.strip()]
        return []

    def get_interests_list(self):
        """Parse interests string into list"""
        self.ensure_one()
        if self.interests:
            return [i.strip() for i in self.interests.split(',') if i.strip()]
        return []

    def get_social_links(self):
        """Get all social media links"""
        self.ensure_one()
        links = {}
        if self.linkedin_url:
            links['linkedin'] = self.linkedin_url
        if self.github_username:
            links['github'] = f'https://github.com/{self.github_username}'
        if self.twitter_handle:
            handle = self.twitter_handle.lstrip('@')
            links['twitter'] = f'https://twitter.com/{handle}'
        if self.website:
            links['website'] = self.website
        return links

    # ========== CRUD Override Examples ==========

    @api.model
    def create(self, vals):
        """Override create to set defaults"""
        if 'account_created' not in vals:
            vals['account_created'] = fields.Datetime.now()

        return super(ApiUserProfile, self).create(vals)

    def write(self, vals):
        """Override write for additional logic"""
        # Strip @ from Twitter handle if provided
        if 'twitter_handle' in vals and vals['twitter_handle']:
            vals['twitter_handle'] = vals['twitter_handle'].lstrip('@')

        return super(ApiUserProfile, self).write(vals)
