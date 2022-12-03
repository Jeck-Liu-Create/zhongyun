
from datetime import datetime
from email.policy import default
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class ZyChargerules(models.Model):
    _name = "zy.charge.rules"
    _inherit = ["zy.charge.rules","mail.thread"]

    approver_gid = fields.Many2one(
        "res.groups",
        "审批者组",
        help="用户还必须属于审批者组",
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
        help="可以批准添加运价单的组",
    )

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
        if not user.has_group("zhongyun_charge_approval.group_charge_approver_user"):
            return False
        # 如果没有任何approver_groups_defined，则用户可以进行审批
        if not self.approver_group_ids:
            return True
        # 要进行审批，用户必须属于任何审批者组
        return len(user.groups_id & self.approver_group_ids) > 0

class ZyCharge(models.Model):
    """ 用于运价单的批准工作流 """
    _name = "zy.charge"
    _inherit = ["zy.charge","mail.thread"]

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
                raise UserError(_("你需要在重新打开前取消"))
            if not (rec.am_i_owner or rec.am_i_approver ):
                raise UserError(
                    _(
                        "你没有权限这样做.\r\n"
                        "只有所有者或批准者才能重新打开变更请求."
                    )
                )
            rec.write({"state": "draft"})

    def action_to_approve(self):
        """ 将运价单请求设置为待批准 """
        template = self.env.ref(
            "zhongyun_charge_approval.email_template_new_draft_need_approval"
        )
        approver_gid = self.env.ref(
            "zhongyun_charge_approval.group_charge_approver_user"
        )
        for rec in self:
            if rec.state != "draft":
                raise UserError(_(" 在'%s'状态下无法进入审批界面 .") % rec.state)
            if not (rec.am_i_owner or rec.am_i_approver):
                raise UserError(
                    _(
                        "你没有权限这样做.\r\n"
                        "只有所有者或批准者才能重新打开变更请求."
                    )
                )
            # 进入请求批准状态 request approval 
            if rec.is_approval_required:
                rec.write({"state": "to approve"})
                guids = [g.id for g in rec.charge_rules.approver_group_ids]
                users = self.env["res.users"].search(
                    [("groups_id", "in", guids), ("groups_id", "in", approver_gid.id)]
                )
                rec.message_subscribe([u.id for u in users])
                rec.message_post_with_template(template.id)
            else:
                # 如果不需要批准，则自动批准
                # rec.action_approve()
                print("自动批准")

    def action_approve(self):
        """ 将运价单设置为已批准 """
        for rec in self:
            if rec.state not in ["draft", "to approve"]:
                raise UserError(_("在'%s'状态下无法被批准.") % rec.state)
            if not rec.am_i_approver:
                raise UserError(
                    _(
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
                body=_("运价单已经被%s批准.")
                % (self.env.user.name),
            )
            # 通知关注者运价单可用
            rec.charge_rules.message_post(
                subtype_xmlid="mail.mt_comment",
                body=_("新的运价单在%s规则中生效 .") % (rec.charge_rules.name),
            )

    def action_cancel(self):
        """ 将更改请求设置为取消 """
        self.write({"state": "cancelled"})
        for rec in self:
            rec.message_post(
                subtype_xmlid="mail.mt_comment",
                body=_("变更请求 <b>%s</b> 已被取消 %s.")
                % (rec.display_name, self.env.user.name),
            )

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
            if ((rec.start_datetime > datetime.now()) or (rec.start_datetime == datetime.now())):
                data_charge = self.env['zy.charge'].search_read(['&',('charge_rules', '=', rec.charge_rules.id),('state', '=' , 'approved')], limit=1, order='id DESC')
                _logger.info("上一笔审批通过的运单：\n")
                _logger.info(data_charge)
                if len(data_charge) > 0:
                    if data_charge[0]['start_datetime'] <= rec.start_datetime:
                        _logger.info("上一笔运价单启用时间小于等于当前启用时间\n")
                        data_id = data_charge[0]['id']
                        _logger.info(type(data_id))
                        data_info = self.env['zy.charge'].search([('id','=', str(data_id))])
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
                        data_info = self.env['zy.charge'].search([('id','=', str(data_id))])
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