from odoo import http
from odoo.http import request

class BatchProcessing(http.Controller):

    @http.route('/data/map', type='json', auth='user')
    def data_tongji(self, **kwargs):
        data = dict()
        news_target = self._data_news()
        province_data = self._data_hot_map()
        history_data = self._history_data(kwargs)
        data['news_target'] = news_target
        data['province_data'] = province_data
        data['history_data'] = history_data
        return data

    