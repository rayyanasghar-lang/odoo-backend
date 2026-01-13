from odoo import models, fields, api
import uuid


class SystemSummary(models.Model):
    _name = 'project.form.system.summary'
    _description = 'System Summary'
    _table = 'system_summaries'

    uuid = fields.Char(string='ID', required=True, index=True, default=lambda self: str(uuid.uuid4()),null=False)
    project_id = fields.Char(string='Project', required=True, index=True)
    system_size = fields.Float(string='System Size', digits=(10, 2))
    system_type = fields.Selection([
        ('roof_mount', 'Roof Mount'),
        ('ground_mount', 'Ground Mount'),
        ('car_pool', 'Car pool'),
        ('both', 'Both Roof and Ground')
    ], string='System Type')
    pv_modules = fields.Integer()
    inverters = fields.Integer()
    
    battery_info_id = fields.One2many('project.form.battery.info', 'system_summary_id', string='Battery Info')

    _sql_constraints = [
        ('project_unique', 'unique(project_id)', 'Project must be unique')
    ]
    

