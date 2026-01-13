from odoo import http
from odoo.http import request
import json
import logging
import jwt
import datetime
import time
from odoo.tools import config

_logger = logging.getLogger(__name__)

SECRET_KEY = config.get('jwt_secret')

class AuthController(http.Controller):

    def _generate_token(self, contractor_id):
        payload = {
            'user_id': contractor_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
            'iat': datetime.datetime.utcnow()
        }
        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

## http://localhost:8069/api/contractor/signup
    @http.route('/api/contractor/signup', type='http', auth='public', methods=['POST', 'OPTIONS'], csrf=False, cors='*')
    def contractor_signup(self, **kwargs):
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
            try:
                data = json.loads(request.httprequest.data.decode('utf-8'))
            except:
                data = request.params

            name = data.get('name')
            email = data.get('email')
            password = data.get('password')
            
            if not name or not email or not password:
                 return request.make_response(
                    json.dumps({'status': 'error', 'message': 'Missing required fields: name, email, password'}),
                    headers={'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    status=400
                )

            # Check if email already exists
            existing_contractor = request.env['project.form.contractor'].sudo().search([('email', '=', email)], limit=1)
            if existing_contractor:
                 return request.make_response(
                    json.dumps({'status': 'error', 'message': 'Email already registered'}),
                    headers={'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    status=409
                )

            contractor = request.env['project.form.contractor'].sudo().create({
                'name': name,
                'email': email,
                'password': password, # TODO: Hash password in production
                'company_name': data.get('company_name'),
                'address': data.get('address'),
                'phone': data.get('phone'),
                'logo_url': data.get('logo_url'),
            })

            # Handle Licenses
            licenses_data = data.get('licenses', [])
            if licenses_data:
                for lic in licenses_data:
                    request.env['project.form.contractor.license'].sudo().create({
                        'contractor_id': contractor.id,
                        'license_no': lic.get('license_no'),
                        'license_type': lic.get('license_type'),
                        'state': lic.get('state'),
                    })

            token = self._generate_token(contractor.id)

            return request.make_response(
                json.dumps({
                    'status': 'success',
                    'message': 'Contractor registered successfully',
                    'token': token,
                    'contractor': {
                        'id': contractor.id,
                        'name': contractor.name,
                        'email': contractor.email,
                    }
                }),
                headers={'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                status=201
            )

        except Exception as e:
            _logger.exception("Contractor signup failed")
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers={'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                status=500
            )
## http://localhost:8069/api/contractor/login
    @http.route('/api/contractor/login', type='http', auth='public', methods=['POST', 'OPTIONS'], csrf=False, cors='*')
    def contractor_login(self, **kwargs):
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
            try:
                data = json.loads(request.httprequest.data.decode('utf-8'))
            except:
                data = request.params
            
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                 return request.make_response(
                    json.dumps({'status': 'error', 'message': 'Email and password are required'}),
                    headers={'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    status=400
                )

            contractor = request.env['project.form.contractor'].sudo().search([
                ('email', '=', email),
                ('password', '=', password) 
            ], limit=1)

            if contractor:
                token = self._generate_token(contractor.id)
                return request.make_response(
                    json.dumps({
                        'status': 'success',
                        'message': 'Login successful',
                        'token': token,
                         'contractor': {
                            'id': contractor.id,
                            'name': contractor.name,
                            'email': contractor.email,
                            'company_name': contractor.company_name,
                            'logo_url': contractor.logo_url
                        }
                    }),
                    headers={'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
                )
            else:
                 return request.make_response(
                    json.dumps({'status': 'error', 'message': 'Invalid credentials'}),
                    headers={'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    status=401
                )
        except Exception as e:
            _logger.exception("Contractor login failed")
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers={'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                status=500
            )

## http://localhost:8069/api/contractor/signout
    @http.route('/api/contractor/signout', type='http', auth='public', methods=['POST', 'OPTIONS'], csrf=False, cors='*')
    def contractor_signout(self, **kwargs):
        if request.httprequest.method == 'OPTIONS':
             return request.make_response(
                json.dumps({'status': 'ok'}),
                headers={
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                }
            )
        
        # In a session-based auth, we would call request.session.logout() here.
        # Since we are currently stateless/custom, we just return success so frontend knows to clear state.
        
        return request.make_response(
            json.dumps({
                'status': 'success',
                'message': 'Signout successful'
            }),
            headers={'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
        )
