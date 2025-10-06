# -*- coding: utf-8 -*-
from odoo import fields,models

class Category(models.Model):
    _name = 'library.category'
    _description = "Book Category"

    name = fields.Char(string='Name', required=True, translate=True)
    book_ids = fields.Many2many('library.book', string="Books")
