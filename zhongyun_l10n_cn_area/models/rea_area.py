import string
from odoo import api, models, fields

class ResCnCity(models.Model):
    _name = 'res.cn.city'
    _inherit = 'res.city'
    _description = 'chain in city'

class ResArea(models.Model):
    _name = 'res.area'
    _description = 'area in city'
    # 继承消息部分
    _inherit = ['mail.thread', 'mail.activity.mixin'] # track_visibility

    name = fields.Char(string='县/区名称', index=True)
    zipcode = fields.Char(string='区域代码')
    country_id = fields.Many2one('res.country', string='国家ID')
    state_id = fields.Many2one('res.country.state' ,string='省级行政单位ID')
    city_id = fields.Many2one('res.cn.city' ,string='地级行政单位ID')

    _sql_constraints = [
        ('zipcode_uniq', 'unique(zipcode)', 'Description must be unique'),
    ]