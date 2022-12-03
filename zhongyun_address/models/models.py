from email.policy import default
from operator import index
import odoo.modules
import logging
import datetime
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


def test_fun():
    print("test")


class ZyAddress(models.Model):
    # 中运物流地址维护
    _name = 'zy.address'
    _description = 'Address maintenance'

    # 字段 发货地点 必填项
    sequence = fields.Char(string='编号', readonly=True, index=True, default='新建地址')

    # 发货地点
    name = fields.Char('发货地点', required=True , copy=True)

    # 字段 运输单位
    transport_company = fields.Many2one('res.company',  string='运输单位', required=True , copy=True)

    # 字段 供应商
    supplier = fields.Char('发货人（供应商）', required=True , copy=True)

    # 起运地
    port_state = fields.Many2one('res.country.state' , string='省', required=True , domain=[('country_id', '=', 48)] , copy=True)
    port_city = fields.Many2one('res.cn.city', string='市' , required=True, copy=True)
    port_area = fields.Many2one('res.area', string='县/区' , required=True, copy=True)

    # 止运地
    stop_state = fields.Many2one('res.country.state' , string='省' , required=True , domain=[('country_id', '=', 48)] , copy=True)
    stop_city = fields.Many2one('res.cn.city', string='市' , required=True , copy=True)
    stop_area =fields.Many2one('res.area', string='县/区', required=True , copy=True)

    # 备注
    remarke = fields.Text(string='备注')

    def name_get(self):
        """本方法用于自定义记录的显示名称"""
        result = []
        for record in self:
            rec_name = "%s (%s)" % (record.sequence,record.name)
            result.append((record.id, rec_name))
        return result


    # 起运地三级联动
    @api.onchange('port_state')
    def _onchange_port_state(self):
        # 作用是当改变省时，清空市和区
        self.port_city = False
        self.port_area = False
        if self.port_state:
            print ("启运地省id: %s" , self.port_state.id)
            return {'domain': {'port_city': [('state_id', '=', self.port_state.id)]}}
        else:
            return {'domain': {'port_city': []}}

    @api.onchange('port_city')
    def _onchange_port_city(self):
        self.port_area = False
        if self.port_city:
            print ("启运地市id: %s" , self.port_city.id)
            return {'domain': {'port_area': [('city_id', '=', self.port_city.id)]}}
        else:
            return {'domain': {'port_area': []}}


    # 止运地三级联动
    @api.onchange('stop_state')
    def _onchange_stop_state(self):
        # 作用是当改变省时，清空市和区
        self.stop_city = False
        self.stop_area = False
        print ("止运地省id: %s" , self.stop_state.id)
        if self.stop_state:
            return {'domain': {'stop_city': [('state_id', '=', self.stop_state.id)]}}
        else:
            return {'domain': {'stop_city': []}}

    @api.onchange('stop_city')
    def _onchange_stop_city(self):
        self.stop_area = False
        print ("止运地市id: %s" , self.stop_city.id)
        if self.stop_city:
            return {'domain': {'stop_area': [('city_id', '=', self.stop_city.id)]}}
        else:
            return {'domain': {'stop_area': []}}

    @api.model
    def create(self, vals):
        # file = self._file_lock()
        sn_prefix = 'SNZA' + datetime.date.today().strftime("%y%m%d")
        obj = self.env['zy.address'].search_read([('sequence', '=like', sn_prefix + '%')], limit=1,
                                                 order='sequence DESC')
        # 今天已经有序列号，在最新的序列号上递增
        if obj and obj[0]['sequence'].startswith(sn_prefix):
            sn_suffix = int(obj[0]['sequence'][-3:]) + 1
            vals['sequence'] = sn_prefix + str(sn_suffix).zfill(3)  # 补0
        else:
            vals['sequence'] = sn_prefix + '001'

        res = super(ZyAddress, self).create(vals)
        # 关闭文件将自动解锁
        # file.close()
        return res


