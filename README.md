# Odiflux Reporting

**Business Intelligence & Reporting Addons for Odoo 19**

A collection of professional analytics and reporting modules for Odoo Community and Enterprise editions.

## Available Modules

### 🧾 [GCC Arabic Bilingual Reports](./odi_gcc_bilingual_reports/)

Arabic/English bilingual invoices and financial statements for GCC/KSA markets:

- **Bilingual Tax Invoices** - AR/EN side-by-side statutory layout for Tax Invoices, Simplified Invoices, Credit Notes, Debit Notes
- **Arabic Master Data** - Company, partner, CoA, and product name_ar fields with EN fallback
- **Financial Statements** - Bilingual Trial Balance, P&L, Balance Sheet (Enterprise: extends account_reports; Community: PDF export)
- **QR Placement** - Renders native ZATCA QR when `l10n_sa_edi` is installed; no crash without it

**Scope:** Reports only — no EDI/ZATCA clearance, no XML generation, no CSID. Works alongside native localizations.

**[View Documentation →](./odi_gcc_bilingual_reports/README.rst)**

### 🧾 [GCC Arabic Bilingual POS Receipts](./odi_gcc_bilingual_reports_pos/) *(optional)*

Companion module for bilingual AR/EN POS receipt templates. Requires `point_of_sale`.

**[View Documentation →](./odi_gcc_bilingual_reports_pos/README.rst)**

### 📊 [Stock Insights](./stock_insights/)

Inventory Business Intelligence & Reporting module providing:

- **Stock Aging Analysis** - Track inventory age across configurable bands (0-30, 31-60, 61-90, 90+ days)
- **ABC Classification** - Pareto-based value classification for SKU prioritization
- **KPI Dashboard** - On-hand value, SKU counts, stock health indicators
- **Coverage & Reorder Analysis** - Days of cover, reorder point comparisons

**[View Documentation →](./stock_insights/README.md)**

## Installation

1. Clone this repository into your Odoo addons path:
   ```bash
   git clone https://github.com/odiflux/odiflux_reporting.git /path/to/addons/odiflux_reporting
   ```

2. Add the path to your Odoo configuration:
   ```
   addons_path = /path/to/addons/odiflux_reporting,/path/to/other/addons
   ```

3. Update the apps list and install desired modules from the Apps menu.

## Compatibility

| Module | Odoo 19 Community | Odoo 19 Enterprise | Notes |
|--------|-------------------|-------------------|-------|
| GCC Arabic Bilingual Reports | ✅ | ✅ | FS reports: Enterprise extends `account_reports`; Community uses PDF wizard |
| GCC Arabic Bilingual POS | ✅ | ✅ | Requires `point_of_sale` |
| Stock Insights | ✅ | ✅ | |

All modules are designed for Odoo 19 first. Ports to Odoo 17 and 18 are planned.

## Planned Modules

The Odiflux Reporting suite will expand to include:

| Module | Description | Status |
|--------|-------------|--------|
| GCC Arabic Bilingual Reports | AR/EN invoices & financial statements | ✅ Available |
| GCC Arabic Bilingual POS | AR/EN POS receipt companion | ✅ Available |
| Stock Insights | Inventory BI & reporting | ✅ Available |
| Sales Insights | Sales analytics & forecasting | 🔜 Planned |
| Finance Insights | Financial KPIs & reporting | 🔜 Planned |
| HR Insights | Workforce analytics | 🔜 Planned |

## License

Individual modules may have different licenses:

- **Stock Insights**: OPL-1 (Odoo Proprietary License) - suitable for commercial App Store distribution

See each module's README for specific licensing details.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request with a clear description

## Support

For issues or feature requests, please open an issue on this repository.

---

*Built for Odoo 19 with ❤️*
