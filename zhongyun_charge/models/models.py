from email.policy import default
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import datetime
import logging

_logger = logging.getLogger(__name__)


class ZyCharge(models.Model):
    _name = 'zy.charge'
    _description = '运价单'
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _order = "id desc"

    state = fields.Selection(
        [
            ("draft", "待提交"),
            ("to approve", "等待批准"),
            ("approved", "批准"),
            ("cancelled", "取消"),
        ],
        "状态",
        default="draft",
        readonly=True,
    )
    company_id = fields.Many2one(
        "res.company",
        "所属公司",
        help="如果设置，页面只能从该公司访问",
        related="charge_rules.company_id",
        store=True,
        index=True,
        readonly=True,
        ondelete="cascade",
        # default=lambda self: self.env.company,

    )

    # 启用日期,截止日期
    start_datetime = fields.Datetime('启用时间', default=lambda self: datetime.datetime.now(), required=True)
    stop_datetime = fields.Datetime('截止时间')

    name = fields.Char('运价单编号', index=True, default='新建运价单', readonly=True)

    # employee_id = fields.Many2one('hr.employee', string="业务员", required=True)

    # user_id = fields.Many2one('res.users', default=lambda self: self.env.user , string='用户', readonly=True)

    charge_rules = fields.Many2one('zy.charge.rules', string="运价规则", required=True)

    currency_id = fields.Many2one('res.currency', "货币", readonly=True, default=7)

    transport_price = fields.Monetary(string='运输价格')

    address_name = fields.Many2one(string='发货地址', related='charge_rules.address_name', store=True)

    active = fields.Boolean(default=True, help="Set active.")

    def button_charge_id(self):
        return {
            'view_mode': 'form',
            'res_model': 'zy.charge.rules',
            'res_id': self.charge_rules.id,
            'type': 'ir.actions.act_window'
        }

    # 启用日期不能小于创建日期
    @api.constrains('start_datetime', 'create_date')
    def _check_date(self):
        for data in self:
            if data.start_datetime < data.create_date:
                raise ValidationError(
                    "启用日期不能小于创建日期"
                )

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('zy.charge.sequence')
        vals['name'] = seq
        new_record = super(ZyCharge, self).create(vals)
        return new_record

    def name_get(self):
        result = []

        for rec in self:
            name = '[' + rec.name + ']' + ' ' + '¥' + ' ' + str(rec.transport_price)
            result.append((rec.id, name))
        return result

    # --------------------------------------------
    # Approved
    # --------------------------------------------

    approved_date = fields.Datetime("批准日期")

    approved_uid = fields.Many2one("res.users", "批准人")

    approver_gid = fields.Many2one(
        related="charge_rules.approver_gid",
        help="用户还必须属于审批者组"
    )

    """ 运价单是否需要批准 """
    is_approval_required = fields.Boolean(
        related="charge_rules.is_approval_required", string="是否需要请求批准"
    )

    """ 判断用户是否为所有者 """
    am_i_owner = fields.Boolean(compute="_compute_am_i_owner")

    """ 判断用户是否有审批权限 """
    am_i_approver = fields.Boolean(related="charge_rules.am_i_approver", related_sudo=False)

    def action_draft(self):
        """ 运价单增加请求设置为待提交 """
        for rec in self:
            if not rec.state == "cancelled":
                raise UserError(("你需要在重新打开前取消"))
            if not (rec.am_i_owner or rec.am_i_approver):
                raise UserError(
                    (
                        "你没有权限这样做.\r\n"
                        "只有所有者或批准者才能重新打开变更请求."
                    )
                )
            rec.write({"state": "draft"})
            self.activity_unlink(['zhongyun_charge.mail_zhongyun_approval'])

    def action_to_approve(self):
        """ 将运价单请求设置为待批准 """
        template = self.env.ref(
            "zhongyun_charge.email_template_new_draft_need_approval"
        )
        approver_gid = self.env.ref(
            "zhongyun_charge.group_charge_approver_user"
        )
        for rec in self:
            if rec.state != "draft":
                raise UserError((" 在'%s'状态下无法进入审批界面 .") % rec.state)
            if not (rec.am_i_owner or rec.am_i_approver):
                raise UserError(
                    (
                        "你没有权限这样做.\r\n"
                        "只有所有者或批准者才能重新打开变更请求."
                    )
                )
            # 进入请求批准状态 request approval 
            if rec.is_approval_required:
                rec.write({"state": "to approve"})
                guids = [g.id for g in rec.charge_rules.approver_group_ids]

                _logger.info(rec.charge_rules.approver_group_ids.id)

                users = self.env["res.users"].search(
                    [("groups_id", "in", approver_gid.id)]
                )
                _logger.info("设置待批准")

                for u in users:
                    self.activity_schedule(
                        'zhongyun_charge.mail_zhongyun_approval',
                        user_id=u.id
                    )

                _logger.info([u.id for u in users])

                rec.message_subscribe([u.id for u in users])
                _logger.info('message_subscribe')
                rec.message_post_with_template(template.id)
                _logger.info('message_post_with_template')
            else:
                # 如果不需要批准，则自动批准
                # rec.action_approve()
                print("自动批准")

    def action_approve(self):
        """ 将运价单设置为已批准 """
        for rec in self:
            if rec.state not in ["draft", "to approve"]:
                raise UserError(("在'%s'状态下无法被批准.") % rec.state)
            if not rec.am_i_approver:
                raise UserError(
                    (
                        "你无权这样做.\r\n"
                        "只有具有这些组的审批者才能批准此操作: "
                    )
                    % ", ".join(
                        [g.display_name for g in rec.charge_rules.approver_group_ids]
                    )
                )
            # 修改之前运价单的截止时间为新运价单的启用时间    
            self.change_after_stopdatetime()

            # 更新状态
            rec.write(
                {
                    "state": "approved",
                    "approved_date": fields.Datetime.now(),
                    "approved_uid": self.env.uid,
                }
            )
            # 触发计算字段更新
            # rec.charge_rules._compute_history_head()
            # 通知状态变化
            rec.message_post(
                subtype_xmlid="mail.mt_comment",
                body=("运价单已经被%s批准.")
                     % (self.env.user.name)
            )
            # 通知关注者运价单可用
            rec.charge_rules.message_post(
                subtype_xmlid="mail.mt_comment",
                body=("新的运价单在%s规则中生效 .") % (rec.charge_rules.name),
            )
            # 更新 activity
            self.activity_feedback(['zhongyun_charge.mail_zhongyun_approval'])

    def action_cancel(self):
        """ 将更改请求设置为取消 """
        for rec in self:
            if rec.state in ["approved"] and not rec.am_i_approver:
                raise UserError(("在'%s'状态下无法取消.") % rec.state)
            else:
                self.write({"state": "cancelled"})

                rec.message_post(
                    subtype_xmlid="mail.mt_comment",
                    body=("变更请求 <b>%s</b> 已被取消 %s.")
                         % (rec.display_name, self.env.user.name))

                self.activity_unlink(['zhongyun_charge.mail_zhongyun_approval'])

    def action_cancel_and_draft(self):
        """ 将变更请求设置为待提交,首先取消它 """
        self.action_cancel()
        self.action_draft()

    def _compute_am_i_owner(self):
        """ 检查当前用户是否为该用户的所有者 """
        for rec in self:
            rec.am_i_owner = rec.create_uid == self.env.user

    def change_after_stopdatetime(self):
        """ 当最新的运价单审批通过后,上一笔运价单截止日期修改为,该笔运价单的启用日期 """
        for rec in self:
            _logger.info(rec.charge_rules)
            if ((rec.start_datetime > fields.Datetime.now()) or (rec.start_datetime == fields.Datetime.now())):
                data_charge = self.env['zy.charge'].search_read(
                    ['&', ('charge_rules', '=', rec.charge_rules.id), ('state', '=', 'approved')], limit=1,
                    order='id DESC')
                _logger.info("上一笔审批通过的运单：\n")
                # _logger.info(data_charge)
                if len(data_charge) > 0:
                    if data_charge[0]['start_datetime'] <= rec.start_datetime:
                        _logger.info("上一笔运价单启用时间小于等于当前启用时间\n")
                        data_id = data_charge[0]['id']
                        _logger.info(type(data_id))
                        data_info = self.env['zy.charge'].search([('id', '=', str(data_id))])
                        _logger.info(type(data_info))

                        info = {
                            'stop_datetime': rec['start_datetime']
                        }

                        data_info.write(info)
                        _logger.info('成功修改上一笔运价单的停止时间')

                    elif data_charge[0]['start_datetime'] > rec.start_datetime:
                        _logger.info("上一笔运价单启用时间大于当前启用时间\n")
                        """ 是否使用当前运价替换上一笔运价单 """
                        data_id = data_charge[0]['id']
                        _logger.info(type(data_id))
                        data_info = self.env['zy.charge'].search([('id', '=', str(data_id))])
                        _logger.info(type(data_info))

                        info = {
                            'state': 'cancelled'
                        }

                        data_info.write(info)
                        """" 再次执行 """
                        self.change_after_stopdatetime()

                else:
                    _logger.info('之前没有运价单')
            else:
                _logger.info("启用时间小于当前时间\n")
                raise ValidationError("启用时间不应该小于当前日期.")


class ZyChargeRules(models.Model):
    _name = 'zy.charge.rules'
    _description = '运价规则'
    _inherit = ["mail.thread"]

    name = fields.Char('运价规则', required=True)

    company_id = fields.Many2one(
        "res.company",
        "所属公司",
        help="如果设置，页面只能从该公司访问",
        index=True,
        ondelete="cascade",
        default=lambda self: self.env.company,
    )

    available_uid = fields.Many2many("res.users", string='可选用户')

    # 一下部分继承自 中运物流-地址模块
    address_name = fields.Many2one('zy.address', string='发货地址')
    transport_company_rules = fields.Many2one(string='运输单位', related='address_name.transport_company', store=True,
                                              readonly=True)
    supplier = fields.Char(string='供应商', related='address_name.supplier', store=True, readonly=True)

    charge_goods_rules = fields.Many2one('zy.goods', string='物料信息', required=True)
    charge_buckle_rules = fields.Many2one('zy.buckle.rules', string='计量规则', required=True)

    port_state = fields.Many2one(string='省', related='address_name.port_state', store=True, readonly=True)
    port_city = fields.Many2one(string='市', related='address_name.port_city', store=True, readonly=True)
    port_area = fields.Many2one(string='县/区', related='address_name.port_area', store=True, readonly=True)

    stop_state = fields.Many2one(string='省', related='address_name.stop_state', store=True, readonly=True)
    stop_city = fields.Many2one(string='市', related='address_name.stop_city', store=True, readonly=True)
    stop_area = fields.Many2one(string='县/区', related='address_name.stop_area', store=True, readonly=True)

    remarke = fields.Text(string='备注')

    rule_line_now_ids = fields.One2many(
        'zy.charge',  # related model
        'charge_rules',  # field for "this" on related model
        domain=lambda self: self._domain_zy_charge_now_id(),
        string='可用运价单',
        store=True,
        readonly=True
    )

    def _domain_zy_charge_now_id(self):
        domain = ['&', ('state', '=', "approved"), '&', (('start_datetime'), '<=', fields.Datetime.now()), '|',
                  ('stop_datetime', '>', fields.Datetime.now()), ('stop_datetime', '=', False)]
        return domain

    rule_line_all_ids = fields.One2many(
        'zy.charge',  # related model
        'charge_rules',  # field for "this" on related model
        string='全部运价单条数',
        store=True,
        readonly=True
    )

    approver_gid = fields.Many2one(
        "res.groups",
        "审批者组",
        help="用户还必须属于审批者组",
        default=lambda self: self.env.ref("zhongyun_charge.group_charge_approver_user")
    )

    # 为运价规则增加是否需要批准选项
    is_approval_required = fields.Boolean(
        "批准要求",
        help="如果为真，则此页面的运价单需要批准",
        default=True
    )

    # 验证是否拥有对该物流规则下，运价单批准权力
    am_i_approver = fields.Boolean(compute="_compute_am_i_approver")

    # 批准用户组
    approver_group_ids = fields.Many2many(
        "res.groups",
        string="审批用户组",
        help="可以批准添加运价单的组"
    )

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'name must be unique'),
    ]

    # 列表按钮
    def button_line_ids(self):
        return {
            'name': '运价单',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'zy.charge',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('charge_rules', '=', self.id)],
        }

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        domain = args + ['|', ('id', operator, name), ('name', operator, name)]
        return self._search(domain, limit=limit)

    # --------------------------------------------
    # Approved
    # --------------------------------------------
    @api.depends("is_approval_required", "approver_group_ids")
    def _compute_am_i_approver(self):
        """检查当前用户是否可以批准对该运价单的更改."""
        for rec in self:
            rec.am_i_approver = rec.can_user_approve_this_charge(self.env.user)

    def can_user_approve_this_charge(self, user):
        """检查用户是否可以批准此运价单."""
        self.ensure_one()
        # 如果不需要，任何人都可以批准
        if not self.is_approval_required:
            return True
        # 如果用户属于“审批人/管理员”，他可以批准任何事情
        if user.has_group("zhongyun_charge.zhongyun_charge_manager"):
            return True
        # 审批时，用户必须具有审批人权限
        if not user.has_group("zhongyun_charge.group_charge_approver_user"):
            return False
        # 如果没有任何approver_groups_defined，则用户可以进行审批
        if not self.approver_group_ids:
            return True
        # 要进行审批，用户必须属于任何审批者组
        return len(user.groups_id & self.approver_group_ids) > 0
