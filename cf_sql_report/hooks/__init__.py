# -*- coding: utf-8 -*-
# 盛哲康虎信息技术（厦门）有限公司
# http://www.khcloud.net
# QQ: 360026606
# wechat: 360026606
# -------------------------
#

try:
    from pycfloader.pycfloader import *
except ImportError:
    raise ImportError("Please install pycfloader using below command first: \n pip(3) install pycfloader")

from . import hooks
