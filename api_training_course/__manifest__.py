{
    'name': 'API Training Course - Backend Development',
    'version': '18.0.1.0.0',
    'category': 'Education/Training',
    'summary': 'Complete Backend API Development Training Course',
    'description': """
        API Training Course - Learn Backend Development with Odoo
        ==========================================================

        A comprehensive, hands-on training module that teaches you how to build
        professional REST APIs using Odoo as your backend framework.

        What You'll Learn:
        -----------------
        ✓ RESTful API Design Principles
        ✓ Database Models & ORM Operations (CRUD)
        ✓ API Controllers & Routing
        ✓ JSON Request/Response Handling
        ✓ Authentication & Authorization
        ✓ Error Handling & Validation
        ✓ Query Parameters & Filtering
        ✓ Pagination & Sorting
        ✓ File Uploads via API
        ✓ API Documentation Best Practices

        Real-World Examples:
        -------------------
        • Blog API - Complete CRUD operations
        • Task Manager API - Project management features
        • User Profile API - User management
        • File Upload API - Handle media files
        • Search & Filter API - Advanced querying

        This training covers 90% of what you need for backend development jobs:
        - Building APIs from scratch
        - Database design and relationships
        - Authentication and security
        - Production-ready code patterns
        - Testing API endpoints

        Perfect For:
        -----------
        • Developers learning backend development
        • Moving from Odoo to general backend roles
        • Understanding modern API architecture
        • Building portfolio projects
    """,
    'author': 'API Training Team',
    'website': 'https://github.com/yourusername/api-training',
    'depends': ['base', 'web', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/api_training_menu.xml',
        'data/demo_data.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
