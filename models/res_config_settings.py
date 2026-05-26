# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    """Inherits the model Res Config Settings to extend the model"""
    _inherit = 'res.config.settings'

    # API Keys
    production_api_key = fields.Char(
        string='Production API Key',
        config_parameter='fpg_odoo_klaviyo_key.production_api_key'
    )
    test_api_key = fields.Char(
        string='Test API Key',
        config_parameter='fpg_odoo_klaviyo_key.test_api_key',
        help='It\'s not mandatory to set up the test key'
    )
    is_test = fields.Boolean(
        string='Test Mode',
        config_parameter='fpg_odoo_klaviyo_key.is_test',
        default=False
    )

    def get_klaviyo_api_key(self):
        """Get the API Key
        """
        config = self.env['ir.config_parameter']
        is_test = config.get_param('fpg_odoo_klaviyo_key.is_test')
        production_api_key = config.get_param('fpg_odoo_klaviyo_key.production_api_key')
        test_api_key = config.get_param('fpg_odoo_klaviyo_key.test_api_key')
        return is_test, test_api_key if is_test else production_api_key

    def get_test_notification(self, result):
        """Alert the user if the connection is successfuly or not
        """
        if result.get('code') == 200:
            message = result.get('message') if 'message' in result else 'Connection to Klaviyo was successful.'
        elif result.get('code') == 401:
            message = 'Connection to Klaviyo was not authorized. Plase check your Private API Key.'
        elif result.get('code') == 403:
            message = f'Connection to Klaviyo was forbidden. Configuration - {result.get("action")}, ' \
                f'plase check permissions to perform: [{result.get("scope")}] action(s)).'
        elif result.get('code') == 500:
            message = 'Something is wrong with the Klaviyo server. Please try again in a few minutes.'
        elif result.get('code') == 503:
            message = 'Klaviyo service is unavailable. Please try again in a few minutes.'
        else:
            message = f'Unknown error in Configuration - {result.get("action")} accessing to [{result.get("scope")}] action(s).'
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Connection successful') if result.get('code') == 200 else _('Connection failed'),
                'message': message,
                'sticky': False,
                'type': 'success' if result.get('code') == 200 else 'danger'
            }
        }
        return notification
