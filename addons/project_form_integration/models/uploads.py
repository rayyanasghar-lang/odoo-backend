from odoo import models, fields, api
import uuid


class Upload(models.Model):
    _name = 'project.form.upload'
    _description = 'Upload'
    _table = 'uploads'

    uuid = fields.Char(string='ID', required=True, index=True, default=lambda self: str(uuid.uuid4()),null=False)
    project_id = fields.Char(string='Project', required=True, index=True)
    url = fields.Char(required=True)
    name = fields.Char(required=True)
    category = fields.Char()
    mime_type = fields.Char()
    size = fields.Integer()
    

