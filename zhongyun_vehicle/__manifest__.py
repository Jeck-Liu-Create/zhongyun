{
    'name': "中运物流-车辆管理",
    'summary': """
        车辆信息管理
    """,
    'description': """
        车辆管理相关操作
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
    'installable': True,
    'auto_install': False,
    'application': True,
}
