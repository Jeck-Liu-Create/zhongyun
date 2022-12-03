{
    'name': "中运物流-运价维护-审批流",
    'summary': """
        运价维护审批业务
    """,
    'description': """
        运价维护审批业务
    """,
    'author': "Liu Dongxing",
    # 'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'mail', 'zhongyun_address', 'zhongyun_charge'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/email_template.xml',
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
