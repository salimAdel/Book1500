# -*- coding: utf-8 -*-
from datetime import date
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

    # ✅ Get all books (with pagination, sorting, and filtering)
    @http.route('/api/library/book', type='http', auth='public', methods=['GET'], csrf=False)
    def get_books(self, **kwargs):
        try:
            Book = request.env['library.book'].sudo()

            # 👇 Pagination
            page = int(kwargs.get('page', 1))
            limit = int(kwargs.get('limit', 10))
            if page < 1:
                page = 1
            if limit < 1:
                limit = 10
            offset = (page - 1) * limit

            # 👇 Filtering
            name_filter = kwargs.get('name', '').strip()
            category_id = kwargs.get('category_id')

            domain = []
            if name_filter:
                domain += ['|', '|',
                        ('name_ar', 'ilike', name_filter),
                        ('name_en', 'ilike', name_filter),
                        ('name_ind', 'ilike', name_filter)]
            if category_id:
                domain.append(('category_id', '=', int(category_id)))

            sort_by = kwargs.get('sort_by', 'id')      # مثال: name_en, name_ar, id
            order = kwargs.get('order', 'asc')         # asc أو desc
            if order not in ['asc', 'desc']:
                order = 'asc'
            order_by = f"{sort_by} {order}"

            total_books = Book.search_count(domain)
            books = Book.search(domain, limit=limit, offset=offset, order=order_by)

            data = []
            for book in books:
                data.append({
                    'id': book.id,
                    'name_ar': safe_val(book.name_ar),
                    'name_en': safe_val(book.name_en),
                    'name_ind': safe_val(book.name_ind),
                    'category_id': book.category_id.id if book.category_id else None,
                    'category_name': book.category_id.name_en if book.category_id else '',
                    'image': _get_attachment(book.id, 'image') if book.image else None,
                    'book_views_count': book.book_views_count,
                    })

            total_pages = (total_books + limit - 1) // limit

            response_data = {
                'status': 200,
                'page': page,
                'limit': limit,
                'total_books': total_books,
                'total_pages': total_pages,
                'sort_by': sort_by,
                'order': order,
                'filters': {
                    'name': name_filter,
                    'category_id': category_id
                },
                'data': data
            }

            return http.Response(
                json.dumps(response_data, ensure_ascii=False),
                content_type='application/json'
            )

        except Exception as e:
            return http.Response(
                json.dumps({'status': 500, 'error': str(e)}, ensure_ascii=False),
                content_type='application/json'
            )


    # ✅ Get single book by ID
    @http.route('/api/library/book/<int:id>', type='http', auth='user', methods=['GET'], csrf=False)
    def get_book(self, id, **kwargs):
        user = request.env.user

        today = date.today()
        if not (user.is_admin or (user.subscription_end_date and user.subscription_end_date > today)):
            return http.Response(
                json.dumps({'status': 403, 'error': 'Access denied. Active subscription or Admin access required.'}),
                content_type='application/json'
            )
        book = request.env['library.book'].sudo().browse(id)
        if not book.exists():
            return http.Response(
                json.dumps({'status': 404, 'error': 'Book not found'}),
                content_type='application/json'
            )
        book.env['book.views'].sudo().create({
            'user_id': user.id,
            'book_id': book.id,
        })
        image = book.image.decode('utf-8') if book.image else None
        file_ar = book.file_ar.decode('utf-8') if book.file_ar else None
        file_en = book.file_en.decode('utf-8') if book.file_en else None
        file_ind = book.file_ind.decode('utf-8') if book.file_ind else None

        data = {
            'id': book.id,
            'name_ar': safe_val(book.name_ar),
            'name_en': safe_val(book.name_en),
            'name_ind': safe_val(book.name_ind),
            'category_id': book.category_id.id if book.category_id else None,
            'category_name': book.category_id.name_en if book.category_id else '',
            'image': image,
            'book_views_count': book.book_views_count,
            'file_ar': file_ar,
            'file_en': file_en,
            'file_ind': file_ind,
        }
        return http.Response(
            json.dumps({'status': 200, 'data': data}, ensure_ascii=False),
            content_type='application/json'
        )

    # ✅ Get single book by ID (Public - No Auth required)
    @http.route('/api/library/public/book/<int:id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_book_public(self, id, **kwargs):
        book = request.env['library.book'].sudo().browse(id)
        if not book.exists():
            return http.Response(
                json.dumps({'status': 404, 'error': 'Book not found'}),
                content_type='application/json'
            )
        
        # Log view if user is logged in
        if request.session.uid:
            book.env['book.views'].sudo().create({
                'user_id': request.session.uid,
                'book_id': book.id,
            })

        image = book.image.decode('utf-8') if book.image else None
        file_ar = book.file_ar.decode('utf-8') if book.file_ar else None
        file_en = book.file_en.decode('utf-8') if book.file_en else None
        file_ind = book.file_ind.decode('utf-8') if book.file_ind else None

        data = {
            'id': book.id,
            'name_ar': safe_val(book.name_ar),
            'name_en': safe_val(book.name_en),
            'name_ind': safe_val(book.name_ind),
            'category_id': book.category_id.id if book.category_id else None,
            'category_name': book.category_id.name_en if book.category_id else '',
            'image': image,
            'book_views_count': book.book_views_count,
            'file_ar': file_ar,
            'file_en': file_en,
            'file_ind': file_ind,
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

            for vals in [
                'name_ar', 'name_en', 'name_ind',
                'category_id',
                'image', 'file_ar', 'file_en', 'file_ind'
            ]:
                if vals in request.httprequest.files:
                    fileobj = request.httprequest.files[field]
                    vals[vals] = base64.b64encode(fileobj.read()).decode('utf-8')
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


    @http.route('/api/library/statistics', type='http', auth='user', methods=['GET'], csrf=False)
    def get_statistics(self, **kwargs):
        user = request.env.user
        if not user.is_admin:
            return http.Response(
                json.dumps({'status': 403, 'error': 'Admin access required.'}),
                content_type='application/json'
            )
        try:
            # 👇 Date Filtering
            start_date = kwargs.get('start_date')
            end_date = kwargs.get('end_date')
            
            domain = []
            if start_date:
                domain.append(('create_date', '>=', start_date))
            if end_date:
                domain.append(('create_date', '<=', end_date))

            # Counts
            total_books = request.env['library.book'].sudo().search_count(domain)
            total_users = request.env['res.users'].sudo().search_count(domain + [('is_admin', '=', False)])
            total_categories = request.env['library.category'].sudo().search_count([]) # Categories are usually static
            total_views = request.env['book.views'].sudo().search_count(domain)
            total_ads = request.env['library.advertisement'].sudo().search_count(domain)

            # Categories for Pie Chart
            categories = request.env['library.category'].sudo().search([])
            categories_data = []
            for cat in categories:
                # Apply the same date filters to the category book count
                cat_domain = domain + [('category_id', '=', cat.id)]
                book_count = request.env['library.book'].sudo().search_count(cat_domain)
                if book_count > 0:
                    percentage = (book_count / total_books * 100) if total_books > 0 else 0
                    categories_data.append({
                        'name': cat.name_ar or cat.name_en,
                        'count': book_count,
                        'percentage': round(percentage, 1)
                    })        

            data = {
                'total_books': total_books,
                'total_users': total_users,
                'total_categories': total_categories,
                'total_views': total_views,
                'total_ads': total_ads,
                'categories_distribution': categories_data,
            }

            return http.Response(
                json.dumps({'status': 200, 'data': data}, ensure_ascii=False),
                content_type='application/json'
            )
        except Exception as e:
            return http.Response(
                json.dumps({'status': 500, 'error': str(e)}, ensure_ascii=False),
                content_type='application/json'
            )
