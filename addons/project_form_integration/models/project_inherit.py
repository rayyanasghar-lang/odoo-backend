from odoo import models, fields, api
import uuid


class Project(models.Model):
    _name = 'project.form.project'
    _description = 'Project'
    _table = 'projects'

    uuid = fields.Char(string='ID', required=True, index=True, default=lambda self: str(uuid.uuid4()),null=False)
    created_at = fields.Datetime(string='Created At', default=fields.Datetime.now, required=True)
    updated_at = fields.Datetime(string='Updated At', default=fields.Datetime.now, required=True)

    user_profile_id = fields.Char(string='User Profile ID', required=True)
    name = fields.Char(required=True)
    address = fields.Char(required=True)
    type = fields.Char(required=True)
    status = fields.Char(string='Status', default='New Job Creation')
    submission_type_id = fields.Char(string='Submission Type ID', required=True)
    general_notes = fields.Text()
    odoo_task_id = fields.Integer(string='Odoo Task ID', help='Reference to auto-created task in Odoo Project module')
    
    # Relationships
    # Note: Many2many with Char IDs might be tricky in Odoo, but we define it to try mapping
    service_ids = fields.Many2many('project.form.service', 'project_services', 'project_id', 'service_id', string='Services')
    contractor_id = fields.Many2one('project.form.contractor', string='Contractor')
    
    # Reverse relations (One2many works with Char field on other side)
    system_summary_id = fields.One2many('project.form.system.summary', 'project_id', string='System Summary')
    site_detail_id = fields.One2many('project.form.site.detail', 'project_id', string='Site Details')
    electrical_detail_id = fields.One2many('project.form.electrical.detail', 'project_id', string='Electrical Details')
    advanced_electrical_detail_id = fields.One2many('project.form.advanced.electrical.detail', 'project_id', string='Advanced Electrical Details')
    optional_extra_detail_id = fields.One2many('project.form.optional.extra.detail', 'project_id', string='Optional Extra Details')
    system_component_ids = fields.One2many('project.form.system.component', 'project_id', string='System Components')
    upload_ids = fields.One2many('project.form.upload', 'project_id', string='Uploads')

    @api.constrains('address', 'contractor_id')
    def _check_address_contractor(self):
        for audit in self:
            if audit.address and audit.contractor_id:
                # Check if another project exists with the same address but DIFFERENT contractor
                # OR if another project exists with the same address and NO contractor locally
                # But the request says: "if other project is created by a contractor with an address that is already here then donot allow it."
                # This implies checking against ALL projects, but we should be careful about the same contractor using the same address (maybe different unit?). 
                # Assuming "already here" means any EXISTING project 
                
                # Let's interpret strict uniqueness for address unless it's the SAME project
                domain = [
                    ('address', '=', audit.address),
                    ('id', '!=', audit.id)
                ]
                blocking_project = self.search(domain, limit=1)
                
                if blocking_project:
                    # If found, it's a duplicate address.
                     # The requirement specifically mentions contractor context:
                     # "if other project is created by a contractor with an address that is already here then donot allow it"
                     # So if I am a contractor and I try to use an address that is already in the system (by anyone), block it.
                     raise models.ValidationError("The address '%s' is already associated with another project." % audit.address)

