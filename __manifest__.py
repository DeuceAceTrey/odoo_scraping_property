# -*- coding: utf-8 -*-
{
    'name': "property",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base','board',],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/broker.xml',
        'views/signature_vs_truecheck.xml',
        'views/listings_by_date.xml',
        'views/averages.xml',
        'views/type.xml',
        'views/pricing.xml',
        'views/furnished.xml',
        'views/views_dld.xml',
        'views/dld_total_transaction.xml',
        'views/dld_averages.xml',
        'views/dld_comparison_subtype.xml',
        'views/dld_comparison_usage.xml',
        'views/dash.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

}
