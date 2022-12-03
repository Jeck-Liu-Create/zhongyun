from operator import index
import string
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import datetime
   
class ZyPound(models.Model):
    # 中运物流磅单管理业务
    _name = 'zy.pound'  
    _description = '磅单数据管理'
    # 继承消息部分
    _inherit = ['mail.thread', 'mail.activity.mixin'] # track_visibility

    name = fields.Char('磅单编号', index=True, required=True)

    pound_supplier = fields.Char('发货人（供应商）')

    transport_goods = fields.Char('运输货物名称', required=True)
    
    car_id = fields.Many2one('zy.vehicle', '车辆编号', required=True)

    manufacture_date = fields.Date('出厂日期', required=True)

    delivery_date = fields.Date('发货日期', required=True)

    car_number = fields.Integer('车数', required=True)

    net_weight = fields.Float('净重', required=True)

    primary_weight = fields.Float('原发重', required=True)

    transport_company = fields.Many2one('res.company',  string='运输单位')

    Tdelivery_location = fields.Many2one('zy.address', string='发货地址')

    car_id_other = fields.Many2one('zy.vehicle', '油车车号')

    tram_carrier_unit = fields.Char('电车承运单位')

    remark = fields.Char('备注')


    user_id = fields.Many2one('res.users', default=lambda self: self.env.user , string='创建者', readonly=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'pounds single only'),
    ]

    @api.constrains('manufacture_date', 'delivery_date')
    def _check_date(self):
        for data in self:
            if data.manufacture_date < data.delivery_date:
                raise ValidationError(
                    "出厂日期 < 发货日期"
                )

    def name_get(self):
        result = []
        for rec in self:
            if rec.car_id_other.name:
                name = '[%s] %s %s' % (rec.name, rec.car_id.name, rec.car_id_other.name)
                result.append((rec.id, name))
            else:
                name = '[%s] %s' % (rec.name, rec.car_id.name)
                result.append((rec.id, name))
        return result

