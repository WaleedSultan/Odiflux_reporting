# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    odi_report_lang_mode = fields.Selection(
        selection=[
            ("bilingual", "Bilingual (AR + EN)"),
            ("ar_only", "Arabic only"),
            ("en_only", "English only"),
        ],
        string="Statutory Report Language Mode",
        default="bilingual",
        config_parameter="odi_gcc_bilingual_reports.lang_mode",
        help="Controls label stacking on invoice / FS QWeb prints. "
             "Does not change Odoo UI language.",
    )
    odi_show_qr_slot = fields.Boolean(
        string="Show QR Placement Slot",
        default=True,
        config_parameter="odi_gcc_bilingual_reports.show_qr_slot",
        help="Reserve space for native ZATCA/GCC QR when EDI modules render it. "
             "This module does not generate QR / TLV / XML.",
    )
    odi_show_cr_block = fields.Boolean(
        string="Show Commercial Registration Block",
        default=True,
        config_parameter="odi_gcc_bilingual_reports.show_cr_block",
        help="Show/hide CR / ID scheme blocks when present on localization.",
    )
    odi_show_building_district = fields.Boolean(
        string="Show Building / District Lines",
        default=True,
        config_parameter="odi_gcc_bilingual_reports.show_building_district",
        help="Show KSA-style building number and district on prints when set.",
    )
