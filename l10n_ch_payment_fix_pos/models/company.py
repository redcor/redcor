
from odoo import models, fields


class ResCompany(models.Model):
    """
    extend 'res.company' in order to select header logo and
    change position, font size for invoice address above bvr
    """
    _inherit = "res.company"

    header_logo = fields.Binary(
        'Header Logo',
    )
    header_logo_width_percent = fields.Integer(
        'Logo`s width in percents (height will be automatically adjusted)',
        default=90
    )
    address_hor_distance_from_left = fields.Float(
        'Horizontal Distance from left (will be multiplicated with dpi)',
        default=5.0
    )
    address_vert_distance_from_bottom = fields.Float(
        'Vertical Distance from bottom (will be multiplicated with dpi)',
        default=9.5
    )
    address_font_size = fields.Integer(
        'Font Size in Pixels',  # this is also font size for company address
        default=11
    )
    generate_esr = fields.Boolean(
        'should esr data be generated',
        default=True
    )

