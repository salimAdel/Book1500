# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request


class SubscriptionController(http.Controller):
    @http.route('/api/library/subscribe', type='http', auth='user', methods=['POST'], csrf=False)
    def create_subscription(self, **kwargs):
        user = request.env.user
        raw = request.httprequest.data.decode()
        vals = json.loads(raw) if raw else {}
        startdate = vals.get('start_date')
        enddate = vals.get('end_date')
        subscriptiontype = vals.get('subscription_type')

        subscription = request.env['subscription'].sudo().create({
            'user_id': user.id,
            'start_date': startdate,
            'end_date': enddate,
            'subscription_type': subscriptiontype,
        })

        response_data = {
            'id': subscription.id,
            'user_id': subscription.user_id.id,
            'start_date': subscription.start_date.isoformat() if subscription.start_date else None,
            'end_date': subscription.end_date.isoformat() if subscription.end_date else None,
            'subscription_type': subscription.subscription_type,
        }

        return http.Response(
            json.dumps({'status': 201, 'data': response_data}),
            content_type='application/json'
        )
    
    @http.route('/api/library/subscription', type='http', auth='user', methods=['GET'], csrf=False)
    def get_subscriptions(self, **kwargs):
        user = request.env.user
        subscriptions = request.env['subscription'].sudo().search([('user_id', '=', user.id)])
        data = [{
            'id': sub.id,
            'user_id': sub.user_id.id,
            'start_date': sub.start_date.isoformat() if sub.start_date else None,
            'end_date': sub.end_date.isoformat() if sub.end_date else None,
            'subscription_type': sub.subscription_type,
        } for sub in subscriptions]

        return http.Response(
            json.dumps({'status': 200, 'data': data}),
            content_type='application/json'
        )
    @http.route('/api/library/subscription/<int:subscription_id>', type='http', auth='user', methods=['GET'], csrf=False)
    def get_subscription(self, subscription_id, **kwargs):
        user = request.env.user
        subscription = request.env['subscription'].sudo().search([('id', '=', subscription_id), ('user_id', '=', user.id)], limit=1)

        if not subscription:
            return http.Response(
                json.dumps({'status': 404, 'error': 'Subscription not found'}),
                content_type='application/json'
            )

        response_data = {
            'id': subscription.id,
            'user_id': subscription.user_id.id,
            'start_date': subscription.start_date.isoformat() if subscription.start_date else None,
            'end_date': subscription.end_date.isoformat() if subscription.end_date else None,
            'subscription_type': subscription.subscription_type,
        }

        return http.Response(
            json.dumps({'status': 200, 'data': response_data}),
            content_type='application/json'
        )
