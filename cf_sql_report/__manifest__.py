# -*- coding: utf-8 -*-
# 盛哲康虎信息技术（厦门）有限公司
# http://www.khcloud.net
# QQ: 360026606
# wechat: 360026606
# -------------------------
#
{
    "name": "CF SQL Report Builder",
    "summary": "CF report(model) builder based on SQL Views (Materialized or Normal)",
    "version": "15.0.0.2",
    "license": "Other proprietary",
    "category": "cfsoft",
    "author": "CFSoft Co., Ltd. 【康虎软件（QQ：360026606， 微信：360026606）】",
    "website": "https://www.khcloud.net",
    "depends": ["base", "cf_report_designer"],
    "data": [
        "security/ir_module_category.xml",
        "security/res_groups.xml",
        "security/ir.model.access.xml",
        "views/view_cf_sql_model.xml",
        "views/cf_report_designer_view.xml",
        "views/cf_sql_report_action.xml",
        "views/cf_sql_report_menu.xml",
        # "views/assets.xml",
    ],
    "qweb": [
        'static/src/xml/qweb.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'cf_sql_report/static/src/**/*',
        ],
    },
    "demo": [
        "demo/res_groups_demo.xml",
        "demo/cf_sql_model_demo.xml"
    ],
    "installable": True,
    "uninstall_hook": "uninstall_hook",
}
