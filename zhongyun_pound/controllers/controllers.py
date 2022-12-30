# -*- coding: utf-8 -*-
import datetime
import io
import json
import operator
import re

from odoo import http, exceptions
from odoo.tools import pycompat
from odoo.tools.misc import xlsxwriter
from odoo.tools.translate import _
from odoo.exceptions import UserError
from odoo.http import serialize_exception, request
from odoo.addons.web.controllers.main import ExportFormat, ExportXlsxWriter, GroupExportXlsxWriter, content_disposition


# class AC_ExportXlsxWriter(ExportXlsxWriter):
#     def __init__(self, field_names, row_count=0, listType=None):
#         self.listType = listType
#         self.field_names = field_names
#         self.output = io.BytesIO()
#         self.workbook = xlsxwriter.Workbook(self.output, {'in_memory': True})
#         self.base_style = self.workbook.add_format({'text_wrap': True})
#         self.base_style.set_font_size(10)
#         self.header_style = self.workbook.add_format({'bold': True})
#         self.header_style.set_align('center')
#         self.header_style.set_font_size(10)
#         self.header_bold_style = self.workbook.add_format({'text_wrap': True,
#                                                            'bold': True,
#                                                            'bg_color': '#e9ecef'})
#         self.header_bold_style.set_font_size(10)
#         self.date_style = self.workbook.add_format({'text_wrap': True,
#                                                     'num_format': 'yyyy-mm-dd'})
#         self.date_style.set_font_size(10)
#         self.datetime_style = self.workbook.add_format(
#             {'text_wrap': True, 'num_format': 'yyyy-mm-dd hh:mm:ss'})
#         self.datetime_style.set_font_size(10)
#         self.worksheet = self.workbook.add_worksheet()
#         self.value = False
#
#         if row_count > self.worksheet.xls_rowmax:
#             raise UserError(_('导出的行数过多 (%s 行, 上限为: %s 行) , 请分多次导出') %
#                             (row_count, self.worksheet.xls_rowmax))
#
#     def write_header(self):
#         for i, fieldname in enumerate(self.field_names):
#             self.write(0, i, fieldname, self.header_style)
#             self.worksheet.set_column(i, i, self.setColumnWidth(fieldname))
#
#     def setColumnWidth(self, fieldname):
#         return AC_ExcelExport.widths.get(fieldname, AC_ExcelExport.default_widths)
#
#
# # 导出模板
# class AC_ExcelExport(ExportFormat, http.Controller):
#     raw_data = True
#     default_widths = 30
#     widths = {"策略号": 6,
#               "贷方金额": 10,
#               "分录摘要": 30,
#               "附件张数": 7,
#               "机构/主体": 28,
#               "机构/主体编码": 10,
#               "机构/主体名称": 25,
#               "核算类别": 20,
#               "核算统计项目": 30,
#               "核算项目编码": 12,
#               "核算项目类别": 11,
#               "核算项目名称": 30,
#               "会计科目": 30,
#               "记账日期": 10,
#               "借方金额": 10,
#               "科目编码": 8,
#               "科目类别": 12,
#               "科目名称": 30,
#               "末级科目": 7,
#               "凭证的标签": 8,
#               "凭证号": 6,
#               "凭证来源": 7,
#               "凭证中可选": 8,
#               "全局标签": 30,
#               "审核人": 12,
#               "所属机构/主体": 30,
#               "所属科目体系": 15,
#               "所属凭证": 9,
#               "唯一号": 9,
#               "现金流量": 37,
#               "业务日期": 10,
#               "余额方向": 7,
#               "制单人": 12,
#               "创建日期": 10,
#               "期初借方": 10,
#               "期初贷方": 10,
#               "本期借方金额": 10,
#               "本期贷方金额": 10,
#               "月初本年借方累计": 10,
#               "月初本年贷方累计": 10,
#               "作为明细科目的类别": 10,
#               "统计项目": 30,
#               "会计科目和核算统计项目": 40,
#               "业务标识": 10,
#               '计量参考': 10,
#               '业务行标识': 12,
#               '外币币别': 7,
#               '汇率': 5,
#               '外币金额': 10,
#               '本币金额': 10,
#               '币别': 5,
#               '业务链接': 10}
#
#
#     def ac_index_base(self, listType, file_name):
#         ''''自定义直接下载'''
#         # 表头
#         columns_headers = listType.get_colums_headers(fields=[])
#         self.column_count = len(columns_headers)
#         # 表体
#         export_data = listType.get_export_data([])
#         self.row_count = len(export_data)
#         response_data = self.from_data(columns_headers, export_data, listType)
#         return request.make_response(response_data,
#                                      headers=[('Content-Disposition',
#                                                content_disposition(self.filename(file_name))),
#                                               ('Content-Type', self.content_type)],
#                                      cookies={'fileToken': ""})
#
#     @property
#     def content_type(self):
#         return 'application/vnd.ms-excel'
#
#     def filename(self, base):
#         return base + '.xlsx'
#
#     def from_data(self, fields, rows, listType):
#         with AC_ExportXlsxWriter(fields, len(rows), listType) as xlsx_writer:
#             for row_index, row in enumerate(rows):
#                 for cell_index, cell_value in enumerate(row):
#                     xlsx_writer.write_cell(
#                         row_index + 1, cell_index, cell_value)
#         return xlsx_writer.value
#
#     @http.route('/web/export/accountcore.import_vouchers_model', type='http', auth="user")
#     def accountcore_import_vouchers_model(self, data='{}', token=""):
#         # listType = ExcelExportVoucherModel()
#         # return self.ac_index_base(listType, '本币凭证导入模板')
#         return 0
#
# class ExcelExportVoucherModel():
#
#     def get_colums_headers(self, fields):
#         columns_headers = ['记账日期',
#                            '机构/主体',
#                            '分录摘要',
#                            '科目编码',
#                            '会计科目',
#                            '核算项目类别',
#                            '核算项目名称',
#                            '统计项目',
#                            '业务项目',
#                            '借方金额',
#                            '贷方金额',
#                            '现金流量项目',
#                            '附件张数',
#                            '业务日期',
#                            '凭证号',
#                            '所属凭证',
#                            '分录全局标签',
#                            '凭证全局标签',
#                            '凭证的标签',
#                            '业务行标识',
#                            '计量参考',
#                            '外币币别',
#                            '汇率',
#                            '外币金额',
#                            '制单人',
#                            '审核人']
#         return columns_headers
#
#     def get_export_data(self, records):
#         export_data = [['2021-03-24', 'test', '报销费用', '6602', '管理费用', '成本费用', '差旅费', '员工:黄虎', '往来:重庆算盘有限公司', 67, 0,
#                         '-支付给职工以及为职工支付的现金', '1', '2021-03-01', '1', 'V00010740', '', '关联交易/凭证全局标签1', '', '业务行标识123456',
#                         99, '美元', 6.7, 10, '李会计', 'Admonistrator'],
#                        ['2021-03-24', 'test', '报销费用', '1001.10', '库存现金---现金', '', '', '', '', 0, 67, '', '1',
#                         '2021-03-01', '1', 'V00010740', '', '关联交易/凭证全局标签1', '', '', '', '', 6.7, '', '李会计',
#                         'Admonistrator'],
#                        ['2021-03-31', 'test', '结转损益', '6602', '管理费用', '成本费用', '差旅费', '员工:黄虎', '', 0, 67, '', '1', '',
#                         '2', 'V00010741', '', '', '结转损益', '', '', '美元', 6.7, '', '李会计', 'Admonistrator'],
#                        ['2021-03-31', 'test', '结转损益', '4103', '本年利润', '', '', '', '', 67, 0, '', '1', '', '2',
#                         'V00010741', '', '', '结转损益', '', '', '美元', 6.7, '', '李会计', 'Admonistrator']]
#         return export_data
