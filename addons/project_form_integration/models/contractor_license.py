from odoo import models, fields

class ContractorLicense(models.Model):
    _name = 'project.form.contractor.license'
    _description = 'Contractor License'

    contractor_id = fields.Many2one('project.form.contractor', string='Contractor', required=True, ondelete='cascade')
    license_no = fields.Char(string='License Number', required=True)
    license_type = fields.Char(string='License Type')
    state = fields.Char(string='State')
