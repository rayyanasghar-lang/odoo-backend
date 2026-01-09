{
    'name': 'Blog API',
    'version': '19.0.1.0.0',
    'summary': 'Simple blog application with posts and categories',
    'description': """
Blog API Module
===============

A comprehensive blog module for Odoo with the following features:

Features
--------
* Create and manage blog posts
* Organize posts with categories
* Website integration for public blog display
* RESTful API endpoints for blog management
* Clean and responsive blog templates
* Author management and post metadata

This module provides a complete blogging solution integrated with Odoo's website builder.
    """,
    'category': 'Website/Website',
    'author': 'Your Name',
    'website': 'https://github.com/yourusername/blog_api',
    'license': 'LGPL-3',
    'depends': ['base', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'views/blog_views.xml',
        'views/website_blog_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'blog_api/static/src/css/blog.css',
            'blog_api/static/src/js/blog.js',
        ],
    },
    'images': [
        'static/description/icon.png',
        'static/description/banner.png',
        'static/description/screenshot_01.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 0.00,
    'currency': 'USD',
}
