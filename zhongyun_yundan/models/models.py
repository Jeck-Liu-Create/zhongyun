from email.policy import default
from modulefinder import Module
import string
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import math
import datetime
import logging
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class ZyYundan(models.Model):
    # 中运物流运单业务
    _name = 'zy.yundan'
    _description = '运单业务'
    # 继承消息部分
    _inherit = ['mail.thread', 'mail.activity.mixin']  # track_visibility
    zy_yundan_company_id = fields.Many2one(
        "res.company",
        "所属公司",
        help="如果设置，页面只能从该公司访问",
        index=True,
        ondelete="cascade",
        default=lambda self: self.env.company,
    )

    name = fields.Char('运单编号', index=True, default='新建运单', readonly=True)

    active = fields.Boolean(default=True, help="Set active.")

    car_id = fields.Many2one('zy.vehicle', '运单车辆编号', required=True, index=True)

    single_supplement = fields.Boolean('是否补单', default=False, help="是否补单")

    establish_datetime = fields.Datetime('建单时间', default=lambda self: fields.Datetime.now(), required=True)

    establish_date = fields.Date('建单日期', compute="_get_field_compute_establish_date")

    single_supplement_datetime = fields.Datetime('补单目标时间', default=lambda self: fields.Datetime.now(), required=True)

    single_supplement_date = fields.Date('补单目标日期', compute="_get_field_compute_single_supplement_date")

    """"""""" """""""""
    """运价单相关信息"""
    """"""""" """""""""
    yundan_unit = fields.Many2one('zy.yundan.unit', '运单组', required=True,
                                  domain=lambda self: self._yundan_unit_function())

    yundan_zy_charge_rules = fields.Many2one(string='运单规则', related='yundan_unit.yundan_unit_zy_charge_rules',
                                             store=True, readonly=True)

    edit_function = fields.Boolean(related='yundan_unit.edit_function', related_sudo=True)

    zy_charge = fields.Many2one(string='运价单', related='yundan_unit.zy_charge', store=True, readonly=True)

    currency_id = fields.Many2one('res.currency', "货币", readonly=True, default=7)

    transport_price = fields.Monetary(string='运输价格', related='zy_charge.transport_price', store=True, readonly=True,
                                      compute='_amount_all')

    """"""""" """""""""
    " 货物价格相关信息 "
    """"""""" """""""""
    yundan_zy_goods_price = fields.Many2one(string='货物信息', related='yundan_unit.yundan_unit_zy_goods_price', store=True,
                                            readonly=True)

    goods_price = fields.Monetary(string='货物价格', related='yundan_zy_goods_price.goods_price', store=True, readonly=True,
                                  compute='_amount_all')

    """ 判断用户是否为所有者 """
    am_i_owner = fields.Boolean(compute="_compute_am_i_owner")
    """ 判断用户是否为出纳人员 """
    am_i_cashier = fields.Boolean(compute="_compute_am_i_cashier")

    """ 判断用户是否管理员 """
    am_i_admin = fields.Boolean(compute="_compute_am_i_admin")

    pound_id = fields.Many2one('zy.pound', '磅单', domain=lambda self: self._pound_id_function(), readonly=True)

    pound_id_bool = fields.Boolean(default=False, compute="_pound_id_bool_function")
    """"""""" """""""""
    """ 磅单相关信息 """
    """"""""" """""""""
    pound_id_supplier = fields.Char('发货人（供应商）', related='pound_id.pound_supplier', store=True, readonly=True)

    pound_id_transport_goods = fields.Char('运输货物名称', related='pound_id.transport_goods', store=True, readonly=True)

    pound_is_transport_goods_specification = fields.Char('规格型号', related='pound_id.transport_goods_specification',
                                                         store=True, readonly=True)

    pound_id_car_id = fields.Many2one('zy.vehicle', '车辆编号', related='pound_id.car_id', store=True, readonly=True)

    pound_id_manufacture_date = fields.Date('出厂日期', related='pound_id.manufacture_date', store=True, readonly=True)

    pound_id_delivery_date = fields.Date('发货日期', related='pound_id.delivery_date', store=True, readonly=True)

    pound_id_car_number = fields.Integer('车数', related='pound_id.car_number', store=True, readonly=True,
                                         compute='_amount_all')

    pound_id_net_weight = fields.Float('净重', related='pound_id.net_weight', store=True, readonly=True,
                                       compute='_amount_all')

    pound_id_primary_weight = fields.Float('原发重', related='pound_id.primary_weight', store=True, readonly=True,
                                           compute='_amount_all')

    pound_id_transport_company = fields.Many2one(string='运输单位', related='pound_id.transport_company', store=True,
                                                 readonly=True)

    pound_id_Tdelivery_location = fields.Many2one(string='发货地址', related='pound_id.delivery_location', store=True,
                                                  readonly=True)

    pound_id_car_id_other = fields.Many2one(string='油车车号', related='pound_id.car_id_other', store=True, readonly=True)

    pound_id_tram_carrier_unit = fields.Char(string='电车承运单位', related='pound_id.tram_carrier_unit', store=True,
                                             readonly=True)

    pound_id_buckle = fields.Many2one(string='计量信息', related='pound_id.pound_id_percentage', store=True,
                                      readonly=True)
    pound_id_percentage_data = fields.Float(string="计量比例", related="pound_id_buckle.buckle_percentage", store=True,
                                            readonly=True, compute='_amount_all')

    """"""""" """""""""

    """ 运单总价值相关字段 """

    amount_untaxed = fields.Monetary(string='付车总额', digits=(10, 3), store=True, readonly=True, compute='_amount_all')

    kui_tons = fields.Float('亏吨量', digits=(10, 4), compute='_amount_all')

    kui_tons_price = fields.Monetary('亏吨款', digits=(10, 3), compute='_amount_all')

    deduct_price = fields.Monetary('扣减亏吨款', compute='_amount_all')

    amount_tax = fields.Monetary(string='实际付车', digits=(10, 3), store=True, readonly=True, compute='_amount_all')

    amount_total = fields.Monetary(string='结算金额', digits=(10, 3), store=True, readonly=True, compute='_amount_all')

    """ 状态信息 """

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

    """ 运单总价计算 """

    @api.depends('zy_charge', 'pound_id')
    def _amount_all(self):
        """
        计算运单总价
        """
        for rec in self:
            # 付车总额
            amount_untaxed = rec.pound_id_net_weight * rec.transport_price

            # 亏吨量 亏吨量=净重-原发重x（1-运损率)
            kui_tons = rec.pound_id_net_weight - rec.pound_id_primary_weight * (1 - rec.pound_id_percentage_data)

            # 亏吨款
            kui_tools = lambda x: x if x < 0 else 0
            kui_tons_price = kui_tools(kui_tons) * rec.goods_price

            # 扣减亏吨款
            deduct_tools = lambda x: -x if x < 0 else 0
            deduct_price = deduct_tools(kui_tons_price)

            # 实际付车
            amount_tax = amount_untaxed + kui_tons_price

            # 结算金额
            if amount_tax % 10 < 9:
                amount_total = math.modf(amount_tax * 0.1)[1] * 10
            else:
                amount_total = (math.modf(amount_tax * 0.1)[1] + 1) * 10

            rec.update({
                'amount_untaxed': amount_untaxed,
                'kui_tons': kui_tons,
                'kui_tons_price': kui_tons_price,
                'deduct_price': deduct_price,
                'amount_tax': amount_tax,
                'amount_total': amount_total
            })

    @api.onchange('car_id', 'single_supplement', 'establish_datetime', 'single_supplement_datetime', 'pound_id')
    def _onchange_pound_id(self):
        self.pound_id = False
        Model_charge = self.env['zy.pound']
        if not self.single_supplement:
            domain = ['&', '|', ('car_id', '=', self.car_id.id), ('car_id_other', '=', self.car_id.id), '&', (
                'delivery_date', '<=', datetime.datetime.strftime((self.establish_datetime.date()), '%Y-%m-%d')), (
                          'manufacture_date', '>=',
                          datetime.datetime.strftime((self.establish_datetime.date()), '%Y-%m-%d'))]
            _logger.info(domain)
            Model_charge.search(domain, limit=1, order='id DESC')

            return {'domain': {
                'pound_id': ['&', '|', ('car_id', '=', self.car_id.id), ('car_id_other', '=', self.car_id.id), '&', (
                    'delivery_date', '<=', datetime.datetime.strftime((self.establish_datetime.date()), '%Y-%m-%d')),
                             (
                                 'manufacture_date', '>=',
                                 datetime.datetime.strftime((self.establish_datetime.date()), '%Y-%m-%d'))]}}
        else:
            domain = ['&', '|', ('car_id', '=', self.car_id.id), ('car_id_other', '=', self.car_id.id), '&', (
                'delivery_date', '<=',
                datetime.datetime.strftime((self.single_supplement_datetime.date()), '%Y-%m-%d')),
                      ('manufacture_date', '>=',
                       datetime.datetime.strftime((self.single_supplement_datetime.date()), '%Y-%m-%d'))]
            _logger.info(domain)
            Model_charge.search(domain, limit=1, order='id DESC')

            return {'domain': {
                'pound_id': ['&', '|', ('car_id', '=', self.car_id.id), ('car_id_other', '=', self.car_id.id), '&', (
                    'delivery_date', '<=',
                    datetime.datetime.strftime((self.single_supplement_datetime.date()), '%Y-%m-%d')), (
                                 'manufacture_date', '>=',
                                 datetime.datetime.strftime((self.single_supplement_datetime.date()), '%Y-%m-%d'))]}}

    @api.onchange('establish_datetime', 'single_supplement_datetime')
    def _onchange_pound_date(self):
        self.establish_date = datetime.datetime.strftime((self.establish_datetime.date()), '%Y-%m-%d')
        self.single_supplement_date = datetime.datetime.strftime((self.single_supplement_datetime.date()),
                                                                 '%Y-%m-%d')

    @api.model
    def create(self, vals):
        if self.edit_function:
            _logger.info("是否可编辑%s" % self.edit_function)
            raise UserError(" 运单组信息有变化，无法创建新运单 ")
        seq = self.env['ir.sequence'].next_by_code('zy.yundan') or '/'
        vals['name'] = seq
        self.with_context(tracking_disable=True)
        new_record = super(ZyYundan, self).create(vals)
        return new_record

    # def write(self, vals):
    #     if (self.state in ['match', 'to_payment', 'payment', 'rejected']) and ('state' in vals):
    #         raise UserError(
    #             _('【%s】状态下无法修改数据 ') % (
    #                 self.state,))
    #     self.with_context(tracking_disable=True)
    #     return super(ZyYundan, self).write(vals)

    @api.depends('establish_datetime')
    def _get_field_compute_establish_date(self):
        """ 自动将时间字段改成日期字段 """
        for rec in self:
            rec.establish_date = datetime.datetime.strftime((rec.establish_datetime.date()), '%Y-%m-%d')

    @api.depends('single_supplement_datetime')
    def _get_field_compute_single_supplement_date(self):
        """ 自动将时间字段改成日期字段 """
        for rec in self:
            rec.single_supplement_date = datetime.datetime.strftime((rec.single_supplement_datetime.date()),
                                                                    '%Y-%m-%d')

    def name_get(self):
        """ 选择时显示字段的字段名称 """
        result = []
        for rec in self:
            name = '[%s] %s' % (rec.name, rec.car_id.name)
            result.append((rec.id, name))
        return result

    """ 批量匹配磅单 """

    def action_matching(self):
        _logger.warning('=== 批量匹配磅单 ===')
        Model_charge = self.env['zy.pound']
        for rec in self:
            if rec.state == 'to_match' or rec.state == 'not_match' or rec.state == 'confirm_rejected':
                if not rec.single_supplement:
                    domain = ['&', ('state', 'in', ['to_match', 'not_match', 'confirm_rejected']), '&', '|',
                              ('car_id', '=', rec.car_id.id),
                              ('car_id_other', '=', rec.car_id.id), '&', (
                                  'delivery_date', '<=',
                                  datetime.datetime.strftime((rec.establish_datetime.date()), '%Y-%m-%d')), (
                                  'manufacture_date', '>=',
                                  datetime.datetime.strftime((rec.establish_datetime.date()), '%Y-%m-%d'))]
                    _logger.info(domain)
                    res = Model_charge.search(domain, limit=1, order='id DESC')
                    if len(res) == 1:
                        rec.pound_id = res[0].id
                        res_write = Model_charge.search([('id', '=', res[0].id)]).write(
                            {'yundan_id': rec.id, 'state': 'match'})
                        print(res_write)
                        self._amount_all()
                        rec.state = 'match'

                    else:
                        rec.state = 'not_match'
                else:
                    domain = ['&', '|', ('car_id', '=', rec.car_id.id), ('car_id_other', '=', rec.car_id.id), '&', (
                        'delivery_date', '<=',
                        datetime.datetime.strftime((rec.single_supplement_datetime.date()), '%Y-%m-%d')), (
                                  'manufacture_date', '>=',
                                  datetime.datetime.strftime((rec.single_supplement_datetime.date()), '%Y-%m-%d'))]
                    _logger.info(domain)
                    res = Model_charge.search(domain, limit=1, order='id DESC')
                    if len(res) == 1:
                        rec.pound_id = res[0].id
                        res_write = Model_charge.search([('id', '=', res[0].id)]).write(
                            {'yundan_id': rec.id, 'state': 'match'})
                        print(res_write)
                        self._amount_all()
                        rec.state = 'match'
                    else:
                        rec.state = 'not_match'

    """ 匹配磅单 """

    def action_matching_data(self):
        _logger.warning('=== 匹配磅单 ===')
        Model_charge = self.env['zy.pound']
        for rec in self:
            if rec.state == 'to_match' or rec.state == 'not_match' or rec.state == 'confirm_rejected':
                if not rec.single_supplement:
                    domain = ['&', '|', ('car_id', '=', rec.car_id.id), ('car_id_other', '=', rec.car_id.id), '&', (
                        'delivery_date', '<=', datetime.datetime.strftime((rec.establish_datetime.date()), '%Y-%m-%d')),
                              (
                                  'manufacture_date', '>=',
                                  datetime.datetime.strftime((rec.establish_datetime.date()), '%Y-%m-%d'))]
                    _logger.info(domain)
                    res = Model_charge.search(domain, limit=1, order='id DESC')
                    if len(res) == 1:
                        rec.pound_id = res[0].id
                        self._amount_all()
                        rec.state = 'match'
                        res_write = Model_charge.search([('id', '=', res[0].id)]).write(
                            {'yundan_id': rec.id, 'state': 'match'})
                        print(res_write)
                    else:
                        rec.state = 'not_match'
                else:
                    domain = ['&', '|', ('car_id', '=', rec.car_id.id), ('car_id_other', '=', rec.car_id.id), '&', (
                        'delivery_date', '<=',
                        datetime.datetime.strftime((rec.single_supplement_datetime.date()), '%Y-%m-%d')), (
                                  'manufacture_date', '>=',
                                  datetime.datetime.strftime((rec.single_supplement_datetime.date()), '%Y-%m-%d'))]
                    _logger.info(domain)
                    res = Model_charge.search(domain, limit=1, order='id DESC')
                    if len(res) == 1:
                        rec.pound_id = res[0].id
                        self._amount_all()
                        rec.state = 'match'
                        res_write = Model_charge.search([('id', '=', res[0].id)]).write(
                            {'yundan_id': rec.id, 'state': 'match'})
                        print(res_write)
                    else:
                        rec.state = 'not_match'
            else:
                raise UserError(" 在'%s'状态下无法匹配运单." % rec.state)

    def _compute_am_i_owner(self):
        """ 检查当前用户是否为该用户的所有者 """
        for rec in self:
            rec.am_i_owner = rec.create_uid == self.env.user

    def _compute_am_i_cashier(self):
        """ 判断【确认付款】和【运单退回】按钮权限 """
        for rec in self:
            rec.am_i_cashier = rec.am_i_cashier_info(self.env.user)

    def am_i_cashier_info(self, user):
        """ 判断【确认付款】和【运单退回】按钮权限 """
        if user.has_group('zhongyun_yundan.zy_yundan_group_account_cashier') or user.has_group(
                'zhongyun_yundan.zy_yundan_group_manager'):
            return True
        else:
            return False

    def _compute_am_i_admin(self):
        """ 判断【匹配磅单】按钮权限 """
        for rec in self:
            rec.am_i_admin = rec.am_i_admin_info(self.env.user)

    def am_i_admin_info(self, user):
        """ 判断【匹配磅单】按钮权限 """
        if user.has_group('zhongyun_yundan.zy_yundan_group_manager'):
            return True
        else:
            return False

    def _pound_id_function(self):
        """ 磅单自动满足匹配限制 """
        if not self.single_supplement:
            domain = ['&', '|', ('car_id', '=', self.car_id.id), ('car_id_other', '=', self.car_id.id), '&',
                      ('delivery_date', '<=', self.establish_date), ('manufacture_date', '>=', self.establish_date)]
        else:
            domain = ['&', '|', ('car_id', '=', self.car_id.id), ('car_id_other', '=', self.car_id.id), '&',
                      ('delivery_date', '<=', self.single_supplement_date),
                      ('manufacture_date', '>=', self.single_supplement_date)]
        return domain

    def _yundan_unit_function(self):
        Model_charge = self.env['zy.charge']
        Model_goods_price = self.env['zy.goods.price']
        domain_chrage_now = ['&', ('state', '=', "approved"), '&', ('start_datetime', '<=', fields.Datetime.now()),
                             '|', ('stop_datetime', '>', fields.Datetime.now()), ('stop_datetime', '=', False)]

        domain_goods_price_now = ['&', ('state', '=', "approved"),
                                  '&', ('start_datetime', '<=', fields.Datetime.now()),
                                  '|', ('stop_datetime', '>', fields.Datetime.now()), ('stop_datetime', '=', False)]

        res_chrage_new = Model_charge.search_read(domain_chrage_now, ['name'])
        res_goods_price_now = Model_goods_price.search_read(domain_goods_price_now, ['name'])

        res_chrage_new_list = []
        for i, val in enumerate(res_chrage_new):
            res_chrage_new_list.append(val['id'])

        res_goods_price_now_list = []
        for i, val in enumerate(res_goods_price_now):
            res_goods_price_now_list.append(val['id'])

        """ 运单组满足当前可用限制 """
        domain = ['&', ("replenish_state", '=', False), '&', ("zy_charge", 'in', res_chrage_new_list),
                  ("yundan_unit_zy_goods_price", 'in', res_goods_price_now_list)]

        return domain

    def _pound_id_bool_function(self):
        """ 检查磅单是否匹配成功,如果匹配成功则显示磅单其他信息,并计算运费 """
        for rec in self:
            if rec.pound_id:
                rec.pound_id_bool = True
            else:
                rec.pound_id_bool = False

    """ 付款通知 """

    def action_notice_of_payment(self):
        _logger.warning('=== 通知付款 ===')
        Model_pound = self.env['zy.pound'].sudo()
        account_cashier_gid = self.env.ref(
            "zhongyun_yundan.zy_yundan_group_account_cashier"
        )
        for rec in self:
            if rec.state == 'match':
                rec.write({"state": "to_payment"})
                Model_pound.search([('id', '=', rec.pound_id.id)]).write({"state": "to_payment"})

                users = self.env["res.users"].search(
                    [("groups_id", "in", account_cashier_gid.id)]
                )
                _logger.info("通知付款")

                for u in users:
                    rec.activity_schedule(
                        'zhongyun_yundan.mail_zhongyun_notice_of_payment',
                        user_id=u.id
                    )

                _logger.info([u.id for u in users])

                rec.message_subscribe([u.id for u in users])
                _logger.info('message_subscribe')
            else:
                raise UserError(" 在'%s'状态下无法执行付款通知 ." % rec.state)

    """ 确认付款 """

    def action_payment(self):
        _logger.warning('=== 确认付款 ===')
        Model_pound = self.env['zy.pound'].sudo()
        for rec in self:
            if rec.state == 'to_payment':
                rec.write({"state": "payment"})
                Model_pound.search([('id', '=', rec.pound_id.id)]).write({"state": "payment"})

                # 更新 activity
                rec.activity_feedback(['zhongyun_yundan.mail_zhongyun_notice_of_payment'])

    """ 运单退回 """

    def action_rejected(self):
        _logger.warning('=== 运单退回 ===')
        Model_pound = self.env['zy.pound'].sudo()

        for rec in self:
            if rec == 'to_payment':
                rec.write({"state": "rejected"})
                Model_pound.search([('id', '=', rec.pound_id.id)]).write({"state": "rejected"})

                Pound_create_user = Model_pound.search_read([('id', '=', rec.pound_id.id)], ["create_uid"])

                Pound_user = self.env["res.users"].search(
                    [("id", "=", (Pound_create_user[0])['id'])]
                )
                users = [Pound_user, rec.create_uid]
                _logger.info("运单退回")
                rec.activity_feedback(['zhongyun_yundan.mail_zhongyun_notice_of_payment'])

                for u in users:
                    _logger.info(u)
                    rec.activity_schedule(
                        'zhongyun_yundan.mail_zhongyun_rejected',
                        user_id=u.id
                    )

    """ 确认退回 """

    def action_confirm_rejected(self):
        _logger.warning('=== 确认退回 ===')
        Model_pound = self.env['zy.pound'].sudo()
        for rec in self:
            if rec.state == 'rejected':
                rec.write({"state": "confirm_rejected"})
                Model_pound.search([('id', '=', rec.pound_id.id)]).write({"state": "confirm_rejected"})
                # 更新 activity
                rec.activity_feedback(['zhongyun_yundan.mail_zhongyun_rejected'])

    """ 批量付款退回 """

    def action_payment_rollback(self):
        _logger.warning('=== 付款退回 ===')
        Model_pound = self.env['zy.pound'].sudo()
        for rec in self:
            if rec.state == 'payment':
                rec.write({"state": "confirm_rejected"})
                Model_pound.search([('id', '=', rec.pound_id.id)]).write({"state": "confirm_rejected"})

    """ 自定义仪表盘数据 """

    @api.model
    def retrieve_dashboard(self):
        """ 此函数返回用于填充自定义仪表板的值
            运单管理视图。
        """
        self.check_access_rights('read')
        result = {
            'all_to_send': 0,
            'all_waiting': 0,
            'all_late': 0,
            'my_to_send': 0,
            'my_waiting': 0,
            'my_late': 0,
            'all_avg_order_value': 0,
            'all_avg_days_to_purchase': 0,
            'all_total_last_7_days': 0,
            'all_sent_rfqs': 0,
            'company_currency_symbol': self.env.company.currency_id.symbol
        }

        # easy counts
        zy = self.env['zy.yundan']
        result['all_to_send'] = zy.search_count([('state', '=', 'to_match')])
        result['my_to_send'] = zy.search_count([('state', '=', 'to_match'), ('create_uid', '=', self.env.uid)])
        result['all_waiting'] = zy.search_count(
            [('state', 'in', ['not_match', 'match', 'to_payment', 'rejected', 'confirm_rejected'])])
        result['my_waiting'] = zy.search_count(
            [('state', 'in', ['not_match', 'match', 'to_payment', 'rejected', 'confirm_rejected']),
             ('create_uid', '=', self.env.uid)])
        result['all_late'] = zy.search_count(
            ['&', ('state', 'in', ['confirm_rejected', 'to_match']), '|',
             ('establish_datetime', '<', fields.Date.context_today(self) - relativedelta(days=3)),
             ('single_supplement_datetime', '<', fields.Date.context_today(self) - relativedelta(days=3))])
        result['my_late'] = zy.search_count(
            ['&', '&', ('state', 'in', ['confirm_rejected', 'to_match']), '|',
             ('establish_datetime', '<', fields.Date.context_today(self) - relativedelta(days=3)),
             ('single_supplement_datetime', '<', fields.Date.context_today(self) - relativedelta(days=3)),
             ('create_uid', '=', self.env.uid)])

        return result

    def unlink_approve(user, rec):
        """检查用户是否可以批准此运价单."""

        # 如果用户属于“管理员”，则可以删除该条记录
        if user.has_group("zhongyun_yundan.zy_yundan_group_manager"):
            return True
        print(rec.create_uid)
        print(rec.state)
        if rec.create_uid == user and rec.state not in ['match', 'to_payment', 'payment', 'rejected',
                                                        'confirm_rejected']:
            return True
        return False

    """ 删除记录设定 """

    def unlink(self):
        """判断用户是否有权删除"""
        for rec in self:
            if self.unlink_approve(self.env.user, rec):
                return super(ZyYundan, self).unlink()
            else:
                raise UserError(
                    _('你的权限不够或【%s】状态下无法修改数据 ') % (
                        rec.state,))


class ZyYunDanUnit(models.Model):
    _name = 'zy.yundan.unit'
    _description = '运单组业务'
    # 继承消息部分
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('运单组编号', index=True, default='新建运单组', readonly=True)

    active = fields.Boolean(default=True, help="Set active.")

    edit_function = fields.Boolean(string='可编辑', compute="_compute_edit_function")

    establish_datetime = fields.Datetime('创建时间', default=lambda self: fields.Datetime.now(), required=True,
                                         readonly=True)

    """ 运价相关字段 """
    yundan_unit_zy_charge_rules = fields.Many2one('zy.charge.rules', string='运价规则', required=True, copy=True)

    yundan_unit_company_id = fields.Many2one(
        "res.company",
        "所属公司",
        help="如果设置，页面只能从该公司访问",
        default=lambda self: self.env.company,
    )

    zy_charge = fields.Many2one('zy.charge', string='运价单', required=True,
                                domain=lambda self: self._zy_charge_function())

    zy_charge_start_datetime = fields.Datetime(related='zy_charge.start_datetime', store=True)
    zy_charge_stop_datetime = fields.Datetime(related='zy_charge.stop_datetime', store=True)

    """ 物料相关字段 """
    yundan_unit_charge_goods_rules = fields.Many2one(string='货物信息',
                                                     related='yundan_unit_zy_charge_rules.charge_goods_rules')

    yundan_unit_zy_goods_price = fields.Many2one('zy.goods.price', string='货物价格', required=True,
                                                 domain=lambda self: self.yundan_unit_zy_goods_price_function())

    yundan_unit_zy_goods_price_start_datetime = fields.Datetime(related='yundan_unit_zy_goods_price.start_datetime',
                                                                store=True)
    yundan_unit_zy_goods_price_stop_datetime = fields.Datetime(related='yundan_unit_zy_goods_price.stop_datetime',
                                                               store=True)

    """ 补单相关字段 """
    replenish_state = fields.Boolean(string='是否补单', default=False)

    single_supplement_datetime = fields.Datetime('补单目标时间', default=lambda self: fields.Datetime.now(), required=True)
    single_supplement_date = fields.Date('补单目标日期', compute="_get_field_compute_single_supplement_date")

    state = fields.Selection(
        [
            ("draft", "待提交"),
            ("to approve", "等待批准"),
            ("approved", "批准"),
            ("cancelled", "取消"),
        ],
        "状态",
        readonly=True,
    )

    """ 补单相关方法 """

    @api.depends('single_supplement_datetime')
    def _get_field_compute_single_supplement_date(self):
        """ 自动将时间字段改成日期字段 """
        for rec in self:
            rec.single_supplement_date = datetime.datetime.strftime((rec.single_supplement_datetime.date()),
                                                                    '%Y-%m-%d')

    """ 运价单触发变更规则 """

    @api.onchange('yundan_unit_zy_charge_rules', 'zy_charge')
    def _onchange_zy_charge(self):

        Model_charge = self.env['zy.charge']
        if self.single_supplement_datetime:
            domain = ['&', ('charge_rules', '=', self.yundan_unit_zy_charge_rules.id), '&', ('state', '=', "approved"),
                      '&',
                      ('start_datetime', '<=', self.single_supplement_datetime), '|',
                      ('stop_datetime', '>', self.single_supplement_datetime), ('stop_datetime', '=', False)]
            res = Model_charge.search(domain, limit=1, order='id DESC')
            _logger.info('运单组运价更新')

            if len(res):
                self.zy_charge = res[0].id

            return {'domain': {'zy_charge': ['&', ('charge_rules', '=', self.yundan_unit_zy_charge_rules.id), '&',
                                             ('state', '=', "approved"), '&',
                                             ('start_datetime', '<=', self.single_supplement_datetime), '|',
                                             ('stop_datetime', '>', self.single_supplement_datetime),
                                             ('stop_datetime', '=', False)]}}
        else:
            domain = ['&', ('charge_rules', '=', self.yundan_unit_zy_charge_rules.id), '&', ('state', '=', "approved"),
                      '&',
                      ('start_datetime', '<=', self.establish_datetime), '|',
                      ('stop_datetime', '>', self.establish_datetime), ('stop_datetime', '=', False)]
            res = Model_charge.search(domain, limit=1, order='id DESC')
            _logger.info('运单组运价更新')

            if len(res):
                self.zy_charge = res[0].id

            return {'domain': {'zy_charge': ['&', ('charge_rules', '=', self.yundan_unit_zy_charge_rules.id), '&',
                                             ('state', '=', "approved"), '&',
                                             ('start_datetime', '<=', self.establish_datetime), '|',
                                             ('stop_datetime', '>', self.establish_datetime),
                                             ('stop_datetime', '=', False)]}}

    """ 货物价格触发变更规则 """

    @api.onchange('yundan_unit_zy_charge_rules')
    def _onchange_yundan_unit_zy_goods_price(self):

        Model_charge = self.env['zy.goods.price']
        if self.single_supplement_datetime:
            domain = ['&', ('goods_rules', '=', self.yundan_unit_charge_goods_rules.id), '&',
                      ('state', '=', "approved"),
                      '&', ('start_datetime', '<=', self.single_supplement_datetime), '|',
                      ('stop_datetime', '>', self.single_supplement_datetime), ('stop_datetime', '=', False)]
            res = Model_charge.search(domain, limit=1, order='id DESC')
            _logger.info('运单组货物价格更新')

            if len(res):
                self.yundan_unit_zy_goods_price = res[0].id

            return {'domain': {
                'yundan_unit_zy_goods_price': ['&', ('goods_rules', '=', self.yundan_unit_charge_goods_rules.id), '&',
                                               ('state', '=', "approved"), '&',
                                               ('start_datetime', '<=', self.single_supplement_datetime), '|',
                                               ('stop_datetime', '>', self.single_supplement_datetime),
                                               ('stop_datetime', '=', False)]}}
        else:
            domain = ['&', ('goods_rules', '=', self.yundan_unit_charge_goods_rules.id), '&',
                      ('state', '=', "approved"),
                      '&', ('start_datetime', '<=', self.establish_datetime), '|',
                      ('stop_datetime', '>', self.establish_datetime), ('stop_datetime', '=', False)]
            res = Model_charge.search(domain, limit=1, order='id DESC')
            _logger.info('运单组货物价格更新')

            if len(res):
                self.yundan_unit_zy_goods_price = res[0].id

            return {'domain': {
                'yundan_unit_zy_goods_price': ['&', ('goods_rules', '=', self.yundan_unit_charge_goods_rules.id), '&',
                                               ('state', '=', "approved"), '&',
                                               ('start_datetime', '<=', self.establish_datetime), '|',
                                               ('stop_datetime', '>', self.establish_datetime),
                                               ('stop_datetime', '=', False)]}}

    yun_dan = fields.One2many(
        'zy.yundan',
        'yundan_unit',
        string='全部运单条数'
    )

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('zy.yundan.unit') or '/'
        vals['name'] = seq
        new_record = super(ZyYunDanUnit, self).create(vals)
        return new_record

    """ 当运价、计量信息、货物价格都未发生变化时运单组可以添加新运单 """

    def _compute_edit_function(self):
        for rec in self:
            Model_charge = self.env['zy.charge']
            Model_goods_price = self.env['zy.goods.price']

            domain_charge_old = ['&', ('charge_rules', '=', rec.yundan_unit_zy_charge_rules.id), '&',
                                 ('state', '=', "approved"), '&', ('start_datetime', '<=', rec.establish_datetime),
                                 '|', ('stop_datetime', '>', rec.establish_datetime), ('stop_datetime', '=', False)]
            domain_chrage_now = ['&', ('charge_rules', '=', rec.yundan_unit_zy_charge_rules.id), '&',
                                 ('state', '=', "approved"), '&', ('start_datetime', '<=', fields.Datetime.now()),
                                 '|', ('stop_datetime', '>', fields.Datetime.now()), ('stop_datetime', '=', False)]

            domain_goods_price_old = ['&', ('goods_rules', '=', rec.yundan_unit_charge_goods_rules.id), '&',
                                      ('state', '=', "approved"), '&',
                                      ('start_datetime', '<=', rec.establish_datetime), '|',
                                      ('stop_datetime', '>', rec.establish_datetime), ('stop_datetime', '=', False)]
            domain_goods_price_now = ['&', ('goods_rules', '=', rec.yundan_unit_charge_goods_rules.id), '&',
                                      ('state', '=', "approved"), '&',
                                      ('start_datetime', '<=', fields.Datetime.now()), '|',
                                      ('stop_datetime', '>', fields.Datetime.now()), ('stop_datetime', '=', False)]

            res_chrage_old = Model_charge.search(domain_charge_old, limit=1, order='id DESC')
            res_chrage_new = Model_charge.search(domain_chrage_now, limit=1, order='id DESC')

            res_goods_price_old = Model_goods_price.search(domain_goods_price_old, limit=1, order='id DESC')
            res_goods_price_now = Model_goods_price.search(domain_goods_price_now, limit=1, order='id DESC')

            _logger.info("res_chrage_old res_chrage_new 验证")
            _logger.info(res_chrage_old)
            _logger.info(res_chrage_new)

            if (res_chrage_old == res_chrage_new) and (
                    res_goods_price_old == res_goods_price_now):
                rec.edit_function = True
            else:
                rec.edit_function = False

    """ 运价单domain """

    def _zy_charge_function(self):
        domain = ['&', ('charge_rules', '=', self.yundan_unit_zy_charge_rules.id), '&', ('state', '=', "approved"), '&',
                  ('start_datetime', '<=', self.establish_datetime), '|',
                  ('stop_datetime', '>', self.establish_datetime), ('stop_datetime', '=', False)]
        return domain

    """ 货物价格domain """

    def yundan_unit_zy_goods_price_function(self):
        domain = ['&', ('goods_rules', '=', self.yundan_unit_charge_goods_rules.id), '&', ('state', '=', "approved"),
                  '&', ('start_datetime', '<=', self.establish_datetime), '|',
                  ('stop_datetime', '>', self.establish_datetime), ('stop_datetime', '=', False)]
        return domain

    def name_get(self):
        result = []
        for rec in self:
            name = '[' + rec.name + ']' + ' ' + str(rec.yundan_unit_zy_charge_rules.name)
            result.append((rec.id, name))
        return result

    @api.model
    def get_form_id(self):
        form_id_val = self.env.ref('zhongyun_yundan.view_form_zy_yundan_unit_replenish').id
        _logger.info(form_id_val)
        return form_id_val

    # 列表按钮
    def button_line_ids(self):
        return {
            'name': '运单',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'zy.yundan',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('yundan_unit', '=', self.id)],
        }

    # 补单按钮
    def button_replenish(self):
        form_id = self.env.ref('zhongyun_yundan.view_form_zy_yundan_unit').id
        data = {'default_replenish_state': True}
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            "view_mode": "form",
            'res_id': False,
            'res_model': 'zy.yundan.unit',
            'name': '补单组',
            'context': data,
            "mode": 'edit',
            'views': [[form_id, 'form']],
        }

    @api.model
    def add_kanban_button(self):
        form_id = self.env.ref('zhongyun_yundan.view_form_zy_yundan_unit').id
        return {'data': {'id': form_id}}


class ZyVehicleChild(models.Model):
    _inherit = 'zy.vehicle'

    yundan_ids = fields.One2many('zy.yundan', 'car_id', string="运单号")
