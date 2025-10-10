from odoo import fields, models

class Book(models.Model):
    _name = "library.book"
    _description = "Book"

    name_ar = fields.Char(string='Book Name Arabic')
    name_en = fields.Char(string='Book Name Engilsh')
    name_ind = fields.Char(string='Book Name Indonesia')
    # author_id = fields.Many2one('library.auther', string="Autherf")
    author_ar = fields.Char(string="Auther Arabic")
    author_en = fields.Char(string="Auther English")
    author_ind = fields.Char(string="Auther Indonesia")
    number_of_pages = fields.Integer(string="Number of Pages")
    category_id = fields.Many2one('library.category', string="Category")
    description_ar = fields.Text(string="Description Arabic")
    description_en = fields.Text(string="Description English")
    description_ind = fields.Text(string="Description Indonesia")
    image = fields.Binary(string="Image")
    file_ar = fields.Binary(string="PDF Arabic")
    file_en = fields.Binary(string="PDF English")
    file_ind = fields.Binary(string="PDF Indonesia")
