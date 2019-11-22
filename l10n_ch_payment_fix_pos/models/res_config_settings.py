
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    """
    extend 'res.company' in order to select header logo and
    change position, font size for invoice address above bvr
    """
    _inherit = "res.config.settings"

    header_logo = fields.Binary(
        related='company_id.header_logo',
        readonly=False)
    header_logo_width_percent = fields.Integer(
        related='company_id.header_logo_width_percent',
        readonly=False)
    address_hor_distance_from_left = fields.Float(
        related='company_id.address_hor_distance_from_left',
        readonly=False)
    address_vert_distance_from_bottom = fields.Float(
        related='company_id.address_vert_distance_from_bottom',
        readonly=False)
    address_font_size = fields.Integer(
        related='company_id.address_font_size',
        readonly=False)
    generate_esr = fields.Boolean(
        related='company_id.generate_esr',
        readonly=False)
