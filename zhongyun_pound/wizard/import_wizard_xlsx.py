import base64
import os.path

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo import exceptions
import time
import datetime

import logging

try:
    import xlrd

    try:
        from xlrd import xlsx
    except ImportError:
        xlsx = None
except ImportError:
    xlrd = xlsx = None

_logger = logging.getLogger(__name__)


def _str2float(data):
    """金额单元格转换成数字"""
    try:
        return float(data)
    except Exception:
        pass
        return 0


class ImportXlsxPound(models.TransientModel):
    _name = "zy.pound.import"
    _description = "磅单导入"

    data = fields.Binary('文件', required=True, attachment=False)
    filename = fields.Char('文件名称', required=True)
    unit_id = fields.Many2one('zy.pound.unit', string='运单组')
    result = fields.Html(string='导入结果', default="")

    def _read_xlsx_book(self, book):
        sheet = book.sheet_by_index(0)
        for rowx, row in enumerate(map(sheet.row, range(sheet.nrows)), 1):
            values = []
            for colx, cell in enumerate(row, 1):
                values.append(cell.value)
            if any(x for x in values if x.strip()):
                yield values

    def process_row(self, row):

        name_data = row[0].value,
        pound_supplier_data = row[1].value,
        transport_goods_data = row[2].value,
        transport_goods_specification_data = row[3].value,

        car_id_data = self._getModelId((row[4].value, 'zy.vehicle'))
        _manufacture_date = row[5].value
        if row[5].ctype == 3:
            _manufacture_date_tuple = self._getTupleDate(_manufacture_date)
        elif row[5].ctype == 1:
            _manufacture_date_tuple = self._get_createdate_tuple(row[5].value)
        manufacture_date_data = datetime.datetime(*_manufacture_date_tuple)

        _delivery_date = row[6].value
        if row[6].ctype == 3:
            _delivery_date_tuple = self._getTupleDate(_delivery_date)
        elif row[6].ctype == 1:
            _delivery_date_tuple = self._get_createdate_tuple(row[6].value)
        delivery_date_data = datetime.datetime(*_delivery_date_tuple)

        car_number_data = row[7].value,
        net_weight_data = _str2float(row[8].value),
        primary_weight_data = _str2float(row[9].value),

        transport_company_data = self._getModelId((row[10].value, 'res.company'))

        delivery_location_data = self._getAddressId(row[11].value, row[1].value)

        car_id_other_data = self._getModelId((row[12].value, 'zy.vehicle'))

        tram_carrier_unit_data = row[13].value

        create_data = {
            'name': name_data[0],
            'pound_id': self.unit_id.id,
            'pound_supplier': pound_supplier_data[0],
            'transport_goods': transport_goods_data[0],
            'transport_goods_specification': transport_goods_specification_data[0],
            'car_id': car_id_data,
            'manufacture_date': manufacture_date_data,
            'delivery_date': delivery_date_data,
            'car_number': car_number_data[0],
            'net_weight': net_weight_data[0],
            'primary_weight': primary_weight_data[0],
            'transport_company': transport_company_data,
            'delivery_location': delivery_location_data,
            'car_id_other': car_id_other_data,
            'tram_carrier_unit': tram_carrier_unit_data
        }

        self.env['zy.pound'].sudo().create(create_data)

    def import_pound(self):
        action = {
            'name': '导入结果',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'zy.pound.import',
            'res_id': self.id}
        this = self[0]
        self.result = ""
        if not self.data:
            self.result = "<div><span class='text-danger fa fa-close'></span><kbd>没有选择excel文件</kbd></div>"
            return action
        try:
            fileformat = os.path.splitext(this.filename)[-1][1:].lower()
            if fileformat != 'xlsx':
                raise Exception(_('Bad file format:%s') % fileformat)

            book = xlrd.open_workbook(file_contents=base64.decodebytes(this.data))
            sh = book.sheet_by_index(0)

            # 检查表头
            head_row = sh.row(0)
            self.result = self._checkheader(head_row)
            if len(self.result) > 0:
                return action

            # 清除缓存
            self.env['zy.pound.import'].clear_caches()

            # 检查数据行
            for rx in range(1, sh.nrows):
                row = sh.row(rx)
                check_result = self._check_row(row, rx)
                if check_result['raiseError']:
                    self.result = str(self.result) + check_result['error']
            if len(self.result) > 0:
                return action

            # datas = {}
            # for row in self._read_xlsx_book(book):
            #     if row[0] == '磅单编号':
            #         continue
            #     dic = process_row(row)
            #     datas[name_data] = dic
            lost_row = 0
            for rx in range(1, sh.nrows):
                row = sh.row(rx)
                try:
                    self.process_row(row)
                except exceptions.ValidationError as e:
                    self.result = self.result + "<div><span class='text-danger fa fa-close'></span><kbd>第{}行未导入</kbd>,{}</div>".format(
                        rx - 1, e.name)
                    lost_row += 1
                    continue
            if len(self.result) > 0:
                pass
                self.result = "<div><span class='text-danger fa fa-exclamation'></span><kbd>共{}行</kbd>。完成<kbd>导入{}行</kbd>,另有<kbd>{}行未导入</kbd>。请整理excel数据,不能包含重复行和系统中已存在的记录</div>".format(
                    sh.nrows - 1, sh.nrows - 1 - lost_row, lost_row) + self.result
            else:
                self.result = "<div><span class='text-success fa fa-thumbs-o-up'></span>导入完成,一共<kbd>{}</kbd>行</div>".format(
                    sh.nrows - 1)
            return action

        except Exception as e:
            _logger.exception('File unsuccessfully imported, due to format mismatch.')
            raise UserError(
                _('File %r not imported due to format mismatch or a malformed file.'
                  ' (Valid formats are .xlsx)\n\nTechnical Details:\n%s') % \
                (this.filename, tools.ustr(e))
            )

    def _checkheader(self, row):
        """检查导入的excel的表头格式"""
        result = ""
        headers = ["磅单编号",
                   "发货人（供应商）",
                   "运输货物名称",
                   "规格型号",
                   "车辆编号",
                   "出厂日期",
                   "发货日期",
                   "车数",
                   "净重",
                   "原发重",
                   "运输单位",
                   "发货地址",
                   "油车车号",
                   "电车承运单位"]
        for i in range(0, len(headers)):
            if headers[i] != row[i].value:
                result = result + "<div><span class='text-danger fa fa-close'></span>表头不正确, <kbd>{}</kbd>单元格的位置应该为<kbd>{}</kbd></div>".format(
                    row[i].value, headers[i])
        return result

    def _check_row(self, row, rx):
        """ 检查行有效性 """
        rais = {"raiseError": False, "error": ""}
        result = ""
        # 运输单位
        if not (self._getModelId((row[10].value, 'res.company'))):
            result = result + r"<div><span class='text-danger fa fa-close'></span>运输单位所在列<kbd>{}</kbd>不存在</div>".format(
                row[10].value)

        # 判断出厂日期栏
        if row[5].ctype != 3 and row[5].ctype != 1:
            result = result + r"<div><span class='text-danger fa fa-close'></span>出厂日期所在列<kbd>{}</kbd>不是有效的日期格式,正确的格如:<kbd>{}</kbd></div>".format(
                row[5].value, "2020-5-12")
        if row[5].ctype == 1:
            try:
                time.strptime(row[5].value, "%Y-%m-%d")
            except Exception:
                result = result + r"<div><span class='text-danger fa fa-close'></span>出厂日期所在列<kbd>{}</kbd>不是有效的日期格式,正确的格如:<kbd>{}</kbd></div>".format(
                    row[5].value, "2020-5-12")

        # 判断发货日期栏
        if row[6].ctype != 3 and row[6].ctype != 1:
            result = result + r"<div><span class='text-danger fa fa-close'></span>发货日期所在列<kbd>{}</kbd>不是有效的日期格式,正确的格如:<kbd>{}</kbd></div>".format(
                row[6].value, "2020-5-12")
        if row[6].ctype == 1:
            try:
                time.strptime(row[6].value, "%Y-%m-%d")
            except Exception:
                result = result + r"<div><span class='text-danger fa fa-close'></span>发货日期所在列<kbd>{}</kbd>不是有效的日期格式,正确的格如:<kbd>{}</kbd></div>".format(
                    row[6].value, "2020-5-12")

        # 判断发货地址栏
        if not (self._getAddressId(row[11].value, row[1].value)):
            result = result + r"<div><span class='text-danger fa fa-close'></span>发货地址所在列<kbd>{}</kbd>不存在或供应商有问题</div>".format(row[11].value)
        # if not (self._getModelId((row[11].value, 'zy.address'))):
        #     result = result + "<div><span class='text-danger fa fa-close'></span>发货地址所在列<kbd>{}</kbd>不存在</div>".format(
        #         row[11].value)

        # 判断车号栏
        vehicleId = self._getModelId((row[4].value, 'zy.vehicle'))
        if not vehicleId:
            self.env["zy.vehicle"].sudo().create(
                {"name": row[4].value})

        self.env['zy.pound.import'].clear_caches()
        # 判断油车车号栏
        carotherID = self._getModelId((row[12].value, 'zy.vehicle'))
        if row[12].value != '' and (not carotherID):
            self.env["zy.vehicle"].sudo().create(
                {"name": row[12].value})

        if len(result) > 0:
            result = r"<div><kbd>第{}行</kbd>出现如下错误:</div>".format(rx + 1) + result
            rais["raiseError"] = True
            rais["error"] = result
        return rais

    @tools.ormcache('date')
    def _getTupleDate(self, date):
        """ 日期单元格转换成元组 """
        return xlrd.xldate_as_tuple(date, 0)

    @tools.ormcache('value')
    def _get_createdate_tuple(self, value):
        """'日期单元格字符串转换成日期元组 """
        split_str = "-"
        if value.find("/") >= 0:
            split_str = "/"
        elif value.find("\\") >= 0:
            split_str = '\\'
        year_s, mon_s, day_s = value.split(split_str)
        return int(year_s), int(mon_s), int(day_s), 0, 0, 0

    @tools.ormcache('name_model')
    def _getModelId(self, name_model):
        """ 更据名称和模型查找ID """
        if not name_model[0]:
            return False
        record = self.env[name_model[1]].sudo().search(
            [('name', '=', name_model[0])], limit=1)
        if record.exists():
            return record.id
        return False

    def _getAddressId(self, name_address, pound_supplier):
        """ 根据地址名称和供货商名查询 """
        if not(name_address or pound_supplier):
            return False
        record = self.env['zy.address'].sudo().search(
            ['&', ('name', '=', name_address), ('supplier', '=', pound_supplier)], limit=1)
        if record.exists():
            return record.id
        return False
