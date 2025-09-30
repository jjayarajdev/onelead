-- ========================================
-- LS_SKU INTEGRATION SCHEMA ENHANCEMENTS
-- HPE OneLead Database Schema Extensions
-- ========================================

-- ========================================
-- NEW DIMENSION TABLES
-- ========================================

-- LS_SKU Product Catalog
CREATE TABLE IF NOT EXISTS dim_ls_sku_product (
    ls_product_key INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name VARCHAR(100) UNIQUE NOT NULL,
    product_category VARCHAR(50) NOT NULL,
    product_type VARCHAR(50),
    description TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- LS_SKU Service Catalog with SKU codes
CREATE TABLE IF NOT EXISTS dim_ls_sku_service (
    ls_service_key INTEGER PRIMARY KEY AUTOINCREMENT,
    service_name VARCHAR(255) NOT NULL,
    service_text TEXT,
    service_type VARCHAR(50),
    service_category VARCHAR(100),
    priority INTEGER DEFAULT 3,
    has_sku BOOLEAN DEFAULT FALSE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SKU Code Reference Table
CREATE TABLE IF NOT EXISTS dim_sku_code (
    sku_key INTEGER PRIMARY KEY AUTOINCREMENT,
    sku_code VARCHAR(50) UNIQUE NOT NULL,
    sku_description TEXT,
    sku_type VARCHAR(50),
    service_credits INTEGER,
    is_fixed_sku BOOLEAN DEFAULT FALSE,
    is_flex_sku BOOLEAN DEFAULT FALSE,
    is_contractual_sku BOOLEAN DEFAULT FALSE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- MAPPING TABLES
-- ========================================

-- Product-to-Service Mapping (from LS_SKU)
CREATE TABLE IF NOT EXISTS map_product_service_sku (
    mapping_key INTEGER PRIMARY KEY AUTOINCREMENT,
    ls_product_key INTEGER NOT NULL,
    ls_service_key INTEGER NOT NULL,
    priority INTEGER DEFAULT 3,
    confidence_score DECIMAL(5,2) DEFAULT 100.00,
    mapping_source VARCHAR(50) DEFAULT 'ls_sku',
    is_active BOOLEAN DEFAULT TRUE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ls_product_key) REFERENCES dim_ls_sku_product(ls_product_key),
    FOREIGN KEY (ls_service_key) REFERENCES dim_ls_sku_service(ls_service_key),
    UNIQUE(ls_product_key, ls_service_key)
);

-- Service-to-SKU Mapping (many-to-many)
CREATE TABLE IF NOT EXISTS map_service_sku (
    service_sku_key INTEGER PRIMARY KEY AUTOINCREMENT,
    ls_service_key INTEGER NOT NULL,
    sku_key INTEGER NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ls_service_key) REFERENCES dim_ls_sku_service(ls_service_key),
    FOREIGN KEY (sku_key) REFERENCES dim_sku_code(sku_key),
    UNIQUE(ls_service_key, sku_key)
);

-- Install Base Product to LS_SKU Product Matching
CREATE TABLE IF NOT EXISTS map_install_base_to_ls_sku (
    match_key INTEGER PRIMARY KEY AUTOINCREMENT,
    product_key INTEGER NOT NULL,
    ls_product_key INTEGER,
    confidence_score DECIMAL(5,2),
    confidence_level VARCHAR(20),
    match_method VARCHAR(50),
    matched_category VARCHAR(50),
    is_verified BOOLEAN DEFAULT FALSE,
    verified_by VARCHAR(100),
    verified_date TIMESTAMP,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
    FOREIGN KEY (ls_product_key) REFERENCES dim_ls_sku_product(ls_product_key),
    UNIQUE(product_key)
);

-- ========================================
-- ENHANCED FACT TABLES
-- ========================================

-- Service Recommendations Fact Table
CREATE TABLE IF NOT EXISTS fact_service_recommendation (
    recommendation_key INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_key INTEGER,
    product_key INTEGER,
    opportunity_key INTEGER,
    ls_service_key INTEGER NOT NULL,
    recommendation_date DATE NOT NULL,
    recommendation_score DECIMAL(5,2),
    recommendation_reason TEXT,
    recommendation_type VARCHAR(50),
    priority INTEGER DEFAULT 3,
    status VARCHAR(50) DEFAULT 'pending',
    quote_generated BOOLEAN DEFAULT FALSE,
    quote_date DATE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
    FOREIGN KEY (opportunity_key) REFERENCES fact_opportunity(opportunity_key),
    FOREIGN KEY (ls_service_key) REFERENCES dim_ls_sku_service(ls_service_key)
);

-- ========================================
-- ANALYTICAL VIEWS
-- ========================================

-- Product Service Recommendations View
CREATE VIEW IF NOT EXISTS v_product_service_recommendations AS
SELECT
    p.product_serial_number,
    p.product_description,
    p.product_platform,
    lp.product_name as ls_sku_product,
    lp.product_category as ls_sku_category,
    ls.service_name,
    ls.service_type,
    ls.priority,
    GROUP_CONCAT(sk.sku_code, ', ') as sku_codes,
    m.confidence_score as match_confidence,
    m.match_method
FROM dim_product p
LEFT JOIN map_install_base_to_ls_sku m ON p.product_key = m.product_key
LEFT JOIN dim_ls_sku_product lp ON m.ls_product_key = lp.ls_product_key
LEFT JOIN map_product_service_sku ps ON lp.ls_product_key = ps.ls_product_key
LEFT JOIN dim_ls_sku_service ls ON ps.ls_service_key = ls.ls_service_key
LEFT JOIN map_service_sku msk ON ls.ls_service_key = msk.ls_service_key
LEFT JOIN dim_sku_code sk ON msk.sku_key = sk.sku_key
GROUP BY p.product_key, ls.ls_service_key;

-- Customer Service Opportunity View
CREATE VIEW IF NOT EXISTS v_customer_service_opportunities AS
SELECT
    c.customer_name,
    c.customer_id_5digit,
    COUNT(DISTINCT ib.product_key) as total_products,
    COUNT(DISTINCT CASE WHEN ib.days_to_eol < 0 THEN ib.product_key END) as expired_products,
    COUNT(DISTINCT CASE WHEN ib.days_to_eol BETWEEN 0 AND 180 THEN ib.product_key END) as expiring_soon,
    COUNT(DISTINCT ps.ls_service_key) as recommended_services,
    COUNT(DISTINCT sk.sku_key) as available_skus,
    GROUP_CONCAT(DISTINCT ls.service_type) as service_types
FROM dim_customer c
JOIN fact_install_base ib ON c.customer_key = ib.customer_key
JOIN dim_product p ON ib.product_key = p.product_key
LEFT JOIN map_install_base_to_ls_sku m ON p.product_key = m.product_key
LEFT JOIN dim_ls_sku_product lp ON m.ls_product_key = lp.ls_product_key
LEFT JOIN map_product_service_sku ps ON lp.ls_product_key = ps.ls_product_key
LEFT JOIN dim_ls_sku_service ls ON ps.ls_service_key = ls.ls_service_key
LEFT JOIN map_service_sku msk ON ls.ls_service_key = msk.ls_service_key
LEFT JOIN dim_sku_code sk ON msk.sku_key = sk.sku_key
GROUP BY c.customer_key;

-- Expired Product Service Mapping View
CREATE VIEW IF NOT EXISTS v_expired_product_service_mapping AS
SELECT
    c.customer_name,
    p.product_description,
    p.product_platform,
    ib.support_status,
    ib.days_to_eol,
    lp.product_name as ls_sku_product,
    ls.service_name,
    ls.service_type,
    ls.priority,
    sk.sku_code,
    sk.service_credits,
    'Expired - Urgent Action' as urgency_level
FROM fact_install_base ib
JOIN dim_customer c ON ib.customer_key = c.customer_key
JOIN dim_product p ON ib.product_key = p.product_key
LEFT JOIN map_install_base_to_ls_sku m ON p.product_key = m.product_key
LEFT JOIN dim_ls_sku_product lp ON m.ls_product_key = lp.ls_product_key
LEFT JOIN map_product_service_sku ps ON lp.ls_product_key = ps.ls_product_key
LEFT JOIN dim_ls_sku_service ls ON ps.ls_service_key = ls.ls_service_key
LEFT JOIN map_service_sku msk ON ls.ls_service_key = msk.ls_service_key
LEFT JOIN dim_sku_code sk ON msk.sku_key = sk.sku_key
WHERE ib.days_to_eol < 0
  AND ls.priority = 1
ORDER BY c.customer_name, ls.priority, ls.service_name;

-- Service Credit Burn-Down Opportunities View
CREATE VIEW IF NOT EXISTS v_credit_burndown_opportunities AS
SELECT
    c.customer_name,
    sc.contract_id,
    sc.purchased_credits,
    sc.delivered_credits,
    sc.active_credits,
    sc.utilization_rate,
    sc.contract_end_date,
    JULIANDAY(sc.contract_end_date) - JULIANDAY('now') as days_to_expiry,
    COUNT(DISTINCT ls.ls_service_key) as eligible_services,
    SUM(sk.service_credits) as estimated_credits_needed,
    GROUP_CONCAT(DISTINCT ls.service_name, ' | ') as recommended_services
FROM fact_service_credit sc
LEFT JOIN dim_customer c ON sc.customer_key = c.customer_key
LEFT JOIN fact_install_base ib ON c.customer_key = ib.customer_key
LEFT JOIN dim_product p ON ib.product_key = p.product_key
LEFT JOIN map_install_base_to_ls_sku m ON p.product_key = m.product_key
LEFT JOIN dim_ls_sku_product lp ON m.ls_product_key = lp.ls_product_key
LEFT JOIN map_product_service_sku ps ON lp.ls_product_key = ps.ls_product_key
LEFT JOIN dim_ls_sku_service ls ON ps.ls_service_key = ls.ls_service_key
LEFT JOIN map_service_sku msk ON ls.ls_service_key = msk.ls_service_key
LEFT JOIN dim_sku_code sk ON msk.sku_key = sk.sku_key
WHERE sc.active_credits > 20
  AND sk.service_credits IS NOT NULL
GROUP BY sc.credit_key
HAVING estimated_credits_needed <= sc.active_credits
ORDER BY days_to_expiry;

-- Quote Ready Export View
CREATE VIEW IF NOT EXISTS v_quote_ready_export AS
SELECT
    c.customer_name,
    c.customer_id_5digit as account_st_id,
    p.product_description as current_product,
    p.product_platform,
    ib.support_status,
    lp.product_name as ls_sku_product,
    ls.service_name,
    ls.service_type,
    ls.priority,
    GROUP_CONCAT(sk.sku_code, ', ') as sku_codes,
    MAX(sk.service_credits) as credits_required,
    m.confidence_score as match_confidence,
    CASE
        WHEN ib.days_to_eol < 0 THEN 'Critical'
        WHEN ib.days_to_eol BETWEEN 0 AND 90 THEN 'High'
        WHEN ib.days_to_eol BETWEEN 91 AND 180 THEN 'Medium'
        ELSE 'Low'
    END as urgency,
    o.opportunity_id,
    o.opportunity_name
FROM dim_customer c
JOIN fact_install_base ib ON c.customer_key = ib.customer_key
JOIN dim_product p ON ib.product_key = p.product_key
LEFT JOIN map_install_base_to_ls_sku m ON p.product_key = m.product_key
LEFT JOIN dim_ls_sku_product lp ON m.ls_product_key = lp.ls_product_key
LEFT JOIN map_product_service_sku ps ON lp.ls_product_key = ps.ls_product_key
LEFT JOIN dim_ls_sku_service ls ON ps.ls_service_key = ls.ls_service_key
LEFT JOIN map_service_sku msk ON ls.ls_service_key = msk.ls_service_key
LEFT JOIN dim_sku_code sk ON msk.sku_key = sk.sku_key
LEFT JOIN fact_opportunity o ON c.customer_key = o.customer_key
WHERE ls.service_name IS NOT NULL
GROUP BY c.customer_key, p.product_key, ls.ls_service_key
ORDER BY urgency DESC, ls.priority, c.customer_name;

-- ========================================
-- PERFORMANCE INDEXES
-- ========================================

-- LS_SKU Product indexes
CREATE INDEX IF NOT EXISTS idx_ls_product_name ON dim_ls_sku_product(product_name);
CREATE INDEX IF NOT EXISTS idx_ls_product_category ON dim_ls_sku_product(product_category);

-- LS_SKU Service indexes
CREATE INDEX IF NOT EXISTS idx_ls_service_type ON dim_ls_sku_service(service_type);
CREATE INDEX IF NOT EXISTS idx_ls_service_priority ON dim_ls_sku_service(priority);

-- SKU Code indexes
CREATE INDEX IF NOT EXISTS idx_sku_code ON dim_sku_code(sku_code);
CREATE INDEX IF NOT EXISTS idx_sku_credits ON dim_sku_code(service_credits);

-- Mapping indexes
CREATE INDEX IF NOT EXISTS idx_map_ps_product ON map_product_service_sku(ls_product_key);
CREATE INDEX IF NOT EXISTS idx_map_ps_service ON map_product_service_sku(ls_service_key);
CREATE INDEX IF NOT EXISTS idx_map_ss_service ON map_service_sku(ls_service_key);
CREATE INDEX IF NOT EXISTS idx_map_ss_sku ON map_service_sku(sku_key);
CREATE INDEX IF NOT EXISTS idx_map_ib_ls_product ON map_install_base_to_ls_sku(product_key);
CREATE INDEX IF NOT EXISTS idx_map_ib_ls_ls_product ON map_install_base_to_ls_sku(ls_product_key);
CREATE INDEX IF NOT EXISTS idx_map_ib_ls_confidence ON map_install_base_to_ls_sku(confidence_score);

-- Recommendation indexes
CREATE INDEX IF NOT EXISTS idx_rec_customer ON fact_service_recommendation(customer_key);
CREATE INDEX IF NOT EXISTS idx_rec_product ON fact_service_recommendation(product_key);
CREATE INDEX IF NOT EXISTS idx_rec_service ON fact_service_recommendation(ls_service_key);
CREATE INDEX IF NOT EXISTS idx_rec_status ON fact_service_recommendation(status);
CREATE INDEX IF NOT EXISTS idx_rec_date ON fact_service_recommendation(recommendation_date);

-- ========================================
-- UTILITY QUERIES (For Testing)
-- ========================================

/*
-- Test Query 1: Count of LS_SKU products by category
SELECT product_category, COUNT(*) as product_count
FROM dim_ls_sku_product
GROUP BY product_category;

-- Test Query 2: Services with SKU codes
SELECT
    s.service_name,
    s.service_type,
    GROUP_CONCAT(k.sku_code, ', ') as sku_codes
FROM dim_ls_sku_service s
LEFT JOIN map_service_sku m ON s.ls_service_key = m.ls_service_key
LEFT JOIN dim_sku_code k ON m.sku_key = k.sku_key
GROUP BY s.ls_service_key
LIMIT 10;

-- Test Query 3: Install Base products matched to LS_SKU
SELECT
    p.product_description,
    lp.product_name as ls_sku_match,
    m.confidence_score,
    m.match_method
FROM dim_product p
LEFT JOIN map_install_base_to_ls_sku m ON p.product_key = m.product_key
LEFT JOIN dim_ls_sku_product lp ON m.ls_product_key = lp.ls_product_key
WHERE m.confidence_score >= 80
LIMIT 20;

-- Test Query 4: Customer service recommendations with SKUs
SELECT * FROM v_quote_ready_export
WHERE urgency IN ('Critical', 'High')
LIMIT 10;
*/