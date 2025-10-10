# -*- coding: utf-8 -*-
from odoo import fields,models

class Category(models.Model):
    _name = 'library.category'
    _description = "Book Category"

    name_ar = fields.Char(string='Name Arbic')
    name_en = fields.Char(string='Name English')
    name_ind = fields.Char(string='Name Indonesia')
