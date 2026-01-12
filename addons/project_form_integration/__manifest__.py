{
    'name': 'Project Form Integration',
    'version': '19.0.1.0.0',
    'summary': 'Project form data integration with Google Drive',
    'description': 'Extends project module to store form submissions from Next.js app',
    'category': 'Project',
    'author': 'techsaker',
    'website': 'github-url',
    'license': 'LGPL-3',
    'depends': ['base', 'project'],
    'data': [
        'security/ir.model.access.csv',
        'views/project_task_views.xml',
    ],



    'installable': True,
    'application': False,
    'auto_install': False,
}
