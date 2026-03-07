{
    'name': 'Drone Services Website Theme',
    'version': '18.0.1.0',
    'category': 'Website/Theme',
    'summary': 'Professional drone services website theme',
    'description': """
        Drone Services Website Theme
        =============================
        Professional website theme designed for drone service businesses:
        - Aerial photography showcase
        - Videography services presentation
        - 2D mapping and orthophoto services
        - Sky-inspired color scheme
        - Custom footer and branding
    """,
    'author': 'Professional Drone Services',
    'depends': ['website'],
    'data': [
        'views/website_templates.xml',
        'views/services_templates.xml',
        'views/portfolio_templates.xml',
        'views/contact_templates.xml',
        'views/header_templates.xml',
        'views/footer_templates.xml',
        'data/menu_data.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'ica_website_theme/static/src/scss/theme.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
