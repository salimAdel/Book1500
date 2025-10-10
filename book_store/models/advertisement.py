# -*- coding: utf-8 -*-
from odoo import fields,models

class Advertisement(models.Model):
    _name = 'library.advertisement'
    _description = "Advertisement"

    name_ar = fields.Char(string='Advertisement Arbic')
    name_en = fields.Char(string='Advertisement English')
    name_ind = fields.Char(string='Advertisement Indonesia')
