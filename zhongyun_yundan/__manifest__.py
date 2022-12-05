{
    'name': "中运物流-运单管理",
    'summary': """
        创建运单、运单匹配、运单维护
    """,
    'description': """
        运单相关操作
    """,
    'author': "Liu Dongxing",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'mail', 'zhongyun_charge','zhongyun_pound','list_button_template'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        # 'data/action_data.xml',
        'views/view.xml',
        'views/menu.xml',
        # 'views/template.xml',
    ],
    # 'qweb': [
    #     "static/src/xml/button.xml",
    # ],
    # 'assets': {
    #     'web.assets_backend': [
    #         "zhongyun_yundan/static/src/xml/button.xml",
    #         'zhongyun_yundan/static/src/js/add_button.js',
    #
    #     ],
    # },
    'installable': True,
    'auto_install': False,
    'application': True,
}
