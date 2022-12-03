{
    'name': "中运物流-计量规则",
    'summary': """
        根据业务建立计量信息
    """,
    'description': """
        统计业务：用于业务数据统计查询，配合出纳使用
    """,
    'author': "Liu Dongxing",
    'category': '中运物流',
    'version': '0.1',
    'depends': ['base', 'mail','zhongyun_address'],
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
    'installable': True,
    'auto_install': False,
    'application': True,
}
