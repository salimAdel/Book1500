# -*- coding: utf-8 -*-
import json
import logging
from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessDenied
from odoo.exceptions import ValidationError


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
            return {'message': _("Incorrect username or password")}
        except:

            return {'message': _("unexpected error")}
        return {'message': _("success login"), 'user':{
            'name': user_record.name,
            'login': user_record.login,
            'email': user_record.email,
            'active': user_record.active,
            'country' : user_record.country_id.name if user_record.country_id else None,
            'city' : user_record.city if user_record.city else None,
            'language' : user_record.lang
        }}

    @http.route('/api/users/create', type='http', auth='user', methods=['POST'], csrf=False)
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

            user = request.env['res.users'].sudo().create({
                'name': data['name'],
                'login': data['login'],
                'password': data['password'],
                'country_id': data['country_id'] if 'country_id' in data else False,
                'city': data['city'] if 'city' in data else False,
                'language': data['language'] if 'language' in data else False,
            })

            return {
                'status': 201,
                'message': 'User created successfully',
                'data': {
                     'name': user.name,
                    'login': user.login,
                    'email': user.email,
                    'active': user.active,
                    'country' : user.country_id.name if user.country_id else None,
                    'city' : user.city,
                    'language' : user.lang
                }
            }

        except ValidationError as e:
            return {
                'status': 400,
                'error': str(e)
            }
        except Exception as e:
            return {
                'status': 500,
                'error': str(e)
            }

    @http.route('/api/user_info', type='http', auth='user', methods=['GET'], csrf=False)
    def get_user(self, **kwargs):
        user_id = request.session.uid
        try:
            user = request.env['res.users'].sudo().browse(user_id)
            if not user.exists():
                return http.Response(
                    json.dumps({
                        'status': 404,
                        'error': 'User not found'
                    }),
                    content_type='application/json'
                )

            return http.Response(
                json.dumps({
                'status': 200,
                'data': {
                    'name': user.name,
                    'login': user.login,
                    'email': user.email,
                    'active': user.active,
                    'country' : user.country_id.name if user.country_id else None,
                    'city' : user.city,
                    'language' : user.lang
                }
            }),
            content_type='application/json'
            )

        except Exception as e:
            return http.Response(
                json.dumps({
                    'status': 500,
                    'error': str(e)
                }),
                content_type='application/json'
            )

    @http.route('/api/language', type='http', auth='public', methods=['GET'], csrf=False)
    def get_languages(self, **kwargs):
        try:
            languages = request.env['res.lang'].sudo().search([('active', '=', True)])
            lang_list = []
            for lang in languages:
                lang_list.append({
                    'code': lang.code,
                    'name': lang.name,
                    'direction': lang.direction
                })
            return http.Response(
                json.dumps({'status': 200, 'data': lang_list}, ensure_ascii=False),
                content_type='application/json'
            )
        except Exception as e:
            return http.Response(
                json.dumps({
                    'status': 500,
                    'error': str(e)
                }),
                content_type='application/json'

            )

    @http.route('/api/country', type='http', auth='user', methods=['GET'], csrf=False, cors='*')
    def get_countries(self, **kwargs):
        try:
            countries = request.env['res.country'].sudo().search([])
            country_list = []
            for country in countries:
                country_list.append({
                    'id': country.id,
                    'name': country.name
                })
            return http.Response(
                json.dumps(
                    {
                        'status': 200,
                        'data': country_list
                    }
                ),
                content_type='application/json'
            )
        except Exception as e:
            return http.Response(
                json.dumps({
                    'status': 500,
                    'error': str(e)
                }),
                content_type='application/json'

            )