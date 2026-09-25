# Part of Stock Insights. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools


class StockAgingReport(models.Model):
    """Stock Aging Report - SQL View Model.
    
    Analyzes inventory age based on the date stock was received. Groups
    products into configurable aging bands (default: 0-30, 31-60, 61-90, 90+ days).
    
    This is a read-only SQL view that aggregates data from stock.quant
    and stock.move.line to calculate the age of inventory.
    """
    _name = 'stock.aging.report'
    _description = 'Stock Aging Report'
    _auto = False
    _rec_name = 'product_id'
    _order = 'total_value desc'

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        readonly=True,
    )
    product_tmpl_id = fields.Many2one(
        'product.template',
        string='Product Template',
        readonly=True,
    )
    categ_id = fields.Many2one(
        'product.category',
        string='Product Category',
        readonly=True,
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        readonly=True,
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Location',
        readonly=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        readonly=True,
    )
    lot_id = fields.Many2one(
        'stock.lot',
        string='Lot/Serial',
        readonly=True,
    )

    quantity = fields.Float(
        string='Quantity',
        readonly=True,
        digits='Product Unit of Measure',
    )
    unit_cost = fields.Float(
        string='Unit Cost',
        readonly=True,
        digits='Product Price',
    )
    total_value = fields.Float(
        string='Total Value',
        readonly=True,
        digits='Product Price',
    )

    stock_age_days = fields.Integer(
        string='Age (Days)',
        readonly=True,
        help='Number of days since stock was received',
    )
    aging_band = fields.Selection([
        ('0_30', '0-30 Days'),
        ('31_60', '31-60 Days'),
        ('61_90', '61-90 Days'),
        ('90_plus', '90+ Days'),
    ], string='Aging Band', readonly=True)

    band_0_30_qty = fields.Float(
        string='0-30 Days Qty',
        readonly=True,
        digits='Product Unit of Measure',
    )
    band_31_60_qty = fields.Float(
        string='31-60 Days Qty',
        readonly=True,
        digits='Product Unit of Measure',
    )
    band_61_90_qty = fields.Float(
        string='61-90 Days Qty',
        readonly=True,
        digits='Product Unit of Measure',
    )
    band_90_plus_qty = fields.Float(
        string='90+ Days Qty',
        readonly=True,
        digits='Product Unit of Measure',
    )

    band_0_30_value = fields.Float(
        string='0-30 Days Value',
        readonly=True,
        digits='Product Price',
    )
    band_31_60_value = fields.Float(
        string='31-60 Days Value',
        readonly=True,
        digits='Product Price',
    )
    band_61_90_value = fields.Float(
        string='61-90 Days Value',
        readonly=True,
        digits='Product Price',
    )
    band_90_plus_value = fields.Float(
        string='90+ Days Value',
        readonly=True,
        digits='Product Price',
    )

    def init(self):
        """Create or replace the SQL view for stock aging analysis."""
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                %s
            )
        """ % (self._table, self._select()))

    def _select(self):
        """Build the SQL query for the stock aging report.
        
        The query calculates inventory age based on:
        1. For lot-tracked products: lot creation date or first incoming move
        2. For non-lot products: weighted average age from incoming moves
        
        Falls back to inventory_date or quant create date when move data unavailable.
        """
        return """
            WITH quant_ages AS (
                SELECT
                    sq.id AS quant_id,
                    sq.product_id,
                    sq.location_id,
                    sq.lot_id,
                    sq.quantity,
                    sq.company_id,
                    COALESCE(
                        -- For lots, use lot create date
                        sl.create_date::date,
                        -- Otherwise estimate from recent incoming moves
                        (
                            SELECT MAX(sm.date)::date
                            FROM stock_move sm
                            JOIN stock_move_line sml ON sml.move_id = sm.id
                            WHERE sml.product_id = sq.product_id
                              AND sml.location_dest_id = sq.location_id
                              AND sm.state = 'done'
                              AND sml.lot_id IS NOT DISTINCT FROM sq.lot_id
                        ),
                        -- Fallback to quant inventory date or create date
                        sq.inventory_date,
                        sq.create_date::date
                    ) AS receipt_date
                FROM stock_quant sq
                LEFT JOIN stock_lot sl ON sl.id = sq.lot_id
                WHERE sq.quantity > 0
            ),
            aged_quants AS (
                SELECT
                    qa.quant_id,
                    qa.product_id,
                    qa.location_id,
                    qa.lot_id,
                    qa.quantity,
                    qa.company_id,
                    qa.receipt_date,
                    GREATEST(0, CURRENT_DATE - qa.receipt_date) AS stock_age_days
                FROM quant_ages qa
            )
            SELECT
                aq.quant_id AS id,
                aq.product_id,
                pp.product_tmpl_id,
                pt.categ_id,
                sl.warehouse_id,
                aq.location_id,
                aq.company_id,
                aq.lot_id,
                aq.quantity,
                pt.standard_price AS unit_cost,
                aq.quantity * pt.standard_price AS total_value,
                aq.stock_age_days,
                CASE
                    WHEN aq.stock_age_days <= 30 THEN '0_30'
                    WHEN aq.stock_age_days <= 60 THEN '31_60'
                    WHEN aq.stock_age_days <= 90 THEN '61_90'
                    ELSE '90_plus'
                END AS aging_band,
                -- Band quantities
                CASE WHEN aq.stock_age_days <= 30 THEN aq.quantity ELSE 0 END AS band_0_30_qty,
                CASE WHEN aq.stock_age_days > 30 AND aq.stock_age_days <= 60 THEN aq.quantity ELSE 0 END AS band_31_60_qty,
                CASE WHEN aq.stock_age_days > 60 AND aq.stock_age_days <= 90 THEN aq.quantity ELSE 0 END AS band_61_90_qty,
                CASE WHEN aq.stock_age_days > 90 THEN aq.quantity ELSE 0 END AS band_90_plus_qty,
                -- Band values
                CASE WHEN aq.stock_age_days <= 30 THEN aq.quantity * pt.standard_price ELSE 0 END AS band_0_30_value,
                CASE WHEN aq.stock_age_days > 30 AND aq.stock_age_days <= 60 THEN aq.quantity * pt.standard_price ELSE 0 END AS band_31_60_value,
                CASE WHEN aq.stock_age_days > 60 AND aq.stock_age_days <= 90 THEN aq.quantity * pt.standard_price ELSE 0 END AS band_61_90_value,
                CASE WHEN aq.stock_age_days > 90 THEN aq.quantity * pt.standard_price ELSE 0 END AS band_90_plus_value
            FROM aged_quants aq
            JOIN product_product pp ON pp.id = aq.product_id
            JOIN product_template pt ON pt.id = pp.product_tmpl_id
            JOIN stock_location sl ON sl.id = aq.location_id
            WHERE sl.usage = 'internal'
        """
