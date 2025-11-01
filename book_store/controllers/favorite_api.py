# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json


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
            'user_id': fav.user_id.id,
            'book_id': fav.book_id.id,
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
            'user_id': fav.user_id.id,
            'book_id': fav.book_id.id,
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