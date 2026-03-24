# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request


class IcaAvailabilityController(http.Controller):

    @http.route('/ica/availability', type='http', auth='public', website=True, csrf=False)
    def get_availability(self, start=None, end=None, **kwargs):
        domain = []
        if start:
            domain.append(('date', '>=', start))
        if end:
            domain.append(('date', '<=', end))

        slots = request.env['ica.availability'].sudo().search(domain)
        data = [
            {
                'date': str(s.date),
                'status': s.status,
                'note': s.note or '',
            }
            for s in slots
        ]
        return request.make_response(
            json.dumps(data),
            headers=[('Content-Type', 'application/json')]
        )

    @http.route('/ica/contact', type='http', auth='public', website=True, csrf=False, methods=['POST'])
    def contact_form(self, **kwargs):
        name = kwargs.get('name', '')
        email = kwargs.get('email_from', '')
        phone = kwargs.get('phone', '')
        service = kwargs.get('service', '')
        subject = kwargs.get('subject', 'Website Contact Form')
        message = kwargs.get('body_html', '')
        location = kwargs.get('project_location', '')
        lat = kwargs.get('project_lat', '')
        lng = kwargs.get('project_lng', '')

        body_parts = [
            '<p><strong>From:</strong> %s</p>' % name,
            '<p><strong>Email:</strong> %s</p>' % email,
        ]
        if phone:
            body_parts.append('<p><strong>Phone:</strong> %s</p>' % phone)
        if service:
            body_parts.append('<p><strong>Service:</strong> %s</p>' % service)
        if location:
            loc_text = location
            if lat and lng:
                loc_text += ' (<a href="https://www.openstreetmap.org/?mlat=%s&mlon=%s">map</a>)' % (lat, lng)
            body_parts.append('<p><strong>Project Location:</strong> %s</p>' % loc_text)
        if message:
            body_parts.append('<hr/><p>%s</p>' % message.replace('\n', '<br/>'))

        body = ''.join(body_parts)

        request.env['mail.mail'].sudo().create({
            'subject': subject,
            'email_from': '%s <%s>' % (name, email),
            'email_to': 'pakelkdrona@gmail.com',
            'body_html': body,
            'auto_delete': True,
        }).send()

        return request.redirect('/contactus-thank-you')
