# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json

def safe_val(val):
    return val if val not in [False, '', None] else None
class LibraryAdvertisementAPI(http.Controller):

    # 📌 Get all advertisements
    @http.route('/api/library/advertisement', type='http', auth='public', methods=['GET'], csrf=False)
    def get_advertisements(self, **kwargs):
        advertisements = request.env['library.advertisement'].sudo().search([])
        data = [{
            'id': c.id,
            'name_ar': safe_val(c.name_ar),
            'name_en': safe_val(c.name_en),
            'name_ind': safe_val(c.name_ind),
        } for c in advertisements]

        return http.Response(
            json.dumps({'status': 200, 'data': data}),
            content_type='application/json'
        )

    # 📌 Get single advertisement by ID
    @http.route('/api/library/advertisement/<int:id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_advertisement(self, id, **kwargs):
        cat = request.env['library.advertisement'].sudo().browse(id)
        if not cat.exists():
            return http.Response(
                json.dumps({'status': 404, 'error': 'Advertisement not found'}),
                content_type='application/json'
            )

        data = {
            'id': cat.id,
            'name_ar': safe_val(cat.name_ar),
            'name_en': safe_val(cat.name_en),
            'name_ind': safe_val(cat.name_ind),
        }
        return http.Response(
            json.dumps({'status': 200, 'data': data}),
            content_type='application/json'
        )

    # 📌 Create new advertisement
    @http.route('/api/library/advertisement', type='http', auth='public', methods=['POST'], csrf=False)
    def create_advertisement(self, **kwargs):
        try:
            raw = request.httprequest.data.decode()
            data = json.loads(raw) if raw else {}
        except Exception:
            return http.Response(
                json.dumps({'status': 400, 'error': 'Invalid JSON format'}),
                content_type='application/json'
            )


        cat = request.env['library.advertisement'].sudo().create({
            'name_ar': data.get('name_ar'),
            'name_en': data.get('name_en'),
            'name_ind': data.get('name_ind'),
        })

        return http.Response(
            json.dumps({'status': 201, 'message': 'Advertisement created', 'id': cat.id}),
            content_type='application/json'
        )

    # 📌 Update advertisement
    @http.route('/api/library/advertisement/<int:id>', type='http', auth='public', methods=['PUT'], csrf=False)
    def update_advertisement(self, id, **kwargs):
        cat = request.env['library.advertisement'].sudo().browse(id)
        if not cat.exists():
            return http.Response(
                json.dumps({'status': 404, 'error': 'Advertisement not found'}),
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

        cat.sudo().write({
            'name_ar': data.get('name_ar', cat.name_ar),
            'name_en': data.get('name_en', cat.name_en),
            'name_ind': data.get('name_ind', cat.name_ind),
        })

        return http.Response(
            json.dumps({'status': 200, 'message': 'Advertisement updated'}),
            content_type='application/json'
        )

    # 📌 Delete advertisement
    @http.route('/api/library/advertisement/<int:id>', type='http', auth='public', methods=['DELETE'], csrf=False)
    def delete_advertisement(self, id, **kwargs):
        cat = request.env['library.advertisement'].sudo().browse(id)
        if not cat.exists():
            return http.Response(
                json.dumps({'status': 404, 'error': 'Advertisement not found'}),
                content_type='application/json'
            )

        cat.unlink()
        return http.Response(
            json.dumps({'status': 200, 'message': 'Advertisement deleted'}),
            content_type='application/json'
        )
