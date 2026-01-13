from odoo import models, fields, api

class Contractor(models.Model):
    _name = 'project.form.contractor'
    _description = 'Contractor'

    name = fields.Char(string='Name', required=True)
    company_name = fields.Char(string='Company Name')
    email = fields.Char(string='Email', required=True)
    password = fields.Char(string='Password', required=True) # In production, this should be hashed
    address = fields.Char(string='Address')
    phone = fields.Char(string='Phone')
    logo_url = fields.Char(string='Logo URL')
    license_ids = fields.One2many('project.form.contractor.license', 'contractor_id', string='Licenses')

    _sql_constraints = [
        ('email_unique', 'unique(email)', 'The email address must be unique for each contractor.')
    ]
