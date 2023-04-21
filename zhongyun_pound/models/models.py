from operator import index
import string
from odoo import models, fields, api
from odoo.api import call_kw
from odoo.exceptions import UserError, ValidationError
import datetime
import logging
from .utils import LocalToUtc

_logger = logging.getLogger(__name__)


class ZyPound(models.Model):
    # 中运物流磅单管理业务
    _name = 'zy.pound'
    _description = '磅单数据管理'
    # 继承消息部分
    _inherit = ['mail.thread', 'mail.activity.mixin']  # track_visibility

    pound_id = fields.Many2one('zy.pound.unit', '过磅单组', required=True)

    state = fields.Selection(
        [
            ("to_match", "待匹配"),
            ("not_match", "匹配失败"),
            ("match", "匹配完成"),
            ("to_payment", "待付款"),
            ("rejected", "退回"),
            ("payment", "付款完成"),
            ("confirm_rejected", "确认退回"),
        ],
        "状态",
        default="to_match",
        readonly=True,
    )

    ZyPound_company_id = fields.Many2one(
        'res.company',
        string="所属公司",
        related='pound_id.ZyPoundUint_company_id',
        readonly=True
    )

    yundan_id = fields.Char('运单')
    # yundan_id = fields.One2many("zy.yundan", "pound_id", string="Tests")
    active = fields.Boolean(default=True, help="Set active.")

    pound_id_percentage = fields.Many2one('zy.buckle', string='计量信息', related="pound_id.pound_unit_zy_buckle",
                                          readonly=True)

    name = fields.Char(string='磅单编号', index=True, required=True)

    pound_supplier = fields.Char('发货人（供应商）')

    transport_goods = fields.Char('运输货物名称', required=True)
    transport_goods_specification = fields.Char('规格型号')

    car_id = fields.Many2one('zy.vehicle', '车辆编号', required=True)

    manufacture_date = fields.Date('出厂日期', required=True)

    delivery_date = fields.Date('发货日期', required=True)

    car_number = fields.Integer('车数', required=True)

    net_weight = fields.Float('净重', required=True)

    primary_weight = fields.Float('原发重', required=True)

    transport_company = fields.Many2one('res.company', string='运输单位')

    delivery_location = fields.Many2one('zy.address', string='发货地址')

    car_id_other = fields.Many2one('zy.vehicle', string='油车车号')

    tram_carrier_unit = fields.Char(string='电车承运单位')

    ZyPound_user_id = fields.Many2one('res.users', default=lambda self: self.env.user, string='创建者', readonly=True)

    _sql_constraints = [
        ('pound_name_uniq', 'unique(name)', 'pounds single only'),
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

    """ 匹配运单 """

    def action_matching_data(self):
        Model_yundan = self.env['zy.yundan'].sudo()
        for rec in self:
            if rec.state == 'to_match' or rec.state == 'not_match' or rec.state == 'confirm_rejected':
                domain = ['&', ('zy_yundan_company_id', '=', rec.ZyPound_company_id.id), '|', '&', '&',
                          ('single_supplement', '=', False),
                          ('state', 'in', ['to_match', 'not_match', 'confirm_rejected']), '&', '|',
                          ('car_id', '=', rec.car_id.id), ('car_id', '=', rec.car_id_other.id), '&',
                          ('establish_datetime', '>=', LocalToUtc(rec.delivery_date)),
                          ('establish_datetime', '<=', LocalToUtc(rec.manufacture_date)),
                          '&', '&', ('single_supplement', '=', True),
                          ('state', 'in', ['to_match', 'not_match', 'confirm_rejected']), '&', '|',
                          ('car_id', '=', rec.car_id.id), ('car_id', '=', rec.car_id_other.id), '&',
                          ('single_supplement_datetime', '>=', LocalToUtc(rec.delivery_date)),
                          ('single_supplement_datetime', '<=', LocalToUtc(rec.manufacture_date))]
                res = Model_yundan.search(domain, limit=1, order='id DESC')
                if len(res) == 1:
                    rec.yundan_id = res[0].id
                    rec.state = 'match'
                    Model_yundan.search([('id', '=', res[0].id)]).write(
                        {'pound_id': rec.id, 'state': 'match'})

                else:
                    rec.state = 'not_match'
            else:
                raise UserError(" 在'%s'状态下无法匹配运单." % rec.state)

    """ 通知付款 """

    def action_notice_of_payment(self):
        Model_yundan = self.env['zy.yundan'].sudo()
        for rec in self:
            if rec.state == 'match':
                yudna_data = Model_yundan.search([('id', '=', rec.yundan_id)])
                call_kw(self.env['zy.yundan'].sudo(),
                        'action_notice_of_payment',
                        [yudna_data.id],
                        {})
                rec.write({"state": "to_payment"})

    """ 批量付款退回 """

    def action_payment_rollback(self):
        _logger.warning('=== 付款退回 ===')
        Model_yundan = self.env['zy.yundan'].sudo()
        for rec in self:
            if rec.state == 'to_payment':
                rec.write({"state": "confirm_rejected"})
                Model_yundan.search([('id', '=', rec.yundan_id)]).write({"state": "confirm_rejected"})


class ZyPoundUint(models.Model):
    # 中运物流磅单组
    _name = 'zy.pound.unit'
    _description = '磅单数据管理'

    ZyPoundUint_company_id = fields.Many2one(
        "res.company",
        "所属公司",
        help="如果设置，页面只能从该公司访问",
        default=lambda self: self.env.company,
    )
    active = fields.Boolean(default=True, help="Set active.")

    name = fields.Char('磅单组编号', index=True, default='新建磅单组', readonly=True)

    ZyPoundUint_establish_datetime = fields.Datetime('创建时间', default=lambda self: fields.Datetime.now(), required=True,
                                                     readonly=True)

    pound_uint_buckle_rules = fields.Many2one('zy.buckle.rules', string='计量规则', required=True)

    pound_unit_zy_buckle = fields.Many2one('zy.buckle', string='计量信息', required=True,
                                           domain=lambda self: self.pound_unit_zy_buckle_function())

    pound_establish_datetime = fields.Datetime('计量目标时间', default=lambda self: fields.Datetime.now(), required=True)

    ZyPoundUint_user_id = fields.Many2one('res.users', default=lambda self: self.env.user, string='创建者', readonly=True)

    """ 磅单相关字段 """
    pound_ids = fields.One2many(
        'zy.pound',
        'pound_id',
        store=True,
        string='全部磅单',

    )
    pound_ids_match = fields.One2many(
        'zy.pound',
        'pound_id',
        store=True,
        string='匹配完成',
        domain=[('state', '=', 'match')]
    )

    pound_ids_not_match = fields.One2many(
        'zy.pound',
        'pound_id',
        store=True,
        string='匹配失败',
        domain=[('state', '=', 'not_match')]

    )
    pound_ids_to_match = fields.One2many(
        'zy.pound',
        'pound_id',
        store=True,
        string='待匹配',
        domain=[('state', '=', 'to_match')]
    )

    pound_ids_to_payment = fields.One2many(
        'zy.pound',
        'pound_id',
        store=True,
        string='待付款',
        domain=[('state', '=', 'to_payment')]
    )

    pound_ids_rejected = fields.One2many(
        'zy.pound',
        'pound_id',
        store=True,
        string='退回',
        domain=[('state', '=', 'rejected')]
    )

    pound_ids_payment = fields.One2many(
        'zy.pound',
        'pound_id',
        store=True,
        string='付款完成',
        domain=[('state', '=', 'payment')]
    )

    pound_ids_confirm_rejected = fields.One2many(
        'zy.pound',
        'pound_id',
        store=True,
        string='确认退回',
        domain=[('state', '=', 'confirm_rejected')]
    )

    """" 全部磅单列表按钮 """

    def pound_line_ids(self):
        return {
            'name': '全部磅单',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'zy.pound',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('pound_id', '=', self.id)],
            'context': {'create': False},
        }

    """" 匹配成功磅单列表按钮 """

    def pound_line_match_ids(self):
        return {
            'name': '匹配成功磅单',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'zy.pound',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': ['&', ('pound_id', '=', self.id), ('state', '=', 'match')],
            'context': {'create': False},
        }

    """" 匹配失败单列表按钮 """

    def pound_line_not_match_ids(self):
        return {
            'name': '匹配失败',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'zy.pound',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': ['&', ('pound_id', '=', self.id), ('state', '=', 'not_match')],
            'context': {'create': False},
        }

    """" 待匹配磅单列表按钮 """

    def pound_line_to_match_ids(self):
        return {
            'name': '待匹配磅单',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'zy.pound',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': ['&', ('pound_id', '=', self.id), ('state', '=', 'to_match')],
            'context': {'create': False},
        }

    """" 待付款磅单列表按钮 """

    def pound_line_to_payment_ids(self):
        return {
            'name': '待付款磅单',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'zy.pound',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': ['&', ('pound_id', '=', self.id), ('state', '=', 'to_payment')],
            'context': {'create': False},
        }

    """" 付款完成单列表按钮 """

    def pound_line_payment_ids(self):
        return {
            'name': '付款完成磅单',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'zy.pound',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': ['&', ('pound_id', '=', self.id), ('state', '=', 'payment')],
            'context': {'create': False},
        }

    """" 确认退回单列表按钮 """

    def pound_line_confirm_rejected(self):
        return {
            'name': '确认退回磅单',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'zy.pound',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': ['&', ('pound_id', '=', self.id), ('state', '=', 'confirm_rejected')],
            'context': {'create': False},
        }

    @api.onchange('pound_uint_buckle_rules')
    def _onchange_pound_unit_zy_buckle(self):
        Model_buckle = self.env['zy.buckle']
        domain = ['&', ('buckle_rules', '=', self.pound_uint_buckle_rules.id), '&', ('state', '=', "approved"),
                  '&', ('start_datetime', '<=', self.ZyPoundUint_establish_datetime), '|',
                  ('stop_datetime', '>', self.ZyPoundUint_establish_datetime), ('stop_datetime', '=', False)]
        res = Model_buckle.search(domain, limit=1, order='id DESC')

        if len(res):
            self.pound_unit_zy_buckle = res[0].id

        return {'domain': {
            'pound_unit_zy_buckle': ['&', ('buckle_rules', '=', self.pound_uint_buckle_rules.id), '&',
                                     ('state', '=', "approved"), '&',
                                     ('start_datetime', '<=', self.ZyPoundUint_establish_datetime), '|',
                                     ('stop_datetime', '>', self.ZyPoundUint_establish_datetime),
                                     ('stop_datetime', '=', False)]}}

    def pound_unit_zy_buckle_function(self):
        domain = ['&', ('buckle_rules', '=', self.pound_uint_buckle_rules.id), '&', ('state', '=', "approved"),
                  '&', ('start_datetime', '<=', self.ZyPoundUint_establish_datetime), '|',
                  ('stop_datetime', '>', self.ZyPoundUint_establish_datetime), ('stop_datetime', '=', False)]
        return domain

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('zy.pound.unit')
        vals['name'] = seq
        new_record = super(ZyPoundUint, self).create(vals)
        return new_record

    def action_import_zy_pound(self):
        ctx = dict(self.env.context, default_unit_id=self.id)
        return {
            'name': self.name,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'zy.pound.import',
            'target': 'new',
            'context': ctx,
        }
