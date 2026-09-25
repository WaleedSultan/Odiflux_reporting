# Part of Stock Insights. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools


class StockCoverageReport(models.Model):
    """Stock Coverage / Reorder Report - SQL View Model.
    
    Analyzes inventory coverage (days of stock) and compares current stock
    levels against reorder points (orderpoints). Helps identify:
    - Products below minimum stock levels
    - Products above maximum stock levels
    - Days of coverage based on historical consumption
    
    This is a read-only SQL view that combines stock.quant data with
    stock.warehouse.orderpoint and consumption history.
    """
    _name = 'stock.coverage.report'
    _description = 'Stock Coverage & Reorder Analysis'
    _auto = False
    _rec_name = 'product_id'
    _order = 'days_of_cover'

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

    # Current stock metrics
    qty_on_hand = fields.Float(
        string='Qty On Hand',
        readonly=True,
        digits='Product Unit of Measure',
    )
    qty_reserved = fields.Float(
        string='Qty Reserved',
        readonly=True,
        digits='Product Unit of Measure',
    )
    qty_available = fields.Float(
        string='Qty Available',
        readonly=True,
        digits='Product Unit of Measure',
        help='On hand minus reserved',
    )
    unit_cost = fields.Float(
        string='Unit Cost',
        readonly=True,
        digits='Product Price',
    )
    stock_value = fields.Float(
        string='Stock Value',
        readonly=True,
        digits='Product Price',
    )

    # Orderpoint / reorder metrics
    has_orderpoint = fields.Boolean(
        string='Has Reorder Rule',
        readonly=True,
    )
    product_min_qty = fields.Float(
        string='Min Qty (Reorder Point)',
        readonly=True,
        digits='Product Unit of Measure',
    )
    product_max_qty = fields.Float(
        string='Max Qty',
        readonly=True,
        digits='Product Unit of Measure',
    )
    qty_to_order = fields.Float(
        string='Qty to Order',
        readonly=True,
        digits='Product Unit of Measure',
        help='Suggested quantity to order to reach max',
    )

    # Coverage metrics
    consumed_qty_30d = fields.Float(
        string='Consumed (30d)',
        readonly=True,
        digits='Product Unit of Measure',
    )
    consumed_qty_90d = fields.Float(
        string='Consumed (90d)',
        readonly=True,
        digits='Product Unit of Measure',
    )
    avg_daily_consumption = fields.Float(
        string='Avg Daily Consumption',
        readonly=True,
        digits='Product Unit of Measure',
        help='Based on 90-day consumption',
    )
    days_of_cover = fields.Float(
        string='Days of Cover',
        readonly=True,
        help='Estimated days until stockout based on consumption rate',
    )

    # Status indicators
    below_min = fields.Boolean(
        string='Below Minimum',
        readonly=True,
        help='Current stock is below the reorder point',
    )
    above_max = fields.Boolean(
        string='Above Maximum',
        readonly=True,
        help='Current stock exceeds the maximum quantity',
    )
    coverage_status = fields.Selection([
        ('critical', 'Critical (< 7 days)'),
        ('low', 'Low (7-14 days)'),
        ('normal', 'Normal (14-60 days)'),
        ('high', 'High (60-90 days)'),
        ('excess', 'Excess (> 90 days)'),
        ('no_consumption', 'No Consumption Data'),
    ], string='Coverage Status', readonly=True)

    # Incoming/outgoing
    incoming_qty = fields.Float(
        string='Incoming Qty',
        readonly=True,
        digits='Product Unit of Measure',
        help='Quantity in confirmed incoming transfers/POs',
    )
    outgoing_qty = fields.Float(
        string='Outgoing Qty',
        readonly=True,
        digits='Product Unit of Measure',
        help='Quantity in confirmed outgoing transfers/SOs',
    )
    forecasted_qty = fields.Float(
        string='Forecasted Qty',
        readonly=True,
        digits='Product Unit of Measure',
        help='On hand + incoming - outgoing',
    )

    def init(self):
        """Create or replace the SQL view for coverage analysis."""
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                %s
            )
        """ % (self._table, self._select()))

    def _select(self):
        """Build SQL query for stock coverage/reorder analysis."""
        return """
            WITH stock_on_hand AS (
                SELECT
                    sq.product_id,
                    sq.company_id,
                    sl.warehouse_id,
                    sq.location_id,
                    SUM(sq.quantity) AS qty_on_hand,
                    SUM(sq.reserved_quantity) AS qty_reserved
                FROM stock_quant sq
                JOIN stock_location sl ON sl.id = sq.location_id
                WHERE sl.usage = 'internal'
                GROUP BY sq.product_id, sq.company_id, sl.warehouse_id, sq.location_id
            ),
            consumption_30d AS (
                SELECT
                    sm.product_id,
                    sm.company_id,
                    COALESCE(sw.id, sl_src.warehouse_id) AS warehouse_id,
                    SUM(ABS(sm.product_qty)) AS consumed_qty
                FROM stock_move sm
                JOIN stock_location sl_src ON sl_src.id = sm.location_id
                JOIN stock_location sl_dest ON sl_dest.id = sm.location_dest_id
                LEFT JOIN stock_warehouse sw ON sw.lot_stock_id = sl_src.id
                WHERE sm.state = 'done'
                  AND sl_src.usage = 'internal'
                  AND sl_dest.usage IN ('customer', 'production', 'inventory')
                  AND sm.date >= (CURRENT_DATE - INTERVAL '30 days')
                GROUP BY sm.product_id, sm.company_id, COALESCE(sw.id, sl_src.warehouse_id)
            ),
            consumption_90d AS (
                SELECT
                    sm.product_id,
                    sm.company_id,
                    COALESCE(sw.id, sl_src.warehouse_id) AS warehouse_id,
                    SUM(ABS(sm.product_qty)) AS consumed_qty
                FROM stock_move sm
                JOIN stock_location sl_src ON sl_src.id = sm.location_id
                JOIN stock_location sl_dest ON sl_dest.id = sm.location_dest_id
                LEFT JOIN stock_warehouse sw ON sw.lot_stock_id = sl_src.id
                WHERE sm.state = 'done'
                  AND sl_src.usage = 'internal'
                  AND sl_dest.usage IN ('customer', 'production', 'inventory')
                  AND sm.date >= (CURRENT_DATE - INTERVAL '90 days')
                GROUP BY sm.product_id, sm.company_id, COALESCE(sw.id, sl_src.warehouse_id)
            ),
            incoming AS (
                SELECT
                    sm.product_id,
                    sm.company_id,
                    COALESCE(sw.id, sl_dest.warehouse_id) AS warehouse_id,
                    SUM(sm.product_qty) AS incoming_qty
                FROM stock_move sm
                JOIN stock_location sl_src ON sl_src.id = sm.location_id
                JOIN stock_location sl_dest ON sl_dest.id = sm.location_dest_id
                LEFT JOIN stock_warehouse sw ON sw.lot_stock_id = sl_dest.id
                WHERE sm.state IN ('assigned', 'confirmed', 'waiting')
                  AND sl_src.usage IN ('supplier', 'transit')
                  AND sl_dest.usage = 'internal'
                GROUP BY sm.product_id, sm.company_id, COALESCE(sw.id, sl_dest.warehouse_id)
            ),
            outgoing AS (
                SELECT
                    sm.product_id,
                    sm.company_id,
                    COALESCE(sw.id, sl_src.warehouse_id) AS warehouse_id,
                    SUM(sm.product_qty) AS outgoing_qty
                FROM stock_move sm
                JOIN stock_location sl_src ON sl_src.id = sm.location_id
                JOIN stock_location sl_dest ON sl_dest.id = sm.location_dest_id
                LEFT JOIN stock_warehouse sw ON sw.lot_stock_id = sl_src.id
                WHERE sm.state IN ('assigned', 'confirmed', 'waiting')
                  AND sl_src.usage = 'internal'
                  AND sl_dest.usage IN ('customer', 'production')
                GROUP BY sm.product_id, sm.company_id, COALESCE(sw.id, sl_src.warehouse_id)
            ),
            orderpoints AS (
                SELECT
                    op.product_id,
                    op.company_id,
                    op.warehouse_id,
                    op.location_id,
                    op.product_min_qty,
                    op.product_max_qty
                FROM stock_warehouse_orderpoint op
                WHERE op.active = TRUE
            )
            SELECT
                ROW_NUMBER() OVER () AS id,
                soh.product_id,
                pp.product_tmpl_id,
                pp.default_code,
                pt.categ_id,
                soh.warehouse_id,
                soh.location_id,
                soh.company_id,
                -- Current stock
                soh.qty_on_hand,
                soh.qty_reserved,
                soh.qty_on_hand - soh.qty_reserved AS qty_available,
                COALESCE((pp.standard_price->>soh.company_id::text)::numeric, 0) AS unit_cost,
                soh.qty_on_hand * COALESCE((pp.standard_price->>soh.company_id::text)::numeric, 0) AS stock_value,
                -- Orderpoint
                op.product_min_qty IS NOT NULL AS has_orderpoint,
                COALESCE(op.product_min_qty, 0) AS product_min_qty,
                COALESCE(op.product_max_qty, 0) AS product_max_qty,
                GREATEST(0, COALESCE(op.product_max_qty, 0) - soh.qty_on_hand) AS qty_to_order,
                -- Consumption
                COALESCE(c30.consumed_qty, 0) AS consumed_qty_30d,
                COALESCE(c90.consumed_qty, 0) AS consumed_qty_90d,
                COALESCE(c90.consumed_qty / 90.0, 0) AS avg_daily_consumption,
                CASE 
                    WHEN COALESCE(c90.consumed_qty, 0) > 0 
                    THEN ROUND((soh.qty_on_hand / (c90.consumed_qty / 90.0))::numeric, 1)
                    ELSE NULL 
                END AS days_of_cover,
                -- Status indicators
                soh.qty_on_hand < COALESCE(op.product_min_qty, 0) AS below_min,
                soh.qty_on_hand > COALESCE(op.product_max_qty, soh.qty_on_hand) 
                    AND op.product_max_qty IS NOT NULL AS above_max,
                CASE
                    WHEN COALESCE(c90.consumed_qty, 0) = 0 THEN 'no_consumption'
                    WHEN soh.qty_on_hand / (c90.consumed_qty / 90.0) < 7 THEN 'critical'
                    WHEN soh.qty_on_hand / (c90.consumed_qty / 90.0) < 14 THEN 'low'
                    WHEN soh.qty_on_hand / (c90.consumed_qty / 90.0) < 60 THEN 'normal'
                    WHEN soh.qty_on_hand / (c90.consumed_qty / 90.0) < 90 THEN 'high'
                    ELSE 'excess'
                END AS coverage_status,
                -- Forecasted
                COALESCE(inc.incoming_qty, 0) AS incoming_qty,
                COALESCE(outg.outgoing_qty, 0) AS outgoing_qty,
                soh.qty_on_hand + COALESCE(inc.incoming_qty, 0) - COALESCE(outg.outgoing_qty, 0) AS forecasted_qty
            FROM stock_on_hand soh
            JOIN product_product pp ON pp.id = soh.product_id
            JOIN product_template pt ON pt.id = pp.product_tmpl_id
            LEFT JOIN consumption_30d c30 
                ON c30.product_id = soh.product_id 
                AND c30.company_id = soh.company_id
                AND c30.warehouse_id = soh.warehouse_id
            LEFT JOIN consumption_90d c90 
                ON c90.product_id = soh.product_id 
                AND c90.company_id = soh.company_id
                AND c90.warehouse_id = soh.warehouse_id
            LEFT JOIN orderpoints op 
                ON op.product_id = soh.product_id 
                AND op.company_id = soh.company_id
                AND op.warehouse_id = soh.warehouse_id
                AND op.location_id = soh.location_id
            LEFT JOIN incoming inc 
                ON inc.product_id = soh.product_id 
                AND inc.company_id = soh.company_id
                AND inc.warehouse_id = soh.warehouse_id
            LEFT JOIN outgoing outg 
                ON outg.product_id = soh.product_id 
                AND outg.company_id = soh.company_id
                AND outg.warehouse_id = soh.warehouse_id
            WHERE pt.type = 'product'
              AND soh.warehouse_id IS NOT NULL
        """
