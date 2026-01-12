from odoo import models, fields, api
import uuid


class AdvancedElectricalDetail(models.Model):
    _name = 'project.form.advanced.electrical.detail'
    _description = 'Advanced Electrical Detail'
    _table = 'advanced_electrical_details'

    uuid = fields.Char(string='ID', required=True, index=True, default=lambda self: str(uuid.uuid4()),null=False)
    project_id = fields.Char(string='Project', required=True, index=True)
    meter_location = fields.Char()
    service_entrance_type = fields.Char()
    subpanel_details = fields.Char()

    _sql_constraints = [
        ('project_unique', 'unique(project_id)', 'Project must be unique')
    ]
    

