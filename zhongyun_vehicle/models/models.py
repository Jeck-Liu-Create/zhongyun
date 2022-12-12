from operator import index
import string
from unicodedata import name
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import datetime


class ZyVehicle(models.Model):
    # 中运物流车辆管理业务
    _name = 'zy.vehicle'
    _description = '车辆信息'
    # 继承消息部分
    _inherit = ['mail.thread', 'mail.activity.mixin']  # track_visibility

    name = fields.Char('车辆编号', index=True, required=True)

    user_id = fields.Many2one('res.users', default=lambda self: self.env.user, string='创建者', readonly=True)

    # yundan_ids = fields.char('zy.yundan', 'car_id', string='运单')

    # yundan_ids = fields.One2many('zy.yundan', 'car_id', string="运单数据")

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'CarID only'),
    ]
