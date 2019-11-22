from odoo import api, models


class AccountInvoice(models.Model):
    """Inherit account.move in order to add isr and invoice details
    printing functionnalites. ISR is a Swiss payment vector"""

    _inherit = "account.move"

    def print_isr_with_invoice_details(self):
        self._check_isr_generatable()
        self.write({
            'invoice_sent': True
        })
        report_name = 'l10n_ch_payment_fix_pos.one_slip_per_page_with_invoice_details'
        docids = self.ids
        result = self.env['ir.actions.report']._get_report_from_name(
            report_name)
        return result.report_action(docids)
