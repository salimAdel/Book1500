# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, Response
import json

class BookStoreAPI(http.Controller):

    # ---------------------------------------------
    # CATEGORY CRUD
    # ---------------------------------------------
    @http.route('/api/categories', type='http', auth='public', methods=['GET'])
    def get_categories(self, **kwargs):
        categories = request.env['library.category'].sudo().search([])
        data = [{'id': c.id, 'name': c.name} for c in categories]
        return Response(json.dumps(data), content_type='application/json')

    @http.route('/api/categories', type='json', auth='public', methods=['POST'], csrf=False)
    def create_category(self):
        try:
            arg = request.httprequest.data.decode()
            val = json.loads(arg)
            request.env['library.category'].sudo().create(val)
            return{
                "massage":"the store created succssfully",
            }
        except Exception as e:
            return request.make_json_response({
                'message': "something went wrong",
                'error': str(e)
            }, status=400)
    

    @http.route('/api/categories/<int:id>',method = ["PUT"], type="json",auth="none",csrf=False)
    def edit_category(self,id):
        try:
            store = request.env['library.category'].sudo().browse(id)
            if not store.exists():
                return request.make_json_response({
                    'message': "record not found"
                }, status=404)
            
            arg = request.httprequest.data.decode()
            val = json.loads(arg)
            store.write(val)
            return{
                "massage":"the category Updated succssfully",
            }
        except Exception as e :
            return request.make_json_response({
                'message': "something went wrong",
                'error': str(e)
            }, status=400)

    @http.route('/api/categories/<int:id>', method = ["DELETE"], type="http",auth="none",csrf=False)
    def delete_category(self, id, **kwargs):
        try:
            category = request.env['library.category'].sudo().browse(id)
            if not category.exists():
                return request.make_json_response({
                    'message': "record not found"
                }, status=404)

            category.unlink()
            return request.make_json_response({
                "message": "The category was deleted successfully"
            }, status=200)

        except Exception as e:
            return request.make_json_response({
                'message': "something went wrong",
                'error': str(e)
            }, status=400)


    # ---------------------------------------------
    # BOOK CRUD
    # ---------------------------------------------
    @http.route('/api/books', type='http', auth='public', methods=['GET'])
    def get_books(self, **kwargs):
        books = request.env['library.book'].sudo().search([])
        data = []
        for book in books:
            data.append({
                'id': book.id,
                'name': book.name,
                'author': book.author,
                'number_of_pages': book.number_of_pages,
                'categories': [c.name for c in book.category_ids],
                'description': book.description,
            })
        return Response(json.dumps(data), content_type='application/json')

    @http.route('/api/books', type='json', auth='public', methods=['POST'])
    def create_book(self, **kwargs):
        vals = {
            'name': kwargs.get('name'),
            'author': kwargs.get('author'),
            'number_of_pages': kwargs.get('number_of_pages'),
            'description': kwargs.get('description'),
        }
        # ربط التصنيفات (IDs)
        cat_ids = kwargs.get('category_ids', [])
        if cat_ids:
            vals['category_ids'] = [(6, 0, cat_ids)]
        book = request.env['library.book'].sudo().create(vals)
        return {'id': book.id, 'name': book.name}

    @http.route('/api/books/<int:book_id>', type='json', auth='public', methods=['PUT'])
    def update_book(self, book_id, **kwargs):
        book = request.env['library.book'].sudo().browse(book_id)
        if not book.exists():
            return {'error': 'Book not found'}
        vals = {}
        for field in ['name', 'author', 'description', 'number_of_pages']:
            if kwargs.get(field):
                vals[field] = kwargs[field]
        if 'category_ids' in kwargs:
            vals['category_ids'] = [(6, 0, kwargs['category_ids'])]
        book.write(vals)
        return {'success': True}

    @http.route('/api/books/<int:book_id>', type='json', auth='public', methods=['DELETE'])
    def delete_book(self, book_id, **kwargs):
        book = request.env['library.book'].sudo().browse(book_id)
        if not book.exists():
            return {'error': 'Book not found'}
        book.unlink()
        return {'success': True}

    # ---------------------------------------------
    # BOOK FILES CRUD
    # ---------------------------------------------
    @http.route('/api/book_files', type='http', auth='public', methods=['GET'])
    def get_book_files(self, **kwargs):
        files = request.env['book.file'].sudo().search([])
        data = [{
            'id': f.id,
            'book': f.book_id.name,
            'lang': f.lang_id.code if f.lang_id else None,
            'filename': f.filename,
        } for f in files]
        return Response(json.dumps(data), content_type='application/json')
