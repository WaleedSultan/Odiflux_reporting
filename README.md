# Odiflux Reporting

**Business Intelligence & Reporting Addons for Odoo 19**

A collection of professional analytics and reporting modules for Odoo Community and Enterprise editions.

## Available Modules

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

| Module | Odoo 19 Community | Odoo 19 Enterprise |
|--------|-------------------|-------------------|
| Stock Insights | ✅ | ✅ |

All modules are designed to work on both Community and Enterprise editions without requiring Enterprise-only dependencies.

## Planned Modules

The Odiflux Reporting suite will expand to include:

| Module | Description | Status |
|--------|-------------|--------|
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
