{
    'name': "中运物流-运价管理",
    'summary': """
        根据业务需要将运单等信息创建
    """,
    'description': """
        统计业务：用于业务数据统计查询，配合出纳使用
    """,
    'author': "Liu Dongxing",
    # 'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'mail','zhongyun_address','zhongyun_goods','zhongyun_buckle'],
    'data': [
        'data/data_tools.xml',
        'data/data.xml',
        'data/email_template.xml',
        'security/groups.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        # 'views/web_assets.xml',
        'views/menu.xml',
        'views/view.xml',
        
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
