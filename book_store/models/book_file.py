from odoo import fields, models, _,api
from odoo.exceptions import ValidationError

class BookFile(models.Model):
    _name = "library.book.file"
    _description = "Book File"

    book_id = fields.Many2one('library.book', string="Book", required=True, ondelete='cascade')
    lang_id = fields.Many2one(
        'res.lang',
        string="Language",
        required=True,
        domain=[('active', '=', True)],
        help="Select from active system languages"
    )
    pdf_file = fields.Binary(string="PDF File", attachment=True)


    _sql_constraints = [
        (
            'unique_book_lang',
            'unique(book_id, lang_id)',
            'Each book can have only one file per language!'
        )
    ]

    @api.constrains('book_id', 'lang_id')
    def _check_unique_book_lang(self):
        for record in self:
            exists = self.search([
                ('book_id', '=', record.book_id.id),
                ('lang_id', '=', record.lang_id.id),
                ('id', '!=', record.id)
            ], limit=1)
            if exists:
                raise ValidationError(
                    _("This book already has a file in the selected language.")
                )