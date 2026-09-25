# -*- coding: utf-8 -*-
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    name_ar = fields.Char(
        string="Arabic Name",
        translate=False,
        help="Partner legal / display name in Arabic. Falls back to English name.",
    )
    street_ar = fields.Char(string="Arabic Street")
    street2_ar = fields.Char(string="Arabic Street 2")
    city_ar = fields.Char(string="Arabic City")
    district_ar = fields.Char(string="Arabic District")
    building_number_ar = fields.Char(string="Arabic Building Number")
    partner_address_ar = fields.Text(
        string="Arabic Address (single block)",
        help="Optional free-form Arabic address when structured fields are empty.",
    )

    def _odi_display_name_ar(self):
        """Return Arabic name or English fallback (for QWeb helpers)."""
        self.ensure_one()
        return self.name_ar or self.name or ""

    def _odi_address_ar_lines(self):
        """Build Arabic address lines with EN fallback per atom."""
        self.ensure_one()
        if self.partner_address_ar and not any(
            (self.street_ar, self.city_ar, self.district_ar)
        ):
            return [line for line in (self.partner_address_ar or "").splitlines() if line]
        lines = []
        street = self.street_ar or self.street
        street2 = self.street2_ar or self.street2
        district = self.district_ar
        city = self.city_ar or self.city
        if street:
            lines.append(street)
        if street2:
            lines.append(street2)
        if district:
            lines.append(district)
        if city:
            lines.append(city)
        return lines
