# -*- coding: utf-8 -*-
{
    'name': "kanban_button_template",

    'summary': """
    kanban button template for odoo
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
            'kanban_button_template/static/src/kanban_button/kanban_button.xml',
            'kanban_button_template/static/src/kanban_button/kanban_button.js',
            'kanban_button_template/static/src/mixins/add_kanban.js',

        ]
    }
}
