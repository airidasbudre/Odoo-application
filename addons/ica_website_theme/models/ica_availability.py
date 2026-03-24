# -*- coding: utf-8 -*-
from datetime import date, timedelta
from odoo import models, fields, api


class IcaAvailability(models.Model):
    _name = 'ica.availability'
    _description = 'Drone Service Availability'
    _order = 'date'
    _rec_name = 'date'

    date = fields.Date(string='Date', required=True)
    status = fields.Selection([
        ('available', 'Available'),
        ('partial', 'Partially Available'),
        ('busy', 'Busy / Occupied'),
    ], string='Status', required=True, default='available')
    note = fields.Char(string='Note (visible to customers)')
    auto_generated = fields.Boolean(default=False, string='Auto-generated')
    color = fields.Integer(compute='_compute_color', store=False)

    @api.depends('status')
    def _compute_color(self):
        colors = {'available': 10, 'partial': 3, 'busy': 9}
        for rec in self:
            rec.color = colors.get(rec.status, 0)

    @api.model
    def generate_default_availability(self, days_ahead=90):
        """Generate default availability for the next N days.
        Weekdays = partial, weekends = available.
        Skips dates that already have a record.
        """
        today = date.today()
        existing = set(self.search([
            ('date', '>=', today),
            ('date', '<=', today + timedelta(days=days_ahead)),
        ]).mapped('date'))

        to_create = []
        for i in range(days_ahead):
            d = today + timedelta(days=i)
            if d not in existing:
                # weekday() 0=Mon, 6=Sun
                status = 'available' if d.weekday() >= 5 else 'partial'
                to_create.append({
                    'date': d,
                    'status': status,
                    'auto_generated': True,
                })

        if to_create:
            self.create(to_create)

    @api.model
    def cron_generate_availability(self):
        self.generate_default_availability(days_ahead=90)
