# -*- coding: utf-8 -*-
import json
import logging
import base64
from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessDenied
from odoo.exceptions import ValidationError

def safe_val(val):
    return val if val not in [False, '', None] else None
def safe_date(val):
    return val.strftime('%Y-%m-%d') if val else None

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
            'id': user_record.id,
            'name': safe_val(user_record.name),
            'login': safe_val(user_record.login),
            'email': safe_val(user_record.email),
            'active': user_record.active,
            'country' : user_record.country_id.name if user_record.country_id else None,
            'city' : user_record.city if user_record.city else None,
            'language' : safe_val(user_record.lang),
            'subscription_start_date' : safe_date(user_record.subscription_start_date),
            'subscription_end_date' : safe_date(user_record.subscription_end_date),
            'subscription_type' : safe_val(user_record.subscription_type),
            'image_1920' : user_record.image_1920 if user_record.image_1920 else None
        }}

    @http.route('/api/users/create', type='http', auth='public', methods=['POST'], csrf=False)
    def create_user(self, **kwargs):
        try:
            # محاولة الحصول على البيانات من JSON أو من form-data
            if request.httprequest.mimetype == 'application/json':
                data = request.get_json_data()
            else:
                # في حالة form-data (مثل عند رفع صورة)
                data = dict(request.params)

            required_fields = ['name', 'login', 'password']
            for field in required_fields:
                if field not in data or not data[field]:
                    return request.make_json_response({
                        'status': 400,
                        'error': f'Missing required field: {field}'
                    })

            # معالجة الصورة إذا تم إرسالها
            image_data = False
            if 'image_1920' in request.httprequest.files:
                fileobj = request.httprequest.files['image_1920']
                image_data = base64.b64encode(fileobj.read()).decode('utf-8')
            elif 'image_1920' in data and data['image_1920']:
                # في حال تم إرسال الصورة على شكل base64 ضمن JSON
                image_data = data['image_1920']

            # إنشاء المستخدم
            user = request.env['res.users'].sudo().create({
                'name': data['name'],
                'login': data['login'],
                'password': data['password'],
                'country_id': int(data['country_id']) if data.get('country_id') else False,
                'city': data.get('city'),
                'lang': data.get('language'),
                'subscription_start_date': data.get('subscription_start_date'),
                'subscription_end_date': data.get('subscription_end_date'),
                'subscription_type': data.get('subscription_type'),
                'image_1920': image_data,
            })

            return request.make_json_response({
                'status': 201,
                'message': 'User created successfully',
                'data': {
                    'id': user.id,
                    'name': safe_val(user.name),
                    'login': safe_val(user.login),
                    'email': safe_val(user.email),
                    'active': user.active,
                    'country': user.country_id.name if user.country_id else None,
                    'city': safe_val(user.city),
                    'language': safe_val(user.lang),
                    'subscription_start_date' : safe_date(user.subscription_start_date),
                    'subscription_end_date' : safe_date(user.subscription_end_date),
                    'subscription_type' : safe_val(user.subscription_type),
                    'image_1920' : user.image_1920 if user.image_1920 else None
                }
            })

        except ValidationError as e:
            return request.make_json_response({
                'status': 400,
                'error': str(e)
            })
        except Exception as e:
            return request.make_json_response({
                'status': 500,
                'error': str(e)
            })

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
            image_base64 = user.image_1920.decode('utf-8') if user.image_1920 else None
            return http.Response(
                json.dumps({
                'status': 200,
                'data': {
                    'id': user.id,
                    'name': safe_val(user.name),
                    'login': safe_val(user.login),
                    'email': safe_val(user.email),
                    'active': user.active,
                    'country' : user.country_id.name if user.country_id else None,
                    'city' : safe_val(user.city),
                    'language' : safe_val(user.lang),
                    'subscription_start_date' : safe_date(user.subscription_start_date),
                    'subscription_end_date' : safe_date(user.subscription_end_date),
                    'subscription_type' : safe_val(user.subscription_type),
                    'image_1920' : image_base64
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

    @http.route('/api/country', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
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

    @http.route('/api/user/update', type='http', auth='user', methods=['POST'], csrf=False)
    def update_user(self, **kwargs):
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
            try:
                raw = request.httprequest.data.decode()
                data = json.loads(raw) if raw else {}
            except Exception:
                return http.Response(
                    json.dumps({'status': 400, 'error': 'Invalid JSON format'}),
                    content_type='application/json'
                )

            # Update user fields
            user.name = data.get('name', user.name)
            user.email = data.get('email', user.email)
            user.country_id = data.get('country_id', user.country_id)
            user.city = data.get('city', user.city)
            user.lang = data.get('language', user.lang)
            user.subscription_start_date = data.get('subscription_start_date', user.subscription_start_date)
            user.subscription_end_date = data.get('subscription_end_date', user.subscription_end_date)
            user.subscription_type = data.get('subscription_type', user.subscription_type)
            user.image_1920 = data.get('image_1920', user.image_1920)

            image_base64 = user.image_1920.decode('utf-8') if user.image_1920 else None

            return http.Response(
                json.dumps({
                    'status': 200,
                    'data': {
                        'id': user.id,
                        'name': safe_val(user.name),
                        'login': safe_val(user.login),
                        'email': safe_val(user.email),
                        'active': user.active,
                        'country': user.country_id.name if user.country_id else None,
                        'city': safe_val(user.city),
                        'language': safe_val(user.lang),
                        'subscription_start_date' : safe_date(user.subscription_start_date),
                        'subscription_end_date' : safe_date(user.subscription_end_date),
                        'subscription_type' : safe_val(user.subscription_type),
                        'image_1920': image_base64
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

    @http.route('/api/user/reset_password', type='http', auth='user', methods=['POST'], csrf=False)
    def reset_password(self, **kwargs):
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
            try:
                raw = request.httprequest.data.decode()
                data = json.loads(raw) if raw else {}
            except Exception:
                return http.Response(
                    json.dumps({'status': 400, 'error': 'Invalid JSON format'}),
                    content_type='application/json'
                )

            new_password = data.get('new_password')
            if not new_password:
                return http.Response(
                    json.dumps({
                        'status': 400,
                        'error': 'New password is required'
                    }),
                    content_type='application/json'
                )

            user.password = new_password
            return http.Response(
                json.dumps({
                    'status': 200,
                    'message': 'Password reset successfully'
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


    @http.route('/api/user/update_language', type='http', auth='user', methods=['POST'], csrf=False)
    def update_language(self, **kwargs):
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
            try:
                raw = request.httprequest.data.decode()
                data = json.loads(raw) if raw else {}
            except Exception:
                return http.Response(
                    json.dumps({'status': 400, 'error': 'Invalid JSON format'}),
                    content_type='application/json'
                )

            new_language = data.get('language')
            if not new_language:
                return http.Response(
                    json.dumps({
                        'status': 400,
                        'error': 'Language code is required'
                    }),
                    content_type='application/json'
                )

            user.lang = new_language
            return http.Response(
                json.dumps({
                    'status': 200,
                    'message': 'Language updated successfully',
                    'data': {
                        'language': user.lang
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
