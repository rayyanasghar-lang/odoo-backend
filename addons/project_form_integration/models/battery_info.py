from odoo import models, fields, api
import uuid


class BatteryInfo(models.Model):
    _name = 'project.form.battery.info'
    _description = 'Battery Info'
    _table = 'battery_infos'

    uuid = fields.Char(string='ID', required=True, index=True, default=lambda self: str(uuid.uuid4()),null=False)
    system_summary_id = fields.Char(string='System Summary', required=True, index=True)
    qty = fields.Integer(required=True)
    model = fields.Char()
    image = fields.Text(string='Image URLs (JSON array)')

    _sql_constraints = [
        ('system_summary_unique', 'unique(system_summary_id)', 'System Summary must be unique')
    ]
    

