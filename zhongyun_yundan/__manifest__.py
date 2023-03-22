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
    'depends': ['base', 'mail', 'zhongyun_charge','list_button_template','zhongyun_pound','zhongyun_vehicle'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/action_data.xml',
        'views/view.xml',
        'views/menu.xml',
        'views/view_vehicle.xml',
        # 'data/email_template.xml'
    ],
    # 'qweb': [
    #     "static/src/xml/button.xml",
    # ],
    'assets': {
        'web.assets_backend': [
            'zhongyun_yundan/static/src/kanban_button/kanban_button.xml',
            'zhongyun_yundan/static/src/kanban_button/kanban_button.js',
            'zhongyun_yundan/static/src/mixins/add_kanban.js',
            'zhongyun_yundan/static/src/fields/input_dropdown.xml',

            'zhongyun_yundan/static/src/views/yundan_dashboard.js',
            'zhongyun_yundan/static/src/views/yundan_dashboard.xml',
            'zhongyun_yundan/static/src/views/yundan_listview.js',
            'zhongyun_yundan/static/src/views/yundan_listview.scss',
            'zhongyun_yundan/static/src/views/yundan_listview.xml',
            'zhongyun_yundan/static/src/views/yundan_kanbanview.xml',
            'zhongyun_yundan/static/src/views/yundan_kanbanview.js',

            'zhongyun_yundan/static/src/daterange/daterange/daterange_field.js',
            'zhongyun_yundan/static/src/daterange/daterange/daterange_field.xml',


        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
}
