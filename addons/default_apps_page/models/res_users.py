# -*- coding: utf-8 -*-
from odoo import models, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def _get_default_home_action(self):
        """Return action to show all installed apps as home page"""
        # Return the menu with all installed apps
        return self.env.ref('default_apps_page.action_show_installed_apps', raise_if_not_found=False) or super()._get_default_home_action()
