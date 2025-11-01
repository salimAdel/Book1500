# -*- coding: utf-8 -*-
from odoo import fields,models

class Favorite(models.Model):
    _name = 'favorite'

    user_id = fields.Many2one('res.users', string='User', required=True)
    book_id = fields.Many2one('library.book', string='Book', required=True)