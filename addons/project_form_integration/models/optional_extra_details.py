from odoo import models, fields, api
import uuid


class OptionalExtraDetail(models.Model):
    _name = 'project.form.optional.extra.detail'
    _description = 'Optional Extra Detail'
    _table = 'optional_extra_details'

    uuid = fields.Char(string='ID', required=True, index=True, default=lambda self: str(uuid.uuid4()),null=False)
    project_id = fields.Char(string='Project', required=True, index=True)
    miracle_watt_required = fields.Boolean(default=False)
    miracle_watt_notes = fields.Text()
    der_rlc_required = fields.Boolean(default=False)
    der_rlc_notes = fields.Text()
    setback_constraints = fields.Boolean(default=False)
    setback_notes = fields.Text()
    site_access_restrictions = fields.Boolean(default=False)
    site_access_notes = fields.Text()
    inspection_notes = fields.Boolean(default=False)
    inspection_notes_text = fields.Text()
    battery_sld_requested = fields.Boolean(default=False)
    battery_sld_notes = fields.Text()

    _sql_constraints = [
        ('project_unique', 'unique(project_id)', 'Project must be unique')
    ]
    

