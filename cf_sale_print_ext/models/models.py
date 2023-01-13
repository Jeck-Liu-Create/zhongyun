# -*- coding: utf-8 -*-
# 康虎软件工作室
# http://www.khcloud.net
# QQ: 360026606
# wechat: 360026606
# -------------------------


from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare


class SaleOrder(models.Model):
    """
    康虎云报表免写代码报表打印后回调函数示例
    """
    _inherit = "sale.order"

    print_count = fields.Integer(string='打印次数', default=0, help='记录该记录的打印次数')

    def after_print_cf(self, ids=[]):
        """
        打印后回调函数，康虎云报表模块在生成打印数据后会调用该方法

        @param ids : 打印记录的ID
        """
        # 在这里执行打印后逻辑，例如更新打印次数
        if len(ids)>0:
            docs = self.search([('id', 'in', ids)])
            for doc in docs:
                doc.update({'print_count': doc.print_count + 1})


