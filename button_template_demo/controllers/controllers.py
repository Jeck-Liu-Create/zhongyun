# -*- coding: utf-8 -*-
from odoo import http


class ButtonTemplateDemo(http.Controller):
    @http.route('/button_template_demo/button_template_demo', auth='public')
    def index(self, **kw):
        return "Hello, world"

    @http.route('/button_template_demo/button_template_demo/objects', auth='public')
    def list(self, **kw):
        return http.request.render('button_template_demo.listing', {
            'root': '/button_template_demo/button_template_demo',
            'objects': http.request.env['button_template_demo.button_template_demo'].search([]),
        })

    @http.route('/button_template_demo/button_template_demo/objects/<model("button_template_demo.button_template_demo"):obj>', auth='public')
    def object(self, obj, **kw):
        return http.request.render('button_template_demo.object', {
            'object': obj
        })
