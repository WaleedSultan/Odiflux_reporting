===============================================
GCC Arabic Bilingual Statutory Reports
===============================================

**Technical name:** ``odi_gcc_bilingual_reports``  
**Odoo:** 19.0 (port targets 18.0 / 17.0)  
**License:** LGPL-3  
**Price band (Apps Store):** top of \$79–199

One-line pitch
--------------

Production-grade bilingual AR/EN QWeb reports for invoices, credit/debit
notes, and financial statements — RTL-correct and GCC field-complete.

Positioning
-----------

*Sits beside native ZATCA/GCC EDI — bilingual reports only; no clearance/send.*

This is **not** a UI translation dump and **not** another ZATCA XML connector.
It is a statutory **print & bilingual presentation layer** on ``account`` +
GCC localizations.

Apps Store keywords
-------------------

* Arabic invoice
* Arabic POS
* Arabic financial report

Also: bilingual invoice, RTL PDF, KSA tax invoice layout, Arabic Trial Balance,
Arabic P&L, Arabic Balance Sheet, GCC statutory reports.

What v1 includes
----------------

* Arabic master data on company, partner, chart of accounts, and products
  (``product.template.name_ar``; print fallback: ``name_ar`` → EN name →
  move-line description)
* Settings: language mode ``bilingual`` | ``ar_only`` | ``en_only``; QR slot /
  CR / building-district show toggles
* Invoice QWeb inherit stubs (Tax Invoice / Simplified / CN **and DN** on the
  same QWeb + QA path — layout TODOs)
* QR **placement** slot only — native ``l10n_sa_edi`` owns generation
* Financial statement report actions + QWeb stubs (TB / P&L / BS)
* Bundled OFL Arabic font path (IBM Plex Sans Arabic / Noto Naskh)

POS receipts
------------

Main module does **not** hard-depend on ``point_of_sale``.  
Install companion ``odi_gcc_bilingual_reports_pos`` (sibling folder) when POS
is present. Do not reimplement ``l10n_sa_pos`` EDI.

Soft / optional modules (document only)
---------------------------------------

* ``point_of_sale`` → companion POS module
* ``l10n_sa``, ``l10n_gcc_invoice``, ``l10n_sa_edi`` — coexistence; no conflict intended
* ``account_reports`` (Enterprise FS) — Community fallback declared; no silent
  Enterprise-only claim

Out of scope (v1)
-----------------

* ZATCA Phase 2 XML / clearance / CSID
* Peppol / UAE PINT send
* Full Odoo UI ``.po`` translation pack
* Payslips / ESS portal
* Qatar e-invoicing API / Ministry filing packs

Compliance note
---------------

This module does **not** claim ZATCA Phase 2 compliance beyond bilingual layout
and QR placement-friendly design. Clearance, XML, and cryptographic signing
remain the responsibility of native or certified EDI modules.

Installation
------------

1. Copy ``odi_gcc_bilingual_reports`` into your addons path.
2. Update Apps list → install **GCC Arabic Bilingual Statutory Reports**.
3. Company / Partners / Accounts → fill Arabic fields.
4. Accounting → Settings → **GCC Arabic Bilingual Reports**.
5. Optional: install ``odi_gcc_bilingual_reports_pos`` for POS receipts.
6. Day-1 spike: print a sample Arabic PDF and verify font shaping on your host.

Screenshots plan
----------------

Bilingual Tax Invoice, Simplified, POS receipt (companion), Arabic P&L.


Effort
------

* **~18–25 person-days** — Odoo **19.0** MVP first (reports suite scaffold →
  bilingual invoice/CN/DN → fonts spike → FS stubs → QA).
* **~28–35 person-days** — including ports to **18.0** and **17.0** (xpath /
  POS / QWeb diffs per major; separate version branches, not one zip).

See ``/workspace/reports/odi_gcc_bilingual_reports-BUILD-CHECKLIST.md``.

Author
------

ODI — GCC partner tooling.
