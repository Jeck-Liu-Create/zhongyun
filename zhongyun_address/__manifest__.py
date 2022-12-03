{
    'name': "中运物流-地址管理",
    'summary': """
        根据需要添加发货地址信息
    """,
    'description': """
        根据需要添加发货地址信息
    """,
    'author': "Liu Dongxing",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'mail','zhongyun_l10n_cn_area'],
    'data': [
        'security/security.xml',
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/view.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
}
