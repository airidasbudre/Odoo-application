{
    'name': 'Default Apps Page',
    'version': '18.0.1.0.0',
    'category': 'Technical',
    'summary': 'Show all apps on first page after login',
    'description': """
        This module changes the default home page to show all available apps
        instead of the standard dashboard.

        Features:
        - Redirects to Apps menu after login
        - Shows all installed apps
        - Clean and simple interface
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'web'],
    'data': [
        'views/res_users_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
