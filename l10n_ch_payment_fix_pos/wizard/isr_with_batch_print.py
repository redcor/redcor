# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.exceptions import UserError


class IsrBatchPrintWizard(models.TransientModel):

    _name = 'isr.batch.print.details.wizard'

    move_ids = fields.Many2many(comodel_name='account.move',
                                   string='Invoices')
    error_message = fields.Text('Errors')

    @api.model
    def default_get(self, fields):
        res = super(IsrBatchPrintWizard, self).default_get(fields)
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            invoices = self.env['account.move'].browse(active_ids)
            msg = self.check_generatable(invoices)
            if msg:
                res['error_message'] = msg
            res['move_ids'] = active_ids
        return res

    @api.model
    def check_generatable(self, invoices):
        try:
            invoices._check_isr_generatable()
        except UserError as e:
            return e.name

    def print_payment_slips_with_details(self):
        if self.move_ids:
            return self.move_ids.print_isr_with_invoice_details()
        else:
            return {'type': 'ir.actions.act_window_close'}
