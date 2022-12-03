# -*- coding: utf-8 -*-
{
    'name': "list_button_template",

    'summary': """
    list button template for odoo
    """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Funenc Odoo Team",
    'website': "https://odoo.funenc.com",

    'category': 'Uncategorized',
    'version': '15.0.0.1',

    'depends': ['base', 'web'],
    'data': [],

    'assets': {
        'web.assets_backend': [
            'list_button_template/static/src/list_button/list_button.xml'
        ]
    }
}
