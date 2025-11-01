# -*- coding: utf-8 -*-
from odoo import fields,models, api

class Subscription(models.Model):
    _name = 'subscription'

    user_id = fields.Many2one('res.users', string='User')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    subscription_type = fields.Selection([
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),], string='Subscription Type', default='monthly')
    subscription_status = fields.Selection([
        ('new', 'New'),
        ('active', 'Active'),
        ('ended', 'Ended'),], string='Subscription Status', compute='_compute_subscription_status', store=True)

    @api.depends('start_date', 'end_date')
    def _compute_subscription_status(self):
        for record in self:
            if record.end_date and record.end_date < fields.Date.today():
                record.subscription_status = 'ended'
            elif record.start_date and record.start_date <= fields.Date.today() <= record.end_date:
                record.subscription_status = 'active'
            else:
                record.subscription_status = 'new'