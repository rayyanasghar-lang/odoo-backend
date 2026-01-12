from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class EngineeringFirmController(http.Controller):

    @http.route('/api/engineering-firm/create', type='http', auth='public', methods=['POST', 'OPTIONS'], csrf=False, cors='*')
    def create_engineering_firm(self, **kwargs):
        if request.httprequest.method == 'OPTIONS':
            return request.make_response(
                json.dumps({'status': 'ok'}),
                headers={
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                }
            )
        try:
            if request.httprequest.content_type == 'application/json':
                data = json.loads(request.httprequest.data.decode('utf-8'))
            else:
                data = request.params
                
            name = data.get('name')
            url = data.get('url')

            if not name:
                return request.make_response(
                    json.dumps({'status': 'error', 'message': 'Name is required'}),
                    headers={'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    status=400
                )

            firm = request.env['project.form.engineering.firm'].sudo().create({
                'name': name,
                'url': url,
            })

            return request.make_response(
                json.dumps({
                    'status': 'success',
                    'data': {
                        'id': firm.id,
                        'name': firm.name,
                        'url': firm.url,
                    }
                }),
                headers={'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
            )
        except Exception as e:
            _logger.error(f"Error creating engineering firm: {str(e)}")
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers={'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                status=500
            )
