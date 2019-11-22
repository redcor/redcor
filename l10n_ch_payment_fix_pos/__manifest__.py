{
    'name': 'swiss_payment_slip with invoice details on same page',
    'version': '13.0.1.0.0',
    'author': "Ogi Vranesic",
    'website': 'http://www.redcor.ch',
    'license': 'AGPL-3',
    'depends': ['l10n_ch_payment_slip'],
    'data': [
        "views/res_config_settings_views.xml",
        "views/account_invoice.xml",
        "report/report_declaration.xml",
        "wizard/isr_with_batch_print.xml"
    ],
    'installable': True,

}
