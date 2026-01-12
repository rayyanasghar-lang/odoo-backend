from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class ServiceController(http.Controller):
    @http.route('/api/services', type='http', auth='public', methods=['GET', 'OPTIONS'], csrf=False, cors='*')
    def get_services(self, **kwargs):
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
            services = request.env['project.form.service'].sudo().search([])
            data = []
            for service in services:
                data.append({
                    'id': service.uuid, # Return UUID as ID
                    'name': service.name,
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

    
    @http.route('/api/create-service', type='http', auth='public', methods=['POST', 'OPTIONS'], csrf=False, cors='*')
    def create_service(self, **kwargs):
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
            data = json.loads(request.httprequest.data.decode('utf-8'))
            _logger.info("Data: %s", data)
        except:
            data = request.params

        service = request.env['project.form.service'].sudo().create({
            'name': data.get('name'),
        })

        return request.make_response(
            json.dumps({'status': 'success', 'data': {'id': service.uuid, 'name': service.name}}),
            headers={
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            }
        )