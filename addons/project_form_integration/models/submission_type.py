from odoo import models, fields, api
import uuid


class SubmissionType(models.Model):
    _name = 'project.form.submission.type'
    _description = 'Submission Type'
    _table = 'submission_types'

    uuid = fields.Char(string='ID', required=True, index=True, default=lambda self: str(uuid.uuid4()),null=False)
    name = fields.Char(required=True)
    
    project_ids = fields.One2many('project.form.project', 'submission_type_id', string='Projects')

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Name must be unique')
    ]
