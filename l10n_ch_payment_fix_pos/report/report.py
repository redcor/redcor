
import os
import subprocess
import base64
import logging
import tempfile
from contextlib import closing

from odoo import _, api, models, tools


_logger = logging.getLogger(__name__)


class Report(models.Model):
    """
        This class is inherited from class with same name in
        addon  l10n_ch_payment_slip, in order to override the following
        method _generate_one_slip_per_page_from_invoice_pdf, since
        the attribute ids of instance Report (self.ids) is 0 and
        self.env.context.get('active_ids', [])) must be used instead
        to get invoices. But is that always trusty?
    """
    _inherit = 'ir.actions.report'

    def _generate_one_slip_per_page_from_invoice_pdf(self, res_ids):
        """Generate payment slip PDF(s) from report model.
        If there is many pdf they are merged in memory or on
        file system based on company settings

        :return: the generated PDF content
        """
        user_model = self.env['res.users']
        slip_model = self.env['l10n_ch.payment_slip']
        invoice_model = self.env['account.move']
        company = user_model.browse(self.env.uid).company_id
        # invoices = invoice_model.browse(self.ids)
        invoices = invoice_model.browse(res_ids)
        docs = slip_model._compute_pay_slips_from_invoices(invoices)
        if len(docs) == 1:
            return docs[0]._draw_payment_slip(a4=True,
                                              b64=False,
                                              report_name=self.report_name,
                                              out_format='PDF')
        else:
            pdfs = (x._draw_payment_slip(a4=True, b64=False, out_format='PDF',
                                         report_name=self.report_name)
                    for x in docs)
            if company.merge_mode == 'in_memory':
                return self.merge_pdf_in_memory(pdfs)
            return self.merge_pdf_on_disk(pdfs)

    def render_reportlab_pdf(self, res_ids=None, data=None):
        if (self.report_name not in [
            ("l10n_ch_payment_fix_pos.one_slip_per_page_with_invoice_details"),
            ("l10n_ch_payment_slip.one_slip_per_page_from_invoice")]) \
                or not res_ids:
            return
        save_in_attachment = {}

        # Dispatch the records by ones having an attachment and ones
        # requesting a call to reportlab. (copied from render_qweb_pdf)
        Model = self.env[self.model]
        records = Model.browse(res_ids)
        rl_records = Model
        if self.attachment:
            for rec in records:
                attachment_id = self.retrieve_attachment(rec)
                if attachment_id:
                    save_in_attachment[rec.id] = attachment_id
                if not self.attachment_use or not attachment_id:
                    rl_records += rec
        else:
            rl_records = records
        res_ids = rl_records.ids

        if save_in_attachment and not res_ids:
            _logger.info('The PDF report has been generated from attachments.')
            return self._post_pdf(save_in_attachment), 'pdf'

        pdf_content = self._generate_one_slip_per_page_from_invoice_pdf(
            res_ids)
        if res_ids:
            _logger.info(
                'The PDF report has been generated for records %s.' % (
                    str(res_ids))
            )
            return self._post_pdf(save_in_attachment, pdf_content=pdf_content,
                                  res_ids=res_ids), 'pdf'
        return pdf_content, 'pdf'


