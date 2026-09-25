# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    name_ar = fields.Char(
        string="Arabic Account Name",
        translate=False,
        help="Arabic display label for bilingual financial statements. "
             "Keep technical English name/code for accountants.",
    )

    def _odi_display_name_ar(self):
        self.ensure_one()
        return self.name_ar or self.name or ""
