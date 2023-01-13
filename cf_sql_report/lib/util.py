# -*- coding: utf-8 -*-
# 康虎软件工作室
# http://www.khcloud.net
# QQ: 360026606
# wechat: 360026606
#--------------------------

import os
import sys
import logging
import string

import odoo
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


def get_ver_info():
    ver_info = odoo.service.common.exp_version()
    return ver_info.get("server_version_info")