# -*- coding: utf-8 -*-
{
    'name': "redo2oo_resources",

    'summary': """
        all resources used accross modules by the redo2oo site
        """,

    'description': """
        all resources used accross modules by the redo2oo site
    """,

    'author': "redO2oo",
    'website': "http://www.redO2oo.ch",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Theme/Creative',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['backend_theme_v10'],

    # always loaded
    'data': [
        'views/assets.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
}