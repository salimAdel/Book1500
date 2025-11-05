# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json


def _get_attachment(record_id, file_name):
    base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
    attachment_path = f"{base_url}/api/library/{record_id}/{file_name}"
    return attachment_path

def safe_val(val):
    return val if val not in [False, '', None] else None
class FavoriteController(http.Controller):
    @http.route('/api/library/favorite', type='http', auth='user', methods=['POST'], csrf=False)
    def create_favorite(self, **kwargs):
        try:
            raw = request.httprequest.data.decode()
            data = json.loads(raw) if raw else {}
        except Exception:
            return http.Response(
                json.dumps({'status': 400, 'error': 'Invalid JSON format'}),
                content_type='application/json'
            )

        user = request.env.user
        book_id = data.get('book_id')

        if not book_id:
            return http.Response(
                json.dumps({'status': 400, 'error': 'book_id is required'}),
                content_type='application/json'
            )

        favorite = request.env['favorite'].sudo().create({
            'user_id': user.id,
            'book_id': book_id,
        })

        return http.Response(
            json.dumps({'status': 201, 'message': 'Favorite created successfully'}),
            content_type='application/json'
        )
    # 📌 Get all favorites
    @http.route('/api/library/favorite', type='http', auth='user', methods=['GET'], csrf=False)
    def get_favorites(self, **kwargs):
        user = request.env.user
        favorites = request.env['favorite'].sudo().search([('user_id', '=', user.id)])
        
        data = [{
            'id': fav.id,
            'book_id': fav.book_id.id,
            'name_ar': safe_val(fav.book_id.name_ar),
            'name_en': safe_val(fav.book_id.name_en),
            'name_ind': safe_val(fav.book_id.name_ind),
            'author_ar': safe_val(fav.book_id.author_ar),
            'author_en': safe_val(fav.book_id.author_en),
            'author_ind': safe_val(fav.book_id.author_ind),
            'number_of_pages': safe_val(fav.book_id.number_of_pages),
            'category_id': fav.book_id.category_id.id if fav.book_id.category_id else None,
            'category_name': fav.book_id.category_id.name_en if fav.book_id.category_id else '',
            'description_ar': safe_val(fav.book_id.description_ar),
            'description_en': safe_val(fav.book_id.description_en),
            'description_ind': safe_val(fav.book_id.description_ind),
            'image': _get_attachment(fav.book_id.id, 'image') if fav.book_id.image else None,
            'book_views_count': fav.book_id.book_views_count,
        } for fav in favorites]

        return http.Response(
            json.dumps({'status': 200, 'data': data}),
            content_type='application/json'
        )

    # 📌 Get single favorite by ID
    @http.route('/api/library/favorite/<int:id>', type='http', auth='user', methods=['GET'], csrf=False)
    def get_favorite(self, id, **kwargs):
        user = request.env.user
        fav = request.env['favorite'].sudo().browse(id)
        if not fav.exists() or fav.user_id.id != user.id:
            return http.Response(
                json.dumps({'status': 404, 'error': 'Favorite not found'}),
                content_type='application/json'
            )

        data = {
            'id': fav.id,
            'book_id': fav.book_id.id,
            'name_ar': safe_val(fav.book_id.name_ar),
            'name_en': safe_val(fav.book_id.name_en),
            'name_ind': safe_val(fav.book_id.name_ind),
            'author_ar': safe_val(fav.book_id.author_ar),
            'author_en': safe_val(fav.book_id.author_en),
            'author_ind': safe_val(fav.book_id.author_ind),
            'number_of_pages': safe_val(fav.book_id.number_of_pages),
            'category_id': fav.book_id.category_id.id if fav.book_id.category_id else None,
            'category_name': fav.book_id.category_id.name_en if fav.book_id.category_id else '',
            'description_ar': safe_val(fav.book_id.description_ar),
            'description_en': safe_val(fav.book_id.description_en),
            'description_ind': safe_val(fav.book_id.description_ind),
            'image': _get_attachment(fav.book_id.id, 'image') if fav.book_id.image else None,
            'book_views_count': fav.book_id.book_views_count,
        }
        return http.Response(
            json.dumps({'status': 200, 'data': data}),
            content_type='application/json'
        )
    # 📌 Delete favorite by ID
    @http.route('/api/library/favorite/<int:id>', type='http', auth='user', methods=['DELETE'], csrf=False)
    def delete_favorite(self, id, **kwargs):
        user = request.env.user
        fav = request.env['favorite'].sudo().browse(id)

        if not fav.exists() or fav.user_id.id != user.id:
            return http.Response(
                json.dumps({'status': 404, 'error': 'Favorite not found'}),
                content_type='application/json'
            )

        fav.sudo().unlink()
        return http.Response(
            json.dumps({'status': 204}),
            content_type='application/json'
        )