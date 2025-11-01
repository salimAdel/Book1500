# -*- coding: utf-8 -*-
from odoo import fields,models

class BookViews(models.Model):
    _name = 'book.views'

    user_id = fields.Many2one('res.users', string='User')
    book_id = fields.Many2one('library.book', string='Book')
    view_date = fields.Datetime(string='View Date', default=fields.Datetime.now)