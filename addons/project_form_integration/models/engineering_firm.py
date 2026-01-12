from odoo import models, fields
import uuid

class EngineeringFirm(models.Model):
    _name = 'project.form.engineering.firm'
    _description = 'Engineering Firm'

    uuid = fields.Char(string='ID', required=True, index=True, default=lambda self: str(uuid.uuid4()))
    name = fields.Char(string='Name', required=True)
    url = fields.Char(string='URL')
