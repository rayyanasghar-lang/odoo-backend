from odoo import models, fields, api
import uuid


class ElectricalDetail(models.Model):
    _name = 'project.form.electrical.detail'
    _description = 'Electrical Detail'
    _table = 'electrical_details'

    uuid = fields.Char(string='ID', required=True, index=True, default=lambda self: str(uuid.uuid4()),null=False)
    project_id = fields.Char(string='Project', required=True, index=True)
    main_panel_size = fields.Char()
    bus_rating = fields.Char()
    main_breaker = fields.Char()
    pv_breaker_location = fields.Selection([
        ('TOP', 'Top'),
        ('BOTTOM', 'Bottom'),
        ('CENTER', 'Center'),
        ('OPPOSITE', 'Opposite'),
        ('UNKNOWN', 'Unknown')
    ], string='PV Breaker Location')
    one_line_diagram = fields.Text(string='One Line Diagram (JSON array)')

    _sql_constraints = [
        ('project_unique', 'unique(project_id)', 'Project must be unique')
    ]
    

