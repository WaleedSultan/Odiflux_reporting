# Stock Insights

**Inventory Business Intelligence & Reporting for Odoo 19**

[![License: OPL-1](https://img.shields.io/badge/License-OPL--1-blue.svg)](https://www.odoo.com/documentation/19.0/legal/licenses.html#odoo-proprietary-license-v1-0)
[![Odoo Version](https://img.shields.io/badge/Odoo-19.0-purple.svg)](https://www.odoo.com)

Transform your inventory data into actionable insights. Stock Insights provides comprehensive analytics and reporting for your Odoo inventory without modifying any stock data.

## Features

### 📈 Stock Aging Analysis
Track inventory age across configurable bands:
- **0-30 days**: Fresh stock
- **31-60 days**: Aging inventory
- **61-90 days**: Old stock
- **90+ days**: Slow-moving / obsolete

Identify slow-moving inventory before it becomes a carrying cost problem.

### 🔤 ABC Classification
Pareto (80/20) analysis for inventory prioritization:
- **Class A**: High-value items (~80% of value, ~20% of SKUs)
- **Class B**: Medium-value items (~15% of value)
- **Class C**: Low-value items (~5% of value)

Focus your resources on the products that matter most.

### 📊 KPI Dashboard
At-a-glance inventory health metrics:
- Total stock value by warehouse
- Active vs. dormant SKU counts
- Out-of-stock alerts
- Low stock warnings
- Overstock identification
- Dead stock indicators

### 📋 Coverage & Reorder Analysis
Days of cover and reorder point comparison:
- Stock coverage (estimated days until stockout)
- Below minimum quantity indicators
- Above maximum quantity alerts
- Incoming/outgoing and forecasted quantities

## Installation

1. Place the `stock_insights` folder in your Odoo addons path
2. Update the apps list: *Apps → Update Apps List*
3. Search for "Stock Insights" and click **Install**
4. Access via the Stock Insights app or *Inventory → Reporting → Stock Insights*

### Dependencies
- `stock` (Inventory module)
- `stock_account` (Inventory Accounting)

No Enterprise-only dependencies required.

## Configuration

Navigate to *Stock Insights → Configuration → Settings* to customize:

### Aging Bands
Configure the day thresholds for aging classification (default: 30, 60, 90 days).

### ABC Thresholds
Set the cumulative value percentages for ABC classification (default: 80% for A, 95% for A+B).

### Stock Level Thresholds
- **Low Stock Days**: Products with less coverage are flagged (default: 7 days)
- **Overstock Days**: Products with more coverage are flagged (default: 90 days)
- **Dead Stock Days**: Products with no movement are flagged (default: 180 days)

## Security Groups

| Group | Access |
|-------|--------|
| **Analyst** | Read-only access to all reports and dashboards |
| **Manager** | Full access including configuration settings |

Multi-company record rules ensure proper data isolation.

## Report Views

All reports include multiple view types:

| View | Purpose |
|------|---------|
| **List** | Detailed line-by-line data with sorting and export |
| **Pivot** | Multi-dimensional analysis with drag-and-drop grouping |
| **Graph** | Visual charts (bar, pie, line) for presentations |

### Filtering Options
- Warehouse
- Location
- Product Category
- Company (multi-company)
- Status-based filters (low stock, overstock, etc.)

## Technical Notes

### SQL Views
The report models use `_auto = False` to create PostgreSQL views rather than tables. This ensures:
- Real-time data (no sync lag)
- No additional storage overhead
- Efficient aggregation using database engine

### Odoo 19 Compatibility
This module is fully compatible with Odoo 19, which removed `stock.valuation.layer`.
Inventory valuation is now derived from `product.product.standard_price` (variant cost)
rather than the deprecated valuation layer model.

### Read-Only Design
Stock Insights is designed for analytics only. It does not:
- Create or modify stock moves
- Change inventory quantities
- Alter reorder rules
- Write to any stock tables

## License

This module is licensed under the **Odoo Proprietary License v1.0 (OPL-1)**.

For commercial use and App Store distribution. See the [Odoo Licensing Documentation](https://www.odoo.com/documentation/19.0/legal/licenses.html#odoo-proprietary-license-v1-0) for details.

If you prefer open-source licensing, the module structure is compatible with LGPL-3 with minimal changes to the manifest.

## Compatibility

- ✅ Odoo 19 Community Edition
- ✅ Odoo 19 Enterprise Edition
- ✅ Multi-company environments
- ✅ Multi-warehouse configurations

## Roadmap

This module is part of the planned **Insights Suite**:

- 📊 **Stock Insights** (this module) - Inventory BI & reporting
- 📈 **Sales Insights** - Sales analytics, trends, and forecasting
- 💰 **Finance Insights** - Financial KPIs and reporting
- 👥 **HR Insights** - Workforce analytics and metrics

## Support

For issues, feature requests, or contributions, please open an issue on the repository.

## Changelog

### 19.0.1.0.0 (Initial Release)
- Stock Aging Report with configurable bands
- ABC Classification with Pareto analysis
- KPI Dashboard with stock health metrics
- Coverage & Reorder Analysis
- Multi-company and multi-warehouse support
- Security groups (Analyst/Manager)
