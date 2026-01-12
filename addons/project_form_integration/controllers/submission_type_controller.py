from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class SubmissionTypeController(http.Controller):

    @http.route('/api/submission-types', type='http', auth='public', methods=['GET', 'OPTIONS'], csrf=False, cors='*')
    def get_submission_types(self, **kwargs):
        if request.httprequest.method == 'OPTIONS':
            return request.make_response(
                json.dumps({'status': 'ok'}),
                headers={
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                }
            )

        try:
            submission_types = request.env['project.form.submission.type'].sudo().search([])
            data = []
            for st in submission_types:
                data.append({
                    'id': st.uuid, # Return UUID as ID
                    'name': st.name,
                })
            
            return request.make_response(
                json.dumps({'status': 'success', 'data': data}),
                headers={
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                }
            )
        except Exception as e:
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers={
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                status=500
            )
