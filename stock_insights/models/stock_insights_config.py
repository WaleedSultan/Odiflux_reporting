# Part of Stock Insights. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StockInsightsConfig(models.Model):
    """Configuration settings for Stock Insights module.
    
    Stores company-specific thresholds for aging bands, ABC classification,
    and low/overstock detection.
    """
    _name = 'stock.insights.config'
    _description = 'Stock Insights Configuration'
    _rec_name = 'company_id'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        ondelete='cascade',
    )

    # Aging band thresholds (in days)
    aging_band_1 = fields.Integer(
        string='Aging Band 1 (Days)',
        default=30,
        help='Upper limit for the first aging band (e.g., 0-30 days)',
    )
    aging_band_2 = fields.Integer(
        string='Aging Band 2 (Days)',
        default=60,
        help='Upper limit for the second aging band (e.g., 31-60 days)',
    )
    aging_band_3 = fields.Integer(
        string='Aging Band 3 (Days)',
        default=90,
        help='Upper limit for the third aging band (e.g., 61-90 days). Above this is considered 90+ days.',
    )

    # ABC classification thresholds (cumulative percentage)
    abc_class_a_threshold = fields.Float(
        string='Class A Threshold (%)',
        default=80.0,
        help='Cumulative value percentage for Class A items (top products by value)',
    )
    abc_class_b_threshold = fields.Float(
        string='Class B Threshold (%)',
        default=95.0,
        help='Cumulative value percentage for Class B items (A + B combined)',
    )

    # Low/overstock thresholds
    low_stock_days = fields.Integer(
        string='Low Stock Days',
        default=7,
        help='Products with less than this many days of coverage are considered low stock',
    )
    overstock_days = fields.Integer(
        string='Overstock Days',
        default=90,
        help='Products with more than this many days of coverage are considered overstock',
    )
    dead_stock_days = fields.Integer(
        string='Dead Stock Days',
        default=180,
        help='Products with no movement for this many days are considered dead stock',
    )

    # Consumption calculation period
    consumption_period_days = fields.Integer(
        string='Consumption Period (Days)',
        default=90,
        help='Number of days to look back when calculating average daily consumption',
    )

    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('company_uniq', 'unique(company_id)', 'Configuration already exists for this company.'),
        ('aging_bands_positive', 'CHECK(aging_band_1 > 0 AND aging_band_2 > aging_band_1 AND aging_band_3 > aging_band_2)',
         'Aging bands must be positive and in ascending order.'),
        ('abc_thresholds_valid', 'CHECK(abc_class_a_threshold > 0 AND abc_class_a_threshold < abc_class_b_threshold AND abc_class_b_threshold <= 100)',
         'ABC thresholds must be between 0 and 100, with A < B.'),
        ('stock_days_positive', 'CHECK(low_stock_days > 0 AND overstock_days > low_stock_days AND dead_stock_days > overstock_days)',
         'Stock day thresholds must be positive and in ascending order.'),
    ]

    @api.model
    def get_config(self, company_id=None):
        """Get or create configuration for the specified company.
        
        Args:
            company_id: Company ID. If None, uses current company.
            
        Returns:
            stock.insights.config record
        """
        if company_id is None:
            company_id = self.env.company.id
        
        config = self.search([('company_id', '=', company_id)], limit=1)
        if not config:
            config = self.create({'company_id': company_id})
        return config

    def action_reset_defaults(self):
        """Reset all thresholds to default values."""
        self.ensure_one()
        self.write({
            'aging_band_1': 30,
            'aging_band_2': 60,
            'aging_band_3': 90,
            'abc_class_a_threshold': 80.0,
            'abc_class_b_threshold': 95.0,
            'low_stock_days': 7,
            'overstock_days': 90,
            'dead_stock_days': 180,
            'consumption_period_days': 90,
        })
        return True
