{
    'name': "中运物流-磅单管理",
    'summary': """
        创建磅单管理、磅单管理匹配、磅单管理维护
    """,
    'description': """
        磅单管理相关操作
    """,
    'author': "Liu Dongxing",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'mail', 'zhongyun_vehicle','zhongyun_address'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/menu.xml',
        'views/view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
