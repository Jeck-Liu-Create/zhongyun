{
    'name': "城市 县/区信息维护",
    'summary': """
        实现 城市 县区信息的维护
    """,
    'description': """
         实现 城市 县区信息的维护
    """,
    'author': "Liu Dongxing",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'mail', 'l10n_cn_city'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/rec_cn_city_view.xml',
        'views/view.xml',
        'data/res_city_data.xml',
        'data/res_area_data.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
