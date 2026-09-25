# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    name_ar = fields.Char(
        string="Arabic Product Name",
        translate=False,
        help="Arabic display name for bilingual invoice / POS lines. "
             "Fallback chain on prints: name_ar → English name → move-line description.",
    )

    def _odi_display_name_ar(self):
        """Return Arabic product name or English fallback."""
        self.ensure_one()
        return self.name_ar or self.name or ""


class AccountMoveLine(models.Model):
    """Helpers for bilingual line description on invoices / CN / DN."""

    _inherit = "account.move.line"

    def _odi_line_description_ar(self):
        """Fallback: product.name_ar → product EN name → line name/description."""
        self.ensure_one()
        product = self.product_id.product_tmpl_id if self.product_id else False
        if product and product.name_ar:
            return product.name_ar
        if product and product.name:
            return product.name
        return self.name or ""

    def _odi_line_description_en(self):
        self.ensure_one()
        product = self.product_id.product_tmpl_id if self.product_id else False
        if product and product.name:
            return product.name
        return self.name or ""
