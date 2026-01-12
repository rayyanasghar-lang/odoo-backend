from odoo import models, fields, api
import uuid


class UserProfile(models.Model):
    _name = 'project.form.user.profile'
    _description = 'User Profile'
    _table = 'user_profiles'
    
    uuid = fields.Char(string='ID', required=True, index=True, default=lambda self: str(uuid.uuid4()),null=False)
    created_at = fields.Datetime(string='Created At', default=fields.Datetime.now, required=True)
    updated_at = fields.Datetime(string='Updated At', default=fields.Datetime.now, required=True)
    
    company_name = fields.Char(required=True)
    contact_name = fields.Char(required=True)
    email = fields.Char(required=True)
    phone = fields.Char()
    
    project_ids = fields.One2many('project.form.project', 'user_profile_id', string='Projects')

    _sql_constraints = [
        ('email_unique', 'unique(email)', 'Email must be unique')
    ]
    

