from odoo import fields, models

class Auther(models.Model):
    _name = "library.auther"

    name = fields.Char(string="Name")