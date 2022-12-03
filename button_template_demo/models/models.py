# -*- coding: utf-8 -*-

from odoo import models, fields, api


class button_template_demo(models.Model):
    _name = 'button_template_demo.button_template_demo'
    _description = 'button_template_demo.button_template_demo'

    name = fields.Char()
    value = fields.Integer()
    value2 = fields.Float(compute="_value_pc", store=True)
    description = fields.Text()

    @api.depends('value')
    def _value_pc(self):
        for record in self:
            record.value2 = float(record.value) / 100

    # test_force_show
    def test_force_show(self):
        # warning
        return {
            'warning': {
                'title': 'Warning',
                'message': 'This is a warning message',
            }
        }
