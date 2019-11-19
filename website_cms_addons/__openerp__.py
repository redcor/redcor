# -*- coding: utf-8 -*-
{
    'name': "website_cms_addons",

    'summary': """
    addons for the website_cms module
    """,

    'description': """
    addons for te website_cms module
    """,

    'author': "redO2oo.ch",
    'website': "http://www.redO2oo.ch",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Website',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website_cms', 'event'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
