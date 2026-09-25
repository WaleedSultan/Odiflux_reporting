# -*- coding: utf-8 -*-
{
    "name": "GCC Arabic Bilingual Invoices & Financial Reports",
    "summary": "Bilingual AR/EN invoices, CN/DN, financial statements — reports only, no EDI/ZATCA send",
    "description": """
GCC Arabic Bilingual Statutory Documents Pack
=============================================

Production-grade bilingual Arabic/English QWeb reports for invoices,
credit/debit notes, and financial statements. RTL-safe typography and
Arabic master-data fields for company, partner, and chart of accounts.

**Positioning**

* Sits beside native ZATCA / GCC EDI — bilingual **reports only**
* No clearance, no XML generation, no CSID — layout and QR **placement** only
* Keywords: Arabic invoice, Arabic POS (companion), Arabic financial report

**Soft companions**

* ``odi_gcc_bilingual_reports_pos`` — POS receipt templates (depends on point_of_sale)
* Works with ``l10n_sa``, ``l10n_gcc_invoice``, ``l10n_sa_edi`` when installed

**Out of scope (v1)**

* ZATCA Phase 2 XML / clearance / CSID
* Peppol / UAE PINT send
* Full Odoo UI .po translation pack
    """,
    "author": "ODI",
    "website": "https://www.odoo.com",
    "category": "Accounting/Localizations/Reporting",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "depends": [
        "account",
    ],
    # Optional / soft (auto_install false — document only; do NOT hard-depend):
    # point_of_sale → companion module odi_gcc_bilingual_reports_pos
    # l10n_gcc_invoice, l10n_sa, l10n_sa_edi, account_reports (Enterprise FS)
    "data": [
        "data/report_paperformat_data.xml",
        "views/res_company_views.xml",
        "views/res_partner_views.xml",
        "views/account_account_views.xml",
        "views/product_template_views.xml",
        "views/res_config_settings_views.xml",
        "views/report_menus.xml",
        "report/report_invoice_bilingual.xml",
        "report/report_financial_statements.xml",
    ],
    "assets": {
        "web.report_assets_common": [
            "odi_gcc_bilingual_reports/static/src/css/report_bilingual.css",
        ],
    },
    "images": [
        "static/description/icon.png",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
