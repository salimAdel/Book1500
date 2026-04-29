# -*- coding: utf-8 -*-
from odoo import fields, models

class ResUser(models.Model):
    _inherit = 'res.users'

    is_admin = fields.Boolean(string="Is Admin", default=False)
    subscription_start_date = fields.Date(string="Subscription Start Date")
    subscription_end_date = fields.Date(string="Subscription End Date")
    subscription_type = fields.Selection([
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),], string='Subscription Type', 
        default='monthly'
        )