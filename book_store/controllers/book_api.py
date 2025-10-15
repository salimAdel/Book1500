# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
import base64

def _get_attachment(record_id, file_name):
    base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
    attachment_path = f"{base_url}/api/library/{record_id}/{file_name}"
    return attachment_path

def _get_attachment_binary_details(res_id, file_name):
    attachment_sudo = request.env['ir.attachment'].sudo().search([('res_model', '=', 'library.book'), ('res_id', '=', res_id), ('res_field', '=', file_name)], limit=1)
    if not attachment_sudo:
        return {
            'name': "",
            'type': "",
            'mimetype': "",
            'datas': ""
        }
    details = {
        'id': attachment_sudo.id,
        'name': attachment_sudo.name or '',
        'type': attachment_sudo.type or '',
        'mimetype': attachment_sudo.mimetype or '',
        'datas': f"data:{attachment_sudo.mimetype};base64,{attachment_sudo.datas.decode('utf-8')}" if attachment_sudo.datas else ""
    }
    return details

def safe_val(val):
    return val if val not in [False, '', None] else None
    
class LibraryBookAPI(http.Controller):

    @http.route('/api/library/<int:id>/<string:file_name>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_image (self, id, file_name, **kwargs):
        attachment = _get_attachment_binary_details(id, file_name)
        return http.Response(
            json.dumps(attachment, ensure_ascii=False),
            content_type='application/json'
        )

    # ✅ Get all books
    @http.route('/api/library/book', type='http', auth='public', methods=['GET'], csrf=False)
    def get_books(self, **kwargs):
        books = request.env['library.book'].sudo().search([])
        data = []
        for book in books:
            data.append({
                'id': book.id,
                'name_ar': safe_val(book.name_ar),
                'name_en': safe_val(book.name_en),
                'name_ind': safe_val(book.name_ind),
                'author_ar': safe_val(book.author_ar),
                'author_en': safe_val(book.author_en),
                'author_ind': safe_val(book.author_ind),
                'number_of_pages': safe_val(book.number_of_pages),
                'category_id': book.category_id.id if book.category_id else False,
                'category_name': book.category_id.name_en if book.category_id else '',
                'description_ar': safe_val(book.description_ar),
                'description_en': safe_val(book.description_en),
                'description_ind': safe_val(book.description_ind),
                'image': _get_attachment(book.id, 'image')if book.image else None,
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
            'name_ar': safe_val(book.name_ar),
            'name_en': safe_val(book.name_en),
            'name_ind': safe_val(book.name_ind),
            'author_ar': safe_val(book.author_ar),
            'author_en': safe_val(book.author_en),
            'author_ind': safe_val(book.author_ind),
            'number_of_pages': safe_val(book.number_of_pages),
            'category_id': book.category_id.id if book.category_id else None,
            'category_name': book.category_id.name_en if book.category_id else '',
            'description_ar': safe_val(book.description_ar),
            'description_en': safe_val(book.description_en),
            'description_ind': safe_val(book.description_ind),
            'image': _get_attachment(book.id, 'image')if book.image else None,
            'file_ar': _get_attachment(book.id, 'file_ar')if book.file_ar else None,
            'file_en': _get_attachment(book.id, 'file_en')if book.file_en else None,
            'file_ind': _get_attachment(book.id, 'file_ind')if book.file_ind else None,
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


