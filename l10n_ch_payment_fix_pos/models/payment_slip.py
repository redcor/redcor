from datetime import datetime
import contextlib
import base64
import io
from PIL import Image

from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader
# odoo 11 has no repost_swx
# from odoo.report import report_sxw
# if we wanted to import report we in v11 we do it like this
# from odoo.tools import report
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo import models, api, _, exceptions
from odoo.modules import get_module_resource
from odoo.tools.misc import mod10r, format_date
import re


class InvoiceAddressSettings(object):
    """invoice address report setting container"""

    def __init__(self, report_name, **kwargs):
        for param, value in kwargs.items():
            setattr(self, param, value)
        self.report_name = report_name
        self.validate()

    def validate(self):
        "Parameter Validationd hook"""
        pass


class PaymentSlipFixPos(models.Model):
    _inherit = "l10n_ch.payment_slip"

    canvas_size = (595.27, 841.89)  # ??? A4
    canvas_size_mm = (210, 297)

    _fill_color = (0, 0, 0)
    _default_font_size = 10
    _default_scan_font_size = 11
    _default_amount_font_size = 16
    _compile_get_ref = re.compile(r'[^0-9]')
    _compile_check_isr = re.compile(r'[0-9][0-9]-[0-9]{3,6}-[0-9]')

    # @api.model
    def get_language_record(self, code):
        res_lang_name = 'res.lang'
        try:
            res_lang_model = self.env[res_lang_name]
        except KeyError:
            raise exceptions.UserError(
                'model "%s" does not exist' % res_lang_name)
        languages = res_lang_model.search(
            [('code', '=', code)],
            limit=1)
        if languages:
            return languages[0]

    def detect_date_format(self, language_record):
        if language_record:
            language_dateformat = language_record.date_format
            if language_dateformat:
                return language_dateformat
        return DEFAULT_SERVER_DATE_FORMAT

    def get_correct_date_str(self, date_str_from_db, correct_date_format):
        if date_str_from_db:
            # first: create date object using date_str_from_db
            #        and DEFAULT_SERVER_DATE_FORMAT
            date_obj = datetime.strptime(
                str(date_str_from_db), DEFAULT_SERVER_DATE_FORMAT)
            # second: from date_obj create again date_str with corre
            # ct_date_format
            return date_obj.strftime(correct_date_format)
        return ''

    def _get_img_from_db(self, img_bin, w_percent):
        img_data = base64.decodebytes(img_bin)
        img = Image.open(io.BytesIO(img_data))
        if w_percent:
            # resize image
            width = int(self.canvas_size[0] * w_percent / 100)
            resize = (width / float(img.size[0]))
            height = int(float(img.size[1]) * resize)
            img = img.resize((width, height), Image.ANTIALIAS)
        return img

    # --------------------------------------------------------------------------

    @api.model
    def _draw_logo_with_address(self, canvas, font_name, font_size,
                                company_id=1):
        # the 0,0 position of a page is its lower left corner
        # Y is the heigth, Y is the width od the pager
        # and the top rigth corner is at self.canvas_size -> paper.witdth/paper.heigth
        # we start drawing at the uper left corner which is 0/paper.heigth
        header_logo_bin = self._get_address_settings(
            self.orig_report_name).header_logo
        header_logo_width_percent = self._get_address_settings(
            self.orig_report_name).header_logo_width_percent
        header_logo_img = self._get_img_from_db(
            header_logo_bin, header_logo_width_percent)
        Y = self.canvas_size[1] - 4 - header_logo_img.size[1]
        canvas.drawImage(
            ImageReader(header_logo_img),
            self.left_dist,
            Y,
            header_logo_img.size[0] - 20,
            header_logo_img.size[1]
        )
        canvas.setFont(font_name, font_size)
        Y -= 10
        # canvas.drawString(
        #         10,
        #         Y,
        #         _('Sponsorship')
        #         )
        # Y -= font_size + 2
        company = self.env['res.company'].browse(company_id)
        # , 'country_id'):
        for fn in ('name', 'street', 'zip city', 'email', 'website'):
            if fn.find(' ') > -1:
                val = ''
                for sfn in fn.split():
                    val += self._get_val(company, sfn) + ' '
            else:
                val = self._get_val(company, fn)
            if val:
                canvas.drawString(
                    self.left_dist,
                    Y,
                    val.encode('utf-8')
                )
                Y -= font_size + 2

    def _draw_description_line(self, canvas, print_settings, initial_position,
                               font, report_name):
        """ Draw invoice details above the payment slip
            (override of same method in AddOn l10_ch_payment_slip

        :param canvas: payment slip reportlab component to be drawn
        :type canvas: :py:class:`reportlab.pdfgen.canvas.Canvas`

        :param print_settings: layouts print setting
        :type print_settings: :py:class:`PaymentSlipSettings` or subclass

        :para initial_position: tuple of coordinate (x, y)
        :type initial_position: tuple

        :param font: font to use
        :type font: :py:class:`FontMeta`

        """
        canvas_size = (595.27, 841.89)  # assuming we are using a4
        if report_name == 'l10n_ch_payment_fix_pos.one_slip_per_page_with_invoice_details':
            # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            # INVOICE DETAILS:
            font_name = 'Helvetica'  # 'Arial'
            # inch is type float and I think actually number of dpi in inch
            invoice = self.invoice_id
            language_record = self.get_language_record(invoice.partner_id.lang)
            date_format = self.detect_date_format(language_record)
            # invoice = invoice.with_context({'lang': invoice.partner_id.lang})
            self.orig_report_name = 'l10n_ch_payment_slip.one_slip_per_page_from_invoice'
            address_print_settings = self._get_address_settings(
                self.orig_report_name)
            address_font_size = address_print_settings.address_font_size
            self.left_dist = 10
            if not self.orig_report_name:
                raise ValueError(
                    'Company logo to be put on payment slip missing. Pleas add it in the company setting-> Esr Data')
            # some settings for the positioning of the fields
            line_dist = 2

            # field_pos are the x position of the fields

            def make_pts(mm):
                # make points from milimeters
                return (mm / 25.4) * inch

            field_pos = [
                self.left_dist,
                make_pts(114.5),  # amount
                make_pts(136),  # price per amount
                make_pts(156),  # taxes
                make_pts(176),  # price excl tax
            ]
            amount_pos = [
                self.left_dist,
                make_pts(117),  # amount
                make_pts(138),  # price per amount
                make_pts(157),  # taxes
                make_pts(173),  # price excl tax
            ]
            format_lines = [
                '{:.70}',
                '{: 6.2f}',  # amount
                '{: 8.2f}',  # price per amount
                '{:>4}',  # taxes
                '{: 8.2f} {}',  # price excl tax
            ]
            # ------------------------------------------------------------------
            # 1. company logo with address on top left of page
            self._draw_logo_with_address(canvas, font_name, address_font_size)
            # ------------------------------------------------------------------
            # 2. account holder's address:
            # address_print_settings.address_hor_distance_from_left  # 5
            customer_address_start_position_X = (field_pos[1] / inch)
            customer_address_start_position_Y = address_print_settings.address_vert_distance_from_bottom  # 9.5
            customer_address_diff_Y = address_font_size + 2
            partner = invoice.partner_id
            canvas.setFont(font_name, address_font_size)
            c = 0
            for fname in ('name', 'street', 'street2', 'zip', 'city'):
                fval = self._get_val(partner, fname)
                if fval:
                    X = customer_address_start_position_X * inch
                    Y = customer_address_start_position_Y * inch - c * customer_address_diff_Y
                    if fname == 'city':
                        Y += customer_address_diff_Y
                        X += 30
                    canvas.drawString(
                        X,
                        Y,
                        fval
                    )
                    c += 1
            # ------------------------------------------------------------------
            # 3. invoice details:
            invoice_number_font_size = 14
            distance_from_address_Y = 40
            Y -= distance_from_address_Y
            canvas.setFont(font_name, invoice_number_font_size)
            canvas.drawString(
                self.left_dist,
                Y,
                '%s %s' % (_('Invoice'), invoice.name)
            )
            date_font_size = 10
            distance_from_number_Y = 30
            Y -= distance_from_number_Y
            canvas.setFont(font_name, date_font_size)
            canvas.drawString(
                self.left_dist,
                Y,
                '%s:' % _('Invoice Date')
            )
            Y -= date_font_size + 2
            canvas.drawString(
                self.left_dist,
                Y,
                self.get_correct_date_str(self._get_val(
                    invoice, 'invoice_date'), date_format)
            )
            invoice_date_due = self.get_correct_date_str(
                self._get_val(invoice, 'invoice_date_due'), date_format)
            if invoice_date_due:
                Y -= date_font_size + 2
                canvas.drawString(
                    self.left_dist,
                    Y,
                    '%s:' % _('Due Date')
                )
                Y -= date_font_size + 2
                canvas.drawString(
                    self.left_dist,
                    Y,
                    invoice_date_due
                )
            # ------------------------------------------------------------------
            # 4. invoice lines
            line_font_size = 10
            canvas.setFont(font_name, line_font_size)
            distance_from_date_Y = 20
            empty_distance_between_rows = 3
            # from reportlab.pdfbase.pdfmetrics import stringWidth
            # stringWidth('A', 'Helvetica', 10)
            # 6.67
            char_width = 7  # aproximately
            fieldtitles = [
                'Description',
                'Quantity',
                'Unit Price',
                'Taxes',
                'Subtotal'
            ]
            fieldnames = [
                'name',
                'quantity',
                'price_unit',
                'tax_ids',
                'price_subtotal'
            ]
            taxes_index = 3
            currency_name = invoice.currency_id.name
            currency_width = len(currency_name) * char_width
            self.right_dist = self.left_dist
            length_list, line_list, invoice_line_tax_ids_exists = \
                self.calc_invoice_lines_lengths_and_collect_vals(
                    invoice,
                    fieldtitles,
                    fieldnames,
                    taxes_index,
                    char_width,
                    currency_width
                )
            if not invoice_line_tax_ids_exists:
                del fieldtitles[taxes_index]
                del length_list[taxes_index]
                del amount_pos[taxes_index]
                del field_pos[taxes_index]
                del format_lines[taxes_index]
            Y -= distance_from_date_Y
            for i, subline_list in enumerate(line_list):
                X = self.left_dist
                Y -= line_font_size + empty_distance_between_rows
                for j, val in enumerate(subline_list):
                    is_last_col = j == len(subline_list) - 1
                    if not i:
                        # draw first field titles
                        X = field_pos[j]
                        canvas.drawString(
                            X,
                            Y,
                            _(fieldtitles[j])
                        )
                        if is_last_col:
                            # draw line under the field titles
                            canvas.line(
                                self.left_dist,
                                Y - line_dist - empty_distance_between_rows,
                                canvas_size[1] - amount_pos[1] + 40,
                                Y - line_dist - empty_distance_between_rows
                            )
                    X = amount_pos[j]
                    nval = 0
                    try:
                        val = float(val)
                    except:
                        pass
                    if isinstance(val, str):
                        val = val.encode("utf-8")
                    try:
                        val = val.decode("utf-8")
                        if "\n" in val:
                            nval = val.split("\n")
                    except:
                        pass
                    if nval:
                        for m in nval:
                            string = str(m)
                            canvas.drawString(
                                X,
                                Y - 2 * line_dist -
                                (line_font_size + empty_distance_between_rows),
                                format_lines[-1].format(
                                    string, currency_name) if is_last_col else
                                format_lines[j].format(string)
                            )
                            Y -= 8
                        Y += ((len(nval))*8)
                    else:
                        canvas.drawString(
                            X,
                            Y - 2 * line_dist -
                            (line_font_size + empty_distance_between_rows),
                            format_lines[-1].format(
                                val, currency_name) if is_last_col else
                            format_lines[j].format(val)
                        )
                    if is_last_col and invoice_line_tax_ids_exists:
                        Y -= 6
                        canvas.line(
                            amount_pos[1] - 10,
                            Y - (
                                        line_font_size + empty_distance_between_rows + 7),
                            canvas_size[1] - amount_pos[1] + 40,
                            Y - (
                                        line_font_size + empty_distance_between_rows + 7)
                        )
                        # draw subtotal
                        if i == len(line_list) - 1:
                            Y -= 4
                            canvas.drawString(
                                amount_pos[1] - 10,
                                Y - 2 * line_dist - 2 *
                                (line_font_size + empty_distance_between_rows),
                                _('Untaxed Amount:')
                            )
                            try:
                                amount_untaxed = float(
                                    self._get_val(invoice, 'amount_untaxed'))
                            except:
                                amount_untaxed = 0.0
                            canvas.drawString(
                                amount_pos[-1],
                                Y - 2 * line_dist - 2 *
                                (line_font_size + empty_distance_between_rows),
                                format_lines[4].format(
                                    amount_untaxed, currency_name)
                            )
                            Y -= 2
                            # canvas.line(
                            # amount_pos[1] - 10,
                            # Y - 2 * (line_font_size + empty_distance_between_rows) - 6,
                            # canvas_size[1] - self.left_dist * 2,
                            # Y - 2 * (line_font_size + empty_distance_between_rows) - 6
                            # )
            if invoice_line_tax_ids_exists:
                mn = 3
            else:
                mn = 2
            Y -= 2 * line_dist + mn * \
                    (line_font_size + empty_distance_between_rows)
            Y -= 4
            # taxes
            for amount_by_group in invoice.amount_by_group:
                canvas.drawString(
                    amount_pos[1] + 20,
                    Y,
                    str(amount_by_group[0])+':'
                )
                try:
                    val = float(amount_by_group[1])
                except:
                    val = 0.0
                canvas.drawString(
                    amount_pos[-1] + 2,
                    Y,
                    format_lines[4].format(val, currency_name)
                )
                Y -= 14
            # line after taxes
            Y -= 0
            canvas.line(
                amount_pos[1] - 10,
                Y,
                canvas_size[1] - amount_pos[1] + 40,
                Y
            )
            # total
            Y -= 14  # line_font_size + empty_distance_between_rows -4
            canvas.drawString(
                amount_pos[1] - 10,
                Y,
                _('Total:')
            )
            try:
                val = float(self._get_val(invoice, 'amount_total'))
            except:
                val = 0.0
            canvas.drawString(
                amount_pos[-1],
                Y,
                format_lines[-1].format(val, currency_name)
            )
            # ------------------------------------------------------------------
        else:
            x, y = initial_position
            # align with the address
            x += print_settings.isr_add_horz * inch
            invoice = self.move_line_id.move_id
            date_maturity = self.move_line_id.date_maturity
            message = _('Payment slip related to invoice %s '
                        'due on the %s')
            fmt_date = format_date(self.env, date_maturity)
            canvas.setFont(font.name, font.size)
            canvas.drawString(x, y,
                              message % (invoice.name, fmt_date))

    # ---------------------------------------------------------------
    # --------------------------------------------------------------------------

    def calc_invoice_lines_lengths_and_collect_vals(
            self,
            invoice,
            fieldtitles,
            fieldnames,
            taxes_index,
            char_width,
            currency_width
    ):
        line_list = []
        invoice_line_tax_ids_exists = False
        dist_between = 2 * char_width
        for line in invoice.invoice_line_ids:
            line_sublist = []
            length_list = []
            total_px_len = 0
            for i, fname in enumerate(fieldnames):
                fval = self._get_val(line, fname)
                if fname == 'tax_ids' and fval:
                    invoice_line_tax_ids_exists = True
                line_sublist.append(fval)
                fval_len = len(fval)
                ftitle_len = len(_(fieldtitles[i]))
                col_len = fval_len if fval_len > ftitle_len else ftitle_len
                col_px_len = col_len * char_width + dist_between
                if not i:
                    col_px_len += self.left_dist
                elif i == len(fieldnames) - 1:
                    col_px_len += char_width + currency_width
                total_px_len += col_px_len
                length_list.append(total_px_len)
            line_list.append(line_sublist)
        if not invoice_line_tax_ids_exists:
            # if invoice_line_tax_ids record not found
            # at least by one invoice line
            # remove values
            for subline_list in line_list:
                del subline_list[taxes_index]
        if length_list[-1] + self.right_dist < self.canvas_size[0]:
            # increase each length in order to move display in right direction:
            r = int(self.canvas_size[0] - length_list[-1] - self.right_dist)
            for i in range(len(length_list)):
                length_list[i] += r
        return length_list, line_list, invoice_line_tax_ids_exists

    def _get_val(self, obj, fieldname):
        val = getattr(obj, fieldname, None)
        if not val:
            return ''
        if fieldname == 'tax_ids':
            val = ', '.join([(x.description or x.name) for x in val])
        elif fieldname == 'country_id':
            val = _(val.name)
        else:
            if isinstance(val, float):
                val = '%.2f' % val
            elif isinstance(val, int):
                val = str(val)
        return val

    @api.model
    def logo_absolute_path(self, file_name):
        """Will get image absolute path

        :param file_name: name of image

        :return: image path
        :rtype: str
        """
        path = get_module_resource('l10n_ch_payment_fix_pos',
                                   'static',
                                   'src',
                                   'img',
                                   file_name)
        return path

    @api.model
    def _get_address_settings(self, report_name):
        company = self.env.user.company_id
        company_settings = {
            col: getattr(company, col) for col in company._fields if
            (col.startswith('address_') or col ==
             'generate_esr' or col.startswith('header_logo'))
        }
        return InvoiceAddressSettings(report_name, **company_settings)

    def _draw_payment_slip(self, a4=False, out_format='PDF', scale=None,
                           b64=False, report_name=None):
        """
        (
         override of same method in AddOn l10_ch_payment_slip
         only in order to pass parameter *report_name* on method
         _draw_description_line
         )
        """
        if out_format != 'PDF':
            raise NotImplementedError(
                'Only PDF payment slip are supported'
            )
        self.ensure_one()
        lang = self.invoice_id.partner_id.lang
        self = self.with_context(lang=lang)
        company = self.env.user.company_id
        print_settings = self._get_settings(report_name)
        self._register_fonts()
        default_font = self._get_text_font()
        small_font = self._get_small_text_font()
        amount_font = self._get_amount_font()
        invoice = self.move_line_id.move_id
        scan_font = self._get_scan_line_text_font(company)
        bank_acc = invoice.invoice_partner_bank_id
        isr_subs_number = invoice.l10n_ch_isr_subscription_formatted
        if a4:
            canvas_size = (595.27, 841.89)
        else:
            canvas_size = (595.27, 286.81)
        with contextlib.closing(io.BytesIO()) as buff:
            canvas = Canvas(buff,
                            pagesize=canvas_size,
                            pageCompression=None)
            self._draw_background(canvas, print_settings)
            canvas.setFillColorRGB(*self._fill_color)
            if a4:
                initial_position = (0.05 * inch, 4.50 * inch)
                self._draw_description_line(canvas,
                                            print_settings,
                                            initial_position,
                                            default_font,
                                            report_name)
            if invoice.invoice_partner_bank_id.print_partner:
                if (invoice.invoice_partner_bank_id.print_account or
                        invoice.invoice_partner_bank_id.l10n_ch_isrb_id_number):
                    initial_position = (0.05 * inch, 3.30 * inch)
                else:
                    initial_position = (0.05 * inch, 3.75 * inch)
                self._draw_address(canvas, print_settings, initial_position,
                                   default_font, company.partner_id)
                if (invoice.invoice_partner_bank_id.print_account or
                        invoice.invoice_partner_bank_id.l10n_ch_isrb_id_number):
                    initial_position = (2.45 * inch, 3.30 * inch)
                else:
                    initial_position = (2.45 * inch, 3.75 * inch)
                self._draw_address(canvas, print_settings, initial_position,
                                   default_font, company.partner_id)
            com_partner = self.get_comm_partner()
            initial_position = (0.05 * inch, 1.4 * inch)
            self._draw_address(canvas, print_settings, initial_position,
                               default_font, com_partner)
            initial_position = (4.86 * inch, 2.2 * inch)
            self._draw_address(canvas, print_settings, initial_position,
                               default_font, com_partner)
            num_car, frac_car = ("%.2f" % self.amount_total).split('.')
            self._draw_amount(canvas, print_settings,
                              (1.48 * inch, 2.0 * inch),
                              amount_font, num_car)
            self._draw_amount(canvas, print_settings,
                              (2.14 * inch, 2.0 * inch),
                              amount_font, frac_car)
            self._draw_amount(canvas, print_settings,
                              (3.88 * inch, 2.0 * inch),
                              amount_font, num_car)
            self._draw_amount(canvas, print_settings,
                              (4.50 * inch, 2.0 * inch),
                              amount_font, frac_car)
            if invoice.invoice_partner_bank_id.print_bank:
                self._draw_bank(canvas,
                                print_settings,
                                (0.05 * inch, 3.75 * inch),
                                default_font,
                                bank_acc.bank_id)
                self._draw_bank(canvas,
                                print_settings,
                                (2.45 * inch, 3.75 * inch),
                                default_font,
                                bank_acc.bank_id)
            if invoice.invoice_partner_bank_id.print_account:
                self._draw_bank_account(canvas,
                                        print_settings,
                                        (1 * inch, 2.35 * inch),
                                        default_font,
                                        isr_subs_number)
                self._draw_bank_account(canvas,
                                        print_settings,
                                        (3.4 * inch, 2.35 * inch),
                                        default_font,
                                        isr_subs_number)
            if print_settings.isr_header_partner_address:
                self._draw_address(canvas, print_settings,
                                   (4.9 * inch, 9.0 * inch),
                                   default_font, com_partner)
            self._draw_ref(canvas,
                           print_settings,
                           (4.9 * inch, 2.70 * inch),
                           default_font,
                           self.reference)
            self._draw_recipe_ref(canvas,
                                  print_settings,
                                  (0.05 * inch, 1.6 * inch),
                                  small_font,
                                  self.reference)
            self._draw_invoice_with_date(canvas,
                                         print_settings,
                                         (4.8 * inch, 3.75 * inch),
                                         default_font,
                                         invoice
                                         )
            self._draw_scan_line(canvas,
                                 print_settings,
                                 (8.26 * inch - 4 / 10 * inch, 4 / 6 * inch),
                                 scan_font)
            self._draw_hook(canvas, print_settings)
            canvas.showPage()
            canvas.save()
            img_stream = buff.getvalue()
            if b64:
                img_stream = base64.encodestring(img_stream)
            return img_stream

    @api.model
    def _draw_invoice_with_date(self, canvas, print_settings, initial_position,
                                font, invoice):
        x, y = initial_position
        x += print_settings.isr_delta_horz * inch
        y += print_settings.isr_delta_vert * inch
        text = canvas.beginText()
        text.setTextOrigin(x, y)
        text.setFont(font.name, font.size)
        text.textOut(invoice.name)
        text.moveCursor(0.0, font.size)
        language_record = self.get_language_record(invoice.partner_id.lang)
        date_format = self.detect_date_format(language_record)
        text.textOut(self.get_correct_date_str(invoice.date, date_format))
        canvas.drawText(text)

