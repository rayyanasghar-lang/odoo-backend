from odoo import models, fields, api
import uuid


class SiteDetail(models.Model):
    _name = 'project.form.site.detail'
    _description = 'Site Detail'
    _table = 'site_details'

    uuid = fields.Char(string='ID', required=True, index=True, default=lambda self: str(uuid.uuid4()),null=False)
    project_id = fields.Char(string='Project', required=True, index=True)
    roof_material = fields.Char()
    roof_pitch = fields.Char()
    number_of_arrays = fields.Integer()
    ground_mount_type = fields.Char()
    foundation_type = fields.Char()
    main_panel_size = fields.Char()
    utility_provider = fields.Char()
    jurisdiction = fields.Char()

    _sql_constraints = [
        ('project_unique', 'unique(project_id)', 'Project must be unique')
    ]
    

