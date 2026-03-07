# -*- coding: utf-8 -*-
"""
User Profile API Controller - Training Example

This controller demonstrates:
- User profile management
- File uploads (avatar)
- Profile validation
- User-specific endpoints
- Statistics and metrics

API Endpoints:
GET    /api/training/users/profile              - Get current user profile
PUT    /api/training/users/profile              - Update current user profile
GET    /api/training/users/<int:id>/profile     - Get user profile by ID (public)
POST   /api/training/users/profile/avatar       - Upload avatar image
GET    /api/training/users/search               - Search users
"""

import json
import base64
import logging
from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


class UserApiController(http.Controller):

    # ========== Helper Methods ==========

    def _get_profile(self, user_id):
        """Helper to get user profile or create if doesn't exist"""
        Profile = request.env['api.user.profile'].sudo()
        profile = Profile.search([('user_id', '=', user_id)], limit=1)

        # Auto-create profile if doesn't exist
        if not profile:
            profile = Profile.create({'user_id': user_id})

        return profile

    def _serialize_profile(self, profile, include_private=False):
        """Convert profile record to dictionary"""
        data = {
            'id': profile.id,
            'user_id': profile.user_id.id,
            'display_name': profile.display_name,
            'bio': profile.bio,
            'avatar_url': profile.avatar_url,
            'job_title': profile.job_title,
            'company': profile.company,
            'years_of_experience': profile.years_of_experience,
            'skills': profile.get_skills_list(),
            'interests': profile.get_interests_list(),
            'city': profile.city,
            'country': profile.country,
            'social_links': profile.get_social_links(),
            'profile_views': profile.profile_views,
            'posts_count': profile.posts_count,
            'tasks_count': profile.tasks_count,
            'is_verified': profile.is_verified,
            'account_created': profile.account_created.isoformat() if profile.account_created else None,
        }

        # Include private info only for own profile
        if include_private:
            data.update({
                'phone': profile.phone,
                'website': profile.website,
                'timezone': profile.timezone,
                'preferred_language': profile.preferred_language,
                'email_notifications': profile.email_notifications,
                'newsletter_subscription': profile.newsletter_subscription,
                'last_login': profile.last_login.isoformat() if profile.last_login else None,
            })

        return data

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

    # ========== Profile Endpoints ==========

    @http.route('/api/training/users/profile', type='http', auth='user', methods=['GET'], csrf=False)
    def get_my_profile(self):
        """
        Get current user's profile (includes private info)

        Example: GET /api/training/users/profile
        """
        try:
            profile = self._get_profile(request.env.user.id)

            # Update last login
            profile.action_update_last_login()

            return self._success_response({
                'profile': self._serialize_profile(profile, include_private=True)
            })

        except Exception as e:
            _logger.error(f'Error fetching user profile: {str(e)}')
            return self._error_response('Internal server error', status=500)

    @http.route('/api/training/users/profile', type='json', auth='user', methods=['PUT'], csrf=False)
    def update_my_profile(self, **params):
        """
        Update current user's profile

        Request Body (JSON):
        {
            "bio": "Software developer",
            "job_title": "Senior Developer",
            "company": "Tech Corp",
            "years_of_experience": 5,
            "skills": "Python,JavaScript,SQL",
            "interests": "AI,Web Development",
            "city": "San Francisco",
            "country": "USA",
            "phone": "+1234567890",
            "website": "https://example.com",
            "linkedin_url": "https://linkedin.com/in/username",
            "github_username": "username",
            "twitter_handle": "@username",
            "timezone": "UTC-8",
            "preferred_language": "en",
            "email_notifications": true,
            "newsletter_subscription": false
        }

        All fields are optional - only send what you want to update
        """
        try:
            profile = self._get_profile(request.env.user.id)

            # List of updateable fields
            updateable_fields = [
                'bio', 'avatar_url', 'phone', 'website', 'linkedin_url',
                'github_username', 'twitter_handle', 'job_title', 'company',
                'years_of_experience', 'skills', 'interests', 'city', 'country',
                'timezone', 'preferred_language', 'email_notifications',
                'newsletter_subscription'
            ]

            # Prepare update values
            vals = {}
            for field in updateable_fields:
                if field in params:
                    vals[field] = params[field]

            if vals:
                profile.write(vals)

            return {
                'success': True,
                'data': {
                    'profile': self._serialize_profile(profile, include_private=True),
                    'message': 'Profile updated successfully'
                }
            }

        except Exception as e:
            _logger.error(f'Error updating profile: {str(e)}')
            return {'success': False, 'error': str(e)}

    @http.route('/api/training/users/<int:user_id>/profile', type='http', auth='public', methods=['GET'], csrf=False)
    def get_user_profile(self, user_id):
        """
        Get user profile by ID (public info only)

        Example: GET /api/training/users/5/profile
        """
        try:
            # Check if user exists
            user = request.env['res.users'].sudo().browse(user_id)
            if not user.exists():
                return self._error_response('User not found', status=404)

            profile = self._get_profile(user_id)

            # Increment view count
            profile.action_increment_views()

            return self._success_response({
                'profile': self._serialize_profile(profile, include_private=False)
            })

        except Exception as e:
            _logger.error(f'Error fetching profile for user {user_id}: {str(e)}')
            return self._error_response('Internal server error', status=500)

    @http.route('/api/training/users/profile/avatar', type='http', auth='user', methods=['POST'], csrf=False)
    def upload_avatar(self, **params):
        """
        Upload avatar image

        Form Data:
        - avatar: File upload (image file)

        Example: POST /api/training/users/profile/avatar
        Content-Type: multipart/form-data
        """
        try:
            # Get uploaded file
            avatar_file = params.get('avatar')

            if not avatar_file:
                return self._error_response('No file uploaded', status=400)

            # Validate file type (basic check)
            filename = avatar_file.filename if hasattr(avatar_file, 'filename') else ''
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']

            if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
                return self._error_response(
                    'Invalid file type. Allowed: JPG, PNG, GIF',
                    status=400
                )

            # Read file and encode to base64
            file_content = avatar_file.read()

            # Check file size (max 2MB)
            max_size = 2 * 1024 * 1024  # 2MB in bytes
            if len(file_content) > max_size:
                return self._error_response('File too large. Maximum size: 2MB', status=400)

            avatar_base64 = base64.b64encode(file_content)

            # Update profile
            profile = self._get_profile(request.env.user.id)
            profile.write({'avatar': avatar_base64})

            return self._success_response({
                'message': 'Avatar uploaded successfully',
                'profile': self._serialize_profile(profile, include_private=True)
            })

        except Exception as e:
            _logger.error(f'Error uploading avatar: {str(e)}')
            return self._error_response('Internal server error', status=500)

    @http.route('/api/training/users/search', type='http', auth='public', methods=['GET'], csrf=False)
    def search_users(self, **params):
        """
        Search users by name or job title

        Query Parameters:
        - q: Search query (searches in name and job title)
        - limit: Maximum results (default: 10)

        Example: GET /api/training/users/search?q=developer&limit=5
        """
        try:
            query = params.get('q', '')
            limit = min(int(params.get('limit', 10)), 50)

            if not query:
                return self._error_response('Search query (q) is required', status=400)

            # Search in user name and profile job title
            Profile = request.env['api.user.profile'].sudo()

            profiles = Profile.search([
                '|', '|',
                ('display_name', 'ilike', query),
                ('job_title', 'ilike', query),
                ('company', 'ilike', query),
            ], limit=limit)

            profiles_data = [
                self._serialize_profile(profile, include_private=False)
                for profile in profiles
            ]

            return self._success_response({
                'profiles': profiles_data,
                'count': len(profiles_data),
                'query': query
            })

        except Exception as e:
            _logger.error(f'Error searching users: {str(e)}')
            return self._error_response('Internal server error', status=500)

    @http.route('/api/training/users/leaderboard', type='http', auth='public', methods=['GET'], csrf=False)
    def get_leaderboard(self, **params):
        """
        Get user leaderboard by blog posts count

        Query Parameters:
        - limit: Maximum results (default: 10)

        Example: GET /api/training/users/leaderboard?limit=10
        """
        try:
            limit = min(int(params.get('limit', 10)), 50)

            Profile = request.env['api.user.profile'].sudo()

            # Get profiles ordered by posts count
            profiles = Profile.search([], order='posts_count desc', limit=limit)

            leaderboard = []
            for idx, profile in enumerate(profiles, 1):
                leaderboard.append({
                    'rank': idx,
                    'user_id': profile.user_id.id,
                    'display_name': profile.display_name,
                    'job_title': profile.job_title,
                    'posts_count': profile.posts_count,
                    'profile_views': profile.profile_views,
                    'is_verified': profile.is_verified,
                })

            return self._success_response({
                'leaderboard': leaderboard,
                'count': len(leaderboard)
            })

        except Exception as e:
            _logger.error(f'Error fetching leaderboard: {str(e)}')
            return self._error_response('Internal server error', status=500)
