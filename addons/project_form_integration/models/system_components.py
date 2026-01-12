from odoo import models, fields, api
import uuid


class SystemComponent(models.Model):
    _name = 'project.form.system.component'
    _description = 'System Component'
    _table = 'system_components'

    uuid = fields.Char(string='ID', required=True, index=True, default=lambda self: str(uuid.uuid4()),null=False)
    project_id = fields.Char(string='Project', required=True, index=True)
from odoo import models, fields, api
import uuid


class SystemComponent(models.Model):
    _name = 'project.form.system.component'
    _description = 'System Component'
    _table = 'system_components'

    uuid = fields.Char(string='ID', required=True, index=True, default=lambda self: str(uuid.uuid4()),null=False)
    project_id = fields.Char(string='Project', required=True, index=True)
    type = fields.Char(required=True)
    make_model = fields.Char(required=True)
    qty = fields.Integer(required=True)
    attachment = fields.Text(string='Attachment URLs (JSON array)')
    notes = fields.Text()
