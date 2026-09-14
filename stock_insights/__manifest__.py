# Part of Stock Insights. See LICENSE file for full copyright and licensing details.
{
    'name': 'Stock Insights',
    'version': '19.0.1.0.0',
    'category': 'Inventory',
    'summary': 'BI & Reporting for Inventory: Aging, ABC, KPIs, Coverage',
    'description': """
Stock Insights - Inventory Business Intelligence
=================================================

A comprehensive analytics and reporting module for Odoo Inventory that provides
read-only insights into your stock performance without modifying inventory data.

Features:
- **Stock Aging Analysis**: Track inventory age across configurable bands (0-30, 31-60, 61-90, 90+ days)
- **ABC Classification**: Pareto-based value classification (A/B/C) for SKU prioritization
- **Dashboard KPIs**: On-hand value, SKU counts, low/out/over/dead stock indicators
- **Coverage Analysis**: Days of cover, reorder point vs. actual stock comparison

All reports support filtering by warehouse, location, product category, and company.
    """,
    'author': 'Stock Insights Contributors',
    'website': 'https://github.com/odiflux/odiflux_reporting',
    'license': 'OPL-1',
    'depends': [
        'stock',
        'stock_account',
    ],
    'data': [
        # Security
        'security/stock_insights_security.xml',
        'security/ir.model.access.csv',
        # Data
        'data/stock_insights_data.xml',
        # Views
        'views/stock_insights_config_views.xml',
        'views/stock_aging_report_views.xml',
        'views/stock_abc_report_views.xml',
        'views/stock_kpi_views.xml',
        'views/stock_coverage_report_views.xml',
        'views/stock_insights_menus.xml',
    ],
    'demo': [
        'data/stock_insights_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'stock_insights/static/src/css/stock_insights.css',
        ],
    },
    'images': [
        'static/description/banner.png',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
