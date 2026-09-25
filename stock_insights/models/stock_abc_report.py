# Part of Stock Insights. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools


class StockABCReport(models.Model):
    """Stock ABC Classification Report - SQL View Model.
    
    Implements Pareto (80/20) analysis to classify products into:
    - Class A: High-value items (typically ~80% of total value, ~20% of SKUs)
    - Class B: Medium-value items (typically ~15% of value, ~30% of SKUs)  
    - Class C: Low-value items (typically ~5% of value, ~50% of SKUs)
    
    Classification is based on consumption value over the configured period.
    This is a read-only SQL view model.
    """
    _name = 'stock.abc.report'
    _description = 'Stock ABC Classification Report'
    _auto = False
    _rec_name = 'product_id'
    _order = 'cumulative_pct'

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
    default_code = fields.Char(
        string='Internal Reference',
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
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        readonly=True,
    )

    # Consumption metrics (from outbound moves in the analysis period)
    consumption_qty = fields.Float(
        string='Consumed Qty',
        readonly=True,
        digits='Product Unit of Measure',
        help='Total quantity consumed/sold in the analysis period',
    )
    unit_cost = fields.Float(
        string='Unit Cost',
        readonly=True,
        digits='Product Price',
    )
    consumption_value = fields.Float(
        string='Consumption Value',
        readonly=True,
        digits='Product Price',
        help='Total value of consumption in the analysis period',
    )

    # Current stock metrics
    qty_on_hand = fields.Float(
        string='Qty On Hand',
        readonly=True,
        digits='Product Unit of Measure',
    )
    stock_value = fields.Float(
        string='Stock Value',
        readonly=True,
        digits='Product Price',
    )

    # Classification fields
    value_pct = fields.Float(
        string='Value %',
        readonly=True,
        help='Percentage of total consumption value',
    )
    cumulative_pct = fields.Float(
        string='Cumulative %',
        readonly=True,
        help='Cumulative percentage of total consumption value',
    )
    abc_class = fields.Selection([
        ('A', 'Class A'),
        ('B', 'Class B'),
        ('C', 'Class C'),
    ], string='ABC Class', readonly=True)
    rank = fields.Integer(
        string='Rank',
        readonly=True,
        help='Product rank by consumption value (1 = highest)',
    )

    def init(self):
        """Create or replace the SQL view for ABC classification."""
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                %s
            )
        """ % (self._table, self._select()))

    def _select(self):
        """Build the SQL query for ABC classification.
        
        Calculates consumption value from outbound stock moves over the
        past 90 days (configurable via stock.insights.config), then ranks
        products and assigns ABC class based on cumulative value percentage.
        """
        return """
            WITH consumption_data AS (
                -- Calculate consumption from outbound moves (deliveries, consumption)
                SELECT
                    sm.product_id,
                    sm.company_id,
                    sw.id AS warehouse_id,
                    SUM(ABS(sm.product_qty)) AS consumption_qty
                FROM stock_move sm
                JOIN stock_location sl_src ON sl_src.id = sm.location_id
                JOIN stock_location sl_dest ON sl_dest.id = sm.location_dest_id
                LEFT JOIN stock_warehouse sw ON sw.lot_stock_id = sl_src.id 
                    OR sl_src.parent_path LIKE CONCAT('%%/', sw.lot_stock_id::text, '/%%')
                WHERE sm.state = 'done'
                  AND sl_src.usage = 'internal'
                  AND sl_dest.usage IN ('customer', 'production', 'inventory')
                  AND sm.date >= (CURRENT_DATE - INTERVAL '90 days')
                GROUP BY sm.product_id, sm.company_id, sw.id
            ),
            stock_on_hand AS (
                -- Current stock quantities by warehouse
                SELECT
                    sq.product_id,
                    sq.company_id,
                    sl.warehouse_id,
                    SUM(sq.quantity) AS qty_on_hand
                FROM stock_quant sq
                JOIN stock_location sl ON sl.id = sq.location_id
                WHERE sl.usage = 'internal'
                  AND sq.quantity > 0
                GROUP BY sq.product_id, sq.company_id, sl.warehouse_id
            ),
            product_values AS (
                -- Combine consumption with product cost
                SELECT
                    COALESCE(cd.product_id, soh.product_id) AS product_id,
                    COALESCE(cd.company_id, soh.company_id) AS company_id,
                    COALESCE(cd.warehouse_id, soh.warehouse_id) AS warehouse_id,
                    COALESCE(cd.consumption_qty, 0) AS consumption_qty,
                    COALESCE(soh.qty_on_hand, 0) AS qty_on_hand,
                    pp.product_tmpl_id,
                    pp.default_code,
                    pt.categ_id,
                    COALESCE((pp.standard_price->>COALESCE(cd.company_id, soh.company_id)::text)::numeric, 0) AS unit_cost
                FROM consumption_data cd
                FULL OUTER JOIN stock_on_hand soh 
                    ON cd.product_id = soh.product_id 
                    AND cd.company_id = soh.company_id
                    AND cd.warehouse_id = soh.warehouse_id
                JOIN product_product pp ON pp.id = COALESCE(cd.product_id, soh.product_id)
                JOIN product_template pt ON pt.id = pp.product_tmpl_id
                WHERE pt.type = 'product'
            ),
            ranked_products AS (
                SELECT
                    pv.*,
                    pv.consumption_qty * pv.unit_cost AS consumption_value,
                    pv.qty_on_hand * pv.unit_cost AS stock_value,
                    ROW_NUMBER() OVER (
                        PARTITION BY pv.company_id, pv.warehouse_id 
                        ORDER BY pv.consumption_qty * pv.unit_cost DESC
                    ) AS rank,
                    SUM(pv.consumption_qty * pv.unit_cost) OVER (
                        PARTITION BY pv.company_id, pv.warehouse_id
                    ) AS total_value
                FROM product_values pv
            ),
            classified_products AS (
                SELECT
                    rp.*,
                    CASE 
                        WHEN rp.total_value > 0 
                        THEN (rp.consumption_value / rp.total_value) * 100 
                        ELSE 0 
                    END AS value_pct,
                    CASE 
                        WHEN rp.total_value > 0 
                        THEN (SUM(rp.consumption_value) OVER (
                            PARTITION BY rp.company_id, rp.warehouse_id 
                            ORDER BY rp.consumption_value DESC
                            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                        ) / rp.total_value) * 100
                        ELSE 0 
                    END AS cumulative_pct
                FROM ranked_products rp
            )
            SELECT
                ROW_NUMBER() OVER () AS id,
                cp.product_id,
                cp.product_tmpl_id,
                cp.default_code,
                cp.categ_id,
                cp.warehouse_id,
                cp.company_id,
                cp.consumption_qty,
                cp.unit_cost,
                cp.consumption_value,
                cp.qty_on_hand,
                cp.stock_value,
                ROUND(cp.value_pct::numeric, 2) AS value_pct,
                ROUND(cp.cumulative_pct::numeric, 2) AS cumulative_pct,
                CASE
                    WHEN cp.cumulative_pct <= 80 THEN 'A'
                    WHEN cp.cumulative_pct <= 95 THEN 'B'
                    ELSE 'C'
                END AS abc_class,
                cp.rank::integer
            FROM classified_products cp
        """
