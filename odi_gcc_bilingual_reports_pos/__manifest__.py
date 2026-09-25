# -*- coding: utf-8 -*-
{
    "name": "GCC Arabic Bilingual POS Receipts",
    "summary": "Bilingual AR/EN POS receipt templates for odi_gcc_bilingual_reports",
    "description": """
Companion to ``odi_gcc_bilingual_reports``.

Hard-depends on ``point_of_sale`` so the main reports module can stay
installable without POS. Does **not** reimplement ZATCA POS EDI
(``l10n_sa_pos``).
    """,
    "author": "ODI",
    "category": "Sales/Point of Sale",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "depends": [
        "point_of_sale",
        "odi_gcc_bilingual_reports",
    ],
    "data": [
        "report/pos_receipt_templates.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
