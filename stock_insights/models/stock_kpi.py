# Part of Stock Insights. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools


class StockKPI(models.Model):
    """Stock KPI Dashboard Helper - SQL View Model.
    
    Aggregated KPIs for inventory dashboard:
    - Total on-hand value
    - SKU counts (total, active, dormant)
    - Stock status counts (low, out of stock, overstock, dead stock)
    - Value distribution metrics
    
    This is a read-only SQL view providing company/warehouse level aggregations.
    """
    _name = 'stock.kpi'
    _description = 'Stock KPI Dashboard'
    _auto = False
    _rec_name = 'warehouse_id'
    _order = 'company_id, warehouse_id'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        readonly=True,
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        readonly=True,
    )

    # Value KPIs
    total_stock_value = fields.Float(
        string='Total Stock Value',
        readonly=True,
        digits='Product Price',
        help='Total value of all inventory on hand',
    )
    avg_unit_cost = fields.Float(
        string='Average Unit Cost',
        readonly=True,
        digits='Product Price',
    )

    # SKU counts
    total_skus = fields.Integer(
        string='Total SKUs',
        readonly=True,
        help='Total number of unique products with stock',
    )
    active_skus = fields.Integer(
        string='Active SKUs',
        readonly=True,
        help='Products with consumption in the last 90 days',
    )
    dormant_skus = fields.Integer(
        string='Dormant SKUs',
        readonly=True,
        help='Products with no consumption in the last 90 days',
    )

    # Quantity metrics
    total_quantity = fields.Float(
        string='Total Quantity',
        readonly=True,
        digits='Product Unit of Measure',
    )

    # Stock status counts
    out_of_stock_skus = fields.Integer(
        string='Out of Stock SKUs',
        readonly=True,
        help='Products with zero or negative on-hand quantity',
    )
    low_stock_skus = fields.Integer(
        string='Low Stock SKUs',
        readonly=True,
        help='Products below reorder point or with less than 7 days coverage',
    )
    overstock_skus = fields.Integer(
        string='Overstock SKUs',
        readonly=True,
        help='Products with more than 90 days coverage',
    )
    dead_stock_skus = fields.Integer(
        string='Dead Stock SKUs',
        readonly=True,
        help='Products with no movement for more than 180 days',
    )

    # Value by stock status
    low_stock_value = fields.Float(
        string='Low Stock Value',
        readonly=True,
        digits='Product Price',
    )
    overstock_value = fields.Float(
        string='Overstock Value',
        readonly=True,
        digits='Product Price',
    )
    dead_stock_value = fields.Float(
        string='Dead Stock Value',
        readonly=True,
        digits='Product Price',
    )

    # ABC distribution
    class_a_skus = fields.Integer(
        string='Class A SKUs',
        readonly=True,
    )
    class_a_value = fields.Float(
        string='Class A Value',
        readonly=True,
        digits='Product Price',
    )
    class_b_skus = fields.Integer(
        string='Class B SKUs',
        readonly=True,
    )
    class_b_value = fields.Float(
        string='Class B Value',
        readonly=True,
        digits='Product Price',
    )
    class_c_skus = fields.Integer(
        string='Class C SKUs',
        readonly=True,
    )
    class_c_value = fields.Float(
        string='Class C Value',
        readonly=True,
        digits='Product Price',
    )

    def init(self):
        """Create or replace the SQL view for stock KPIs."""
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                %s
            )
        """ % (self._table, self._select()))

    def _select(self):
        """Build the SQL query for stock KPI aggregations."""
        return """
            WITH stock_data AS (
                SELECT
                    sq.company_id,
                    sl.warehouse_id,
                    sq.product_id,
                    SUM(sq.quantity) AS qty_on_hand,
                    pt.standard_price AS unit_cost
                FROM stock_quant sq
                JOIN stock_location sl ON sl.id = sq.location_id
                JOIN product_product pp ON pp.id = sq.product_id
                JOIN product_template pt ON pt.id = pp.product_tmpl_id
                WHERE sl.usage = 'internal'
                  AND pt.type = 'product'
                GROUP BY sq.company_id, sl.warehouse_id, sq.product_id, COALESCE((pp.standard_price->>sq.company_id::text)::numeric, 0)
                HAVING SUM(sq.quantity) != 0
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
            last_movement AS (
                SELECT
                    sm.product_id,
                    sm.company_id,
                    MAX(sm.date) AS last_move_date
                FROM stock_move sm
                WHERE sm.state = 'done'
                GROUP BY sm.product_id, sm.company_id
            ),
            product_metrics AS (
                SELECT
                    sd.company_id,
                    sd.warehouse_id,
                    sd.product_id,
                    sd.qty_on_hand,
                    sd.unit_cost,
                    sd.qty_on_hand * sd.unit_cost AS stock_value,
                    COALESCE(c90.consumed_qty, 0) AS consumed_qty_90d,
                    COALESCE(c90.consumed_qty / 90.0, 0) AS daily_consumption,
                    lm.last_move_date,
                    CASE 
                        WHEN COALESCE(c90.consumed_qty, 0) > 0 AND sd.qty_on_hand > 0 
                        THEN sd.qty_on_hand / (c90.consumed_qty / 90.0)
                        ELSE NULL 
                    END AS days_of_cover
                FROM stock_data sd
                LEFT JOIN consumption_90d c90 
                    ON c90.product_id = sd.product_id 
                    AND c90.company_id = sd.company_id
                    AND c90.warehouse_id = sd.warehouse_id
                LEFT JOIN last_movement lm 
                    ON lm.product_id = sd.product_id 
                    AND lm.company_id = sd.company_id
            ),
            orderpoint_data AS (
                SELECT
                    op.product_id,
                    op.company_id,
                    op.warehouse_id,
                    op.product_min_qty
                FROM stock_warehouse_orderpoint op
                WHERE op.active = TRUE
            )
            SELECT
                ROW_NUMBER() OVER () AS id,
                pm.company_id,
                pm.warehouse_id,
                -- Value KPIs
                SUM(pm.stock_value) AS total_stock_value,
                AVG(pm.unit_cost) AS avg_unit_cost,
                -- SKU counts
                COUNT(DISTINCT pm.product_id) AS total_skus,
                COUNT(DISTINCT CASE WHEN pm.consumed_qty_90d > 0 THEN pm.product_id END) AS active_skus,
                COUNT(DISTINCT CASE WHEN pm.consumed_qty_90d = 0 THEN pm.product_id END) AS dormant_skus,
                -- Quantity
                SUM(pm.qty_on_hand) AS total_quantity,
                -- Stock status counts
                COUNT(DISTINCT CASE WHEN pm.qty_on_hand <= 0 THEN pm.product_id END) AS out_of_stock_skus,
                COUNT(DISTINCT CASE 
                    WHEN pm.qty_on_hand > 0 AND (
                        pm.days_of_cover < 7 
                        OR pm.qty_on_hand < COALESCE(op.product_min_qty, 0)
                    ) THEN pm.product_id 
                END) AS low_stock_skus,
                COUNT(DISTINCT CASE 
                    WHEN pm.days_of_cover > 90 THEN pm.product_id 
                END) AS overstock_skus,
                COUNT(DISTINCT CASE 
                    WHEN pm.last_move_date < (CURRENT_DATE - INTERVAL '180 days') 
                         OR pm.last_move_date IS NULL 
                    THEN pm.product_id 
                END) AS dead_stock_skus,
                -- Value by status
                SUM(CASE 
                    WHEN pm.qty_on_hand > 0 AND (
                        pm.days_of_cover < 7 
                        OR pm.qty_on_hand < COALESCE(op.product_min_qty, 0)
                    ) THEN pm.stock_value 
                    ELSE 0 
                END) AS low_stock_value,
                SUM(CASE 
                    WHEN pm.days_of_cover > 90 THEN pm.stock_value 
                    ELSE 0 
                END) AS overstock_value,
                SUM(CASE 
                    WHEN pm.last_move_date < (CURRENT_DATE - INTERVAL '180 days') 
                         OR pm.last_move_date IS NULL 
                    THEN pm.stock_value 
                    ELSE 0 
                END) AS dead_stock_value,
                -- ABC placeholders (computed via join to ABC report in practice)
                0 AS class_a_skus,
                0.0 AS class_a_value,
                0 AS class_b_skus,
                0.0 AS class_b_value,
                0 AS class_c_skus,
                0.0 AS class_c_value
            FROM product_metrics pm
            LEFT JOIN orderpoint_data op 
                ON op.product_id = pm.product_id 
                AND op.company_id = pm.company_id
                AND op.warehouse_id = pm.warehouse_id
            WHERE pm.warehouse_id IS NOT NULL
            GROUP BY pm.company_id, pm.warehouse_id
        """


class StockKPIProduct(models.Model):
    """Product-level KPI detail for drill-down from dashboard.
    
    Provides detailed per-product metrics supporting the aggregated KPIs.
    """
    _name = 'stock.kpi.product'
    _description = 'Stock KPI Product Detail'
    _auto = False
    _rec_name = 'product_id'
    _order = 'stock_value desc'

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
        string='Category',
        readonly=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        readonly=True,
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        readonly=True,
    )

    qty_on_hand = fields.Float(
        string='Qty On Hand',
        readonly=True,
        digits='Product Unit of Measure',
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
    consumed_qty_90d = fields.Float(
        string='Consumed (90d)',
        readonly=True,
        digits='Product Unit of Measure',
    )
    daily_consumption = fields.Float(
        string='Daily Consumption',
        readonly=True,
        digits='Product Unit of Measure',
    )
    days_of_cover = fields.Float(
        string='Days of Cover',
        readonly=True,
    )
    last_move_date = fields.Date(
        string='Last Movement',
        readonly=True,
    )
    days_since_movement = fields.Integer(
        string='Days Since Movement',
        readonly=True,
    )
    stock_status = fields.Selection([
        ('out_of_stock', 'Out of Stock'),
        ('low_stock', 'Low Stock'),
        ('normal', 'Normal'),
        ('overstock', 'Overstock'),
        ('dead_stock', 'Dead Stock'),
    ], string='Stock Status', readonly=True)

    def init(self):
        """Create or replace the SQL view for product-level KPIs."""
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                %s
            )
        """ % (self._table, self._select()))

    def _select(self):
        """Build SQL query for product-level KPI details."""
        return """
            WITH stock_data AS (
                SELECT
                    sq.company_id,
                    sl.warehouse_id,
                    sq.product_id,
                    pp.product_tmpl_id,
                    pt.categ_id,
                    SUM(sq.quantity) AS qty_on_hand,
                    pt.standard_price AS unit_cost
                FROM stock_quant sq
                JOIN stock_location sl ON sl.id = sq.location_id
                JOIN product_product pp ON pp.id = sq.product_id
                JOIN product_template pt ON pt.id = pp.product_tmpl_id
                WHERE sl.usage = 'internal'
                  AND pt.type = 'product'
                GROUP BY sq.company_id, sl.warehouse_id, sq.product_id, 
                         pp.product_tmpl_id, pt.categ_id, COALESCE((pp.standard_price->>sq.company_id::text)::numeric, 0)
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
            last_movement AS (
                SELECT
                    sm.product_id,
                    sm.company_id,
                    MAX(sm.date)::date AS last_move_date
                FROM stock_move sm
                WHERE sm.state = 'done'
                GROUP BY sm.product_id, sm.company_id
            ),
            orderpoint_data AS (
                SELECT
                    op.product_id,
                    op.company_id,
                    op.warehouse_id,
                    op.product_min_qty
                FROM stock_warehouse_orderpoint op
                WHERE op.active = TRUE
            )
            SELECT
                ROW_NUMBER() OVER () AS id,
                sd.product_id,
                sd.product_tmpl_id,
                sd.categ_id,
                sd.company_id,
                sd.warehouse_id,
                sd.qty_on_hand,
                sd.unit_cost,
                sd.qty_on_hand * sd.unit_cost AS stock_value,
                COALESCE(c90.consumed_qty, 0) AS consumed_qty_90d,
                COALESCE(c90.consumed_qty / 90.0, 0) AS daily_consumption,
                CASE 
                    WHEN COALESCE(c90.consumed_qty, 0) > 0 AND sd.qty_on_hand > 0 
                    THEN ROUND((sd.qty_on_hand / (c90.consumed_qty / 90.0))::numeric, 1)
                    ELSE NULL 
                END AS days_of_cover,
                lm.last_move_date,
                CASE 
                    WHEN lm.last_move_date IS NOT NULL 
                    THEN (CURRENT_DATE - lm.last_move_date)
                    ELSE NULL 
                END AS days_since_movement,
                CASE
                    WHEN sd.qty_on_hand <= 0 THEN 'out_of_stock'
                    WHEN lm.last_move_date < (CURRENT_DATE - INTERVAL '180 days') 
                         OR lm.last_move_date IS NULL THEN 'dead_stock'
                    WHEN COALESCE(c90.consumed_qty, 0) > 0 
                         AND sd.qty_on_hand / (c90.consumed_qty / 90.0) > 90 THEN 'overstock'
                    WHEN sd.qty_on_hand < COALESCE(op.product_min_qty, 0)
                         OR (COALESCE(c90.consumed_qty, 0) > 0 
                             AND sd.qty_on_hand / (c90.consumed_qty / 90.0) < 7) THEN 'low_stock'
                    ELSE 'normal'
                END AS stock_status
            FROM stock_data sd
            LEFT JOIN consumption_90d c90 
                ON c90.product_id = sd.product_id 
                AND c90.company_id = sd.company_id
                AND c90.warehouse_id = sd.warehouse_id
            LEFT JOIN last_movement lm 
                ON lm.product_id = sd.product_id 
                AND lm.company_id = sd.company_id
            LEFT JOIN orderpoint_data op 
                ON op.product_id = sd.product_id 
                AND op.company_id = sd.company_id
                AND op.warehouse_id = sd.warehouse_id
            WHERE sd.warehouse_id IS NOT NULL
        """
