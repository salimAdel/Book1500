# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json


def safe_val(val):
    return val if val not in [False, '', None] else None

class LibraryCategoryAPI(http.Controller):

    # 📌 Get all categories
    @http.route('/api/library/category', type='http', auth='public', methods=['GET'], csrf=False)
    def get_categories(self, **kwargs):
        categories = request.env['library.category'].sudo().search([])
        data = [{
            'id': cat.id,
            'name_ar': safe_val(cat.name_ar),
            'name_en': safe_val(cat.name_en),
            'name_ind': safe_val(cat.name_ind),
        } for cat in categories]

        return http.Response(
            json.dumps({'status': 200, 'data': data}),
            content_type='application/json'
        )

    # 📌 Get single category by ID
    @http.route('/api/library/category/<int:id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_category(self, id, **kwargs):
        cat = request.env['library.category'].sudo().browse(id)
        if not cat.exists():
            return http.Response(
                json.dumps({'status': 404, 'error': 'Category not found'}),
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

    # 📌 Create new category
    @http.route('/api/library/category', type='http', auth='public', methods=['POST'], csrf=False)
    def create_category(self, **kwargs):
        try:
            raw = request.httprequest.data.decode()
            data = json.loads(raw) if raw else {}
        except Exception:
            return http.Response(
                json.dumps({'status': 400, 'error': 'Invalid JSON format'}),
                content_type='application/json'
            )

        cat = request.env['library.category'].sudo().create({
            'name_ar': data.get('name_ar'),
            'name_en': data.get('name_en'),
            'name_ind': data.get('name_ind'),
        })

        return http.Response(
            json.dumps({'status': 201, 'message': 'Category created', 'id': cat.id}),
            content_type='application/json'
        )

    # 📌 Update category
    @http.route('/api/library/category/<int:id>', type='http', auth='public', methods=['PUT'], csrf=False)
    def update_category(self, id, **kwargs):
        cat = request.env['library.category'].sudo().browse(id)
        if not cat.exists():
            return http.Response(
                json.dumps({'status': 404, 'error': 'Category not found'}),
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
            json.dumps({'status': 200, 'message': 'Category updated'}),
            content_type='application/json'
        )

    # 📌 Delete category
    @http.route('/api/library/category/<int:id>', type='http', auth='public', methods=['DELETE'], csrf=False)
    def delete_category(self, id, **kwargs):
        cat = request.env['library.category'].sudo().browse(id)
        if not cat.exists():
            return http.Response(
                json.dumps({'status': 404, 'error': 'Category not found'}),
                content_type='application/json'
            )

        cat.unlink()
        return http.Response(
            json.dumps({'status': 200, 'message': 'Category deleted'}),
            content_type='application/json'
        )
