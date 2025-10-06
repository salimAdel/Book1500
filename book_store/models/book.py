from odoo import fields, models

class Book(models.Model):
    _name = "library.book"
    _description = "Book"

    name = fields.Char(string='Book Name', required=True, translate=True)
    # author_id = fields.Many2one('library.auther', string="Autherf")
    author = fields.Char(string="Auther")
    number_of_pages = fields.Integer(string="Number of Pages")
    category_ids = fields.Many2many('library.category', string="Categories")
    description = fields.Text(string="Description", translate=True)
    file_ids = fields.One2many('library.book.file', 'book_id', string="Files")
