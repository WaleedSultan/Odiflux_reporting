# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    name_ar = fields.Char(
        string="Arabic Company Name",
        translate=False,
        help="Legal / trade name in Arabic for bilingual statutory prints. "
             "Falls back to English name when empty.",
    )
    street_ar = fields.Char(string="Arabic Street")
    street2_ar = fields.Char(string="Arabic Street 2")
    city_ar = fields.Char(string="Arabic City")
    district_ar = fields.Char(
        string="Arabic District",
        help="KSA-style district / neighborhood (حي).",
    )
    building_number_ar = fields.Char(
        string="Arabic Building Number",
        help="Optional Arabic display for building / unit number.",
    )
    partner_address_ar = fields.Text(
        string="Arabic Address (single block)",
        help="Optional free-form Arabic address block used when atom fields "
             "are empty. Prefer structured street/city fields when available.",
    )
    # VAT / TRN: use native res.company.vat — do not duplicate.
