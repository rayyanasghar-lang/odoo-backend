from odoo import models, fields

class ProjectTask(models.Model):
    _inherit = 'project.task'

    engineering_firm_id = fields.Many2one('project.form.engineering.firm', string='Engineering Firm')

    def write(self, vals):
        res = super(ProjectTask, self).write(vals)
        if 'stage_id' in vals:
            for task in self:
                # Find linked project.form.project using odoo_task_id
                # Note: odoo_task_id is an Integer field on project.form.project
                linked_projects = self.env['project.form.project'].sudo().search([('odoo_task_id', '=', task.id)])
                for project in linked_projects:
                    project.status = task.stage_id.name
        return res
