from odoo import models, fields, api
import uuid


class Service(models.Model):
    _name = 'project.form.service'
    _description = 'Service'
    _table = 'services'

    uuid = fields.Char(string='ID', required=True, index=True, default=lambda self: str(uuid.uuid4()),null=False)
    name = fields.Char(required=True)
    
    project_ids = fields.Many2many('project.form.project', 'project_services', 'service_id', 'project_id', string='Projects')

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Name must be unique')
    ]
    

