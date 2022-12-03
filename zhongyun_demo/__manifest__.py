{
    'name': "ZhongYunStatistics",
    'summary': """
        统计业务：用于业务数据统计查询，配合出纳使用
    """,
    'description': """
        统计业务：用于业务数据统计查询，配合出纳使用
    """,
    'author': "Liu Dongxing",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # 悬浮组件
            # 'zhongyun_demo/static/es6/**/*',
            'zhongyun_demo/static/src/xml/spreadsheet_test.xml',
            'zhongyun_demo/static/src/js/spreadsheet_test.js',
            'zhongyun_demo/static/src/js/xspreadsheet.js',
            'zhongyun_demo/static/src/css/xspreadsheet.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
}
