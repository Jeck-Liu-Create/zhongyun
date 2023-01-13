# -*- coding: utf-8 -*-
# 康虎软件工作室
# http://www.khcloud.net
# QQ: 360026606
# wechat: 360026606
# -------------------------
#

{
    'name': "CF Report Designer",

    'summary': """
        康虎云报表字段定义设计器
        """,

    'description': """
康虎云报表字段定义设计器
============================
本模块用以实现可视化定义报表所需的字段、使用的模板等信息。
定义后，在打印报表时即可自动生成报表数据，无需手工在QWeb模板中定义。


本模块主要功能：
----------------------------
* 定义报表所需字段
* 定义报表使用的模板
* 自动生成报表定义
* 自动生成报表数据文件

剩下的事情就是在康虎云报表设计器中设计报表模板并打印即可。

注意：
============================
该模块依赖 pycryptodome，请用以下命令安装：
pip install pycryptodome
或
python -m pip install pycryptodome

    """,

    'author': "CFSoft Co., Ltd. 【康虎软件工作室（QQ：360026606， 微信：360026606）】",
    'website': "http://www.khcloud.net",

    'category': 'cfsoft',
    'version': '15.0.2.9',
    'license': 'Other proprietary',

    # 依赖的python库
    "external_dependencies": {
        'python': ['pycryptodome', 'pycfloader']
    },

    # any module necessary for this one to work correctly
    'depends': ['base', 'cfprint'],
    'assets': {
        'web.assets_backend': [
            'cf_report_designer/static/src/**/*',
            'cf_report_designer/static/src/**/*.js',
        ],
    },

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/ir.model.access.xml',
        'views/views.xml',
        'views/templates.xml',
        # 'views/assets.xml',

        "data/cfprint_templates.xml",
        "data/report_define_category_data.xml",
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
