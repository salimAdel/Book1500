# -*- coding: utf-8 -*-
import json
import logging
from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessDenied
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class AuthenticationController(http.Controller):

    @http.route('/api/auth/login', type='json', auth='public', methods=['POST'], csrf=False, cors='*')
    def api_login(self, **kw):
        try:
            args = request.get_json_data()
            if 'login' in args and 'password' in args:
                login = args.get('login')
                user_record = request.env['res.users'].sudo().search(
                    [('login', '=', (login))])
                if user_record:
                    password = args.get('password')
                    credential = {'login': login, 'password': password, 'type': 'password'}
                    request.session.authenticate(
                        request.session.db, credential)
            else:
                return {'status': 400, 'error': 'the key login or password are not found in json body'}
            
        
        except AccessDenied as error:
            return {'message': _("Incorrect username or password"), 'error': sys.exc_info()}
        except:

            return {'message': _("unexpected error"), 'error': sys.exc_info()}
        return {'message': _("success login")}

    @http.route('/api/users/create', type='json', auth='user', methods=['POST'], csrf=False)
    def create_user(self, **kwargs):
        try:
            data = request.get_json_data()
            required_fields = ['name', 'login', 'password']
            for field in required_fields:
                if field not in data:
                    return {
                        'status': 400,
                        'error': f'Missing required field: {field}'
                    }

            new_user = request.env['res.users'].sudo().create({
                'name': data['name'],
                'login': data['login'],
                'password': data['password'],
            })

            return {
                'status': 201,
                'message': 'User created successfully',
                'data': {
                    'user_id': new_user.id,
                    'name': new_user.name,
                    'login': new_user.login,
                }
            }

        except ValidationError as e:
            return {
                'status': 400,
                'error': str(e)
            }
        except Exception as e:
            _logger.exception("Failed to create user")
            return {
                'status': 500,
                'error': str(e)
            }

    @http.route('/api/users/<int:user_id>', type='json', auth='user', methods=['GET'], csrf=False)
    def get_user(self, user_id, **kwargs):
        try:
            user = request.env['res.users'].sudo().browse(user_id)
            if not user.exists():
                return {
                    'status': 404,
                    'error': 'User not found'
                }

            return {
                'status': 200,
                'data': {
                    'user_id': user.id,
                    'name': user.name,
                    'login': user.login,
                    'email': user.email,
                    'active': user.active,
                }
            }

        except Exception as e:
            _logger.exception("Failed to fetch user")
            return {
                'status': 500,
                'error': str(e)
            }