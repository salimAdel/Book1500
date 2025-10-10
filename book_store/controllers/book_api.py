# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
import base64

class LibraryBookAPI(http.Controller):

    # ✅ Get all books
    @http.route('/api/library/book', type='http', auth='public', methods=['GET'], csrf=False)
    def get_books(self, **kwargs):
        books = request.env['library.book'].sudo().search([])
        data = []
        for book in books:
            data.append({
                'id': book.id,
                'name_ar': book.name_ar,
                'name_en': book.name_en,
                'name_ind': book.name_ind,
                'author_ar': book.author_ar,
                'author_en': book.author_en,
                'author_ind': book.author_ind,
                'number_of_pages': book.number_of_pages,
                'category_id': book.category_id.id if book.category_id else False,
                'category_name': book.category_id.name_en if book.category_id else '',
                'description_ar': book.description_ar,
                'description_en': book.description_en,
                'description_ind': book.description_ind,
            })
        return http.Response(
            json.dumps({'status': 200, 'data': data}, ensure_ascii=False),
            content_type='application/json'
        )

    # ✅ Get single book by ID
    @http.route('/api/library/book/<int:id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_book(self, id, **kwargs):
        book = request.env['library.book'].sudo().browse(id)
        if not book.exists():
            return http.Response(
                json.dumps({'status': 404, 'error': 'Book not found'}),
                content_type='application/json'
            )
        data = {
            'id': book.id,
            'name_ar': book.name_ar,
            'name_en': book.name_en,
            'name_ind': book.name_ind,
            'author_ar': book.author_ar,
            'author_en': book.author_en,
            'author_ind': book.author_ind,
            'number_of_pages': book.number_of_pages,
            'category_id': book.category_id.id if book.category_id else False,
            'category_name': book.category_id.name_en if book.category_id else '',
            'description_ar': book.description_ar,
            'description_en': book.description_en,
            'description_ind': book.description_ind,
        }
        return http.Response(
            json.dumps({'status': 200, 'data': data}, ensure_ascii=False),
            content_type='application/json'
        )

    # ✅ Create new book
    @http.route('/api/library/book', type='http', auth='public', methods=['POST'], csrf=False)
    def create_book(self, **kwargs):
        try:
            raw = request.httprequest.data.decode()
            vals = json.loads(raw) if raw else {}

            # التعامل مع الحقول الثنائية (Base64)
            for field in ['image', 'file_ar', 'file_en', 'file_ind']:
                    if field in request.httprequest.files:
                        fileobj = request.httprequest.files[field]
                        vals[field] = base64.b64encode(fileobj.read()).decode('utf-8')

            book = request.env['library.book'].sudo().create(vals)
            return http.Response(
                json.dumps({'status': 201, 'message': 'Book created', 'id': book.id}),
                content_type='application/json'
            )
        except Exception as e:
            return http.Response(
                json.dumps({'status': 500, 'error': str(e)}),
                content_type='application/json'
            )

    # ✅ Update book
    @http.route('/api/library/book/<int:id>', type='http', auth='public', methods=['PUT'], csrf=False)
    def update_book(self, id, **kwargs):
        try:
            raw_data = request.httprequest.data.decode()
            vals = json.loads(raw_data)
            book = request.env['library.book'].sudo().browse(id)
            if not book.exists():
                return http.Response(
                    json.dumps({'status': 404, 'error': 'Book not found'}),
                    content_type='application/json'
                )

            for field in [
                'name_ar', 'name_en', 'name_ind',
                'author_ar', 'author_en', 'author_ind',
                'number_of_pages', 'category_id',
                'description_ar', 'description_en', 'description_ind',
                'image', 'file_ar', 'file_en', 'file_ind'
            ]:
                if field in request.httprequest.files:
                    fileobj = request.httprequest.files[field]
                    vals[field] = base64.b64encode(fileobj.read()).decode('utf-8')
            return http.Response(
                json.dumps({'status': 200, 'message': 'Book updated'}),
                content_type='application/json'
            )
        except Exception as e:
            return http.Response(
                json.dumps({'status': 500, 'error': str(e)}),
                content_type='application/json'
            )

    # ✅ Delete book
    @http.route('/api/library/book/<int:id>', type='http', auth='public', methods=['DELETE'], csrf=False)
    def delete_book(self, id, **kwargs):
        book = request.env['library.book'].sudo().browse(id)
        if not book.exists():
            return http.Response(
                json.dumps({'status': 404, 'error': 'Book not found'}),
                content_type='application/json'
            )
        book.unlink()
        return http.Response(
            json.dumps({'status': 200, 'message': 'Book deleted'}),
            content_type='application/json'
        )
    
    @http.route('/api/library/book/<int:id>/file/<string:field>', type='http', auth='public', methods=['GET'], csrf=False)
    def download_file(self, id, field, **kwargs):
        book = request.env['library.book'].sudo().browse(id)
        if not book.exists() or field not in ['image','file_ar','file_en','file_ind']:
            return request.not_found()

        file_data = getattr(book, field)
        if not file_data:
            return request.not_found()

        return request.make_response(
            file_data,
            headers=[
                ('Content-Type', 'application/octet-stream'),
                ('Content-Disposition', f'attachment; filename={field}_{id}.bin')
            ]
        )


