"""
SQLite Database Loader for HPE OneLead System
Replaces Excel file loading with SQLite database queries
"""

import sqlite3
import pandas as pd
from pathlib import Path
import logging
from typing import Dict, Optional
import streamlit as st

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OneleadSQLiteLoader:
    """Load data from SQLite database instead of Excel"""
    
    def __init__(self, db_path: str = "data/onelead.db"):
        """
        Initialize SQLite loader
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")
        
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def load_all_data(_self) -> Dict[str, pd.DataFrame]:
        """
        Load all data from SQLite database
        
        Returns:
            Dictionary of DataFrames
        """
        conn = sqlite3.connect(_self.db_path)
        
        try:
            data = {}
            
            # Load customer 360 view
            logger.info("Loading customer data...")
            data['customers'] = pd.read_sql_query("""
                SELECT 
                    c.*,
                    COALESCE(v.product_count, 0) as product_count,
                    COALESCE(v.opportunity_count, 0) as opportunity_count,
                    COALESCE(v.project_count, 0) as project_count,
                    COALESCE(v.expired_products, 0) as expired_products,
                    COALESCE(v.avg_credit_utilization, 0) as avg_credit_utilization
                FROM dim_customer c
                LEFT JOIN v_customer_360 v ON c.customer_key = v.customer_key
            """, conn)
            
            # Load install base (simulated since we have no data)
            logger.info("Loading install base...")
            data['install_base'] = pd.read_sql_query("""
                SELECT 
                    c.customer_id_5digit as account_sales_territory_id,
                    p.*,
                    f.support_status,
                    f.days_to_eol,
                    f.days_to_eos
                FROM fact_install_base f
                JOIN dim_customer c ON f.customer_key = c.customer_key
                JOIN dim_product p ON f.product_key = p.product_key
            """, conn)
            
            # If no install base data, create simulated data for demo
            if data['install_base'].empty:
                data['install_base'] = _self._create_simulated_install_base(conn)
            
            # Load opportunities
            logger.info("Loading opportunities...")
            data['opportunities'] = pd.read_sql_query("""
                SELECT 
                    o.*,
                    c.customer_id_5digit as account_st_id,
                    c.customer_name as account_name
                FROM fact_opportunity o
                JOIN dim_customer c ON o.customer_key = c.customer_key
            """, conn)
            
            # Load APS projects
            logger.info("Loading APS projects...")
            data['aps_projects'] = pd.read_sql_query("""
                SELECT 
                    p.*,
                    pr.project_id_aps as project,
                    pr.project_name as prj_description,
                    pr.practice as prj_practice,
                    c.customer_id_9digit as prj_customer_id,
                    c.customer_name as prj_customer
                FROM fact_aps_project p
                JOIN dim_project pr ON p.project_key = pr.project_key
                JOIN dim_customer c ON p.customer_key = c.customer_key
            """, conn)
            
            # Load service credits
            logger.info("Loading service credits...")
            data['service_credits'] = pd.read_sql_query("""
                SELECT 
                    sc.*,
                    pr.project_id_credit as projectid
                FROM fact_service_credit sc
                LEFT JOIN dim_project pr ON sc.project_key = pr.project_key
            """, conn)
            
            # Load services
            logger.info("Loading services...")
            data['services'] = pd.read_sql_query("""
                SELECT * FROM dim_service
            """, conn)
            
            # Load summary metrics
            logger.info("Loading summary metrics...")
            data['credit_summary'] = pd.read_sql_query("""
                SELECT * FROM v_service_credit_summary
            """, conn)
            
            # Load opportunity pipeline
            data['opportunity_pipeline'] = pd.read_sql_query("""
                SELECT * FROM v_opportunity_pipeline
            """, conn)
            
            logger.info(f"Successfully loaded data from SQLite database")
            return data
            
        except Exception as e:
            logger.error(f"Error loading from database: {e}")
            raise
        finally:
            conn.close()
    
    def _create_simulated_install_base(self, conn) -> pd.DataFrame:
        """Create simulated install base data for demo purposes"""
        
        # Get customers with 5-digit IDs
        customers = pd.read_sql_query("""
            SELECT customer_id_5digit, customer_name 
            FROM dim_customer 
            WHERE customer_id_5digit IS NOT NULL
        """, conn)
        
        if customers.empty:
            return pd.DataFrame()
        
        # Create simulated product data
        import numpy as np
        from datetime import datetime, timedelta
        
        products = []
        product_types = [
            ('HP DL360p Gen8', 'Server', 'x86 Premium Servers', '2019-12-31'),
            ('HP MSA2000', 'Storage', 'Storage Arrays', '2018-06-30'),
            ('Aruba AP-325', 'Network', 'WLAN Infrastructure', '2099-12-31'),
            ('HP BL460c', 'Server', 'Blade Servers', '2020-03-31'),
            ('HP 3PAR', 'Storage', 'Enterprise Storage', '2021-12-31'),
        ]
        
        for _, customer in customers.iterrows():
            # Each customer gets 2-5 random products
            num_products = np.random.randint(2, 6)
            for _ in range(num_products):
                product_idx = np.random.randint(0, len(product_types))
                product = product_types[product_idx]
                eol_date = pd.to_datetime(product[3])
                days_to_eol = (eol_date - pd.Timestamp.now()).days
                
                products.append({
                    'account_sales_territory_id': customer['customer_id_5digit'],
                    'product_serial_number': f"SN{np.random.randint(100000, 999999)}",
                    'product_description': product[0],
                    'product_platform': product[1],
                    'product_business': product[2],
                    'support_status': 'Active' if days_to_eol > 0 else 'Expired',
                    'days_to_eol': days_to_eol,
                    'days_to_eos': days_to_eol + 365,
                    'eol_date': eol_date,
                    'eos_date': eol_date + timedelta(days=365)
                })
        
        return pd.DataFrame(products)
    
    @st.cache_data(ttl=3600)
    def calculate_metrics(_self, data: Dict[str, pd.DataFrame]) -> Dict:
        """
        Calculate business metrics from database data
        
        Args:
            data: Dictionary of DataFrames from database
            
        Returns:
            Dictionary of calculated metrics
        """
        metrics = {}
        
        # Install base metrics
        if 'install_base' in data and not data['install_base'].empty:
            ib = data['install_base']
            
            # Products at risk
            expired = ib[ib['days_to_eol'] < 0] if 'days_to_eol' in ib.columns else pd.DataFrame()
            at_risk = ib[(ib['days_to_eol'] >= 0) & (ib['days_to_eol'] < 180)] if 'days_to_eol' in ib.columns else pd.DataFrame()
            
            metrics['expired_products'] = len(expired)
            metrics['products_6mo_risk'] = len(at_risk)
            metrics['customers_with_expired'] = expired['account_sales_territory_id'].nunique() if not expired.empty else 0
            
            # Support coverage
            if 'support_status' in ib.columns:
                metrics['unsupported_products'] = (ib['support_status'] == 'Expired').sum()
        else:
            metrics['expired_products'] = 0
            metrics['products_6mo_risk'] = 0
            metrics['customers_with_expired'] = 0
            metrics['unsupported_products'] = 0
        
        # Credit metrics
        if 'credit_summary' in data and not data['credit_summary'].empty:
            summary = data['credit_summary'].iloc[0]
            metrics['unused_credits'] = summary.get('total_purchased', 0) - summary.get('total_delivered', 0)
            metrics['credit_utilization'] = summary.get('avg_utilization', 0)
        else:
            metrics['unused_credits'] = 0
            metrics['credit_utilization'] = 0
        
        # Opportunity metrics
        if 'opportunities' in data:
            metrics['total_opportunities'] = len(data['opportunities'])
            
            # Get key account (most opportunities)
            if not data['opportunities'].empty:
                key_account = data['opportunities'].groupby('account_st_id').size().idxmax()
                metrics['key_account'] = key_account
                metrics['key_account_opps'] = data['opportunities'][
                    data['opportunities']['account_st_id'] == key_account
                ].shape[0]
        else:
            metrics['total_opportunities'] = 0
        
        # Project metrics
        if 'aps_projects' in data:
            metrics['total_projects'] = len(data['aps_projects'])
            metrics['active_projects'] = data['aps_projects'][
                data['aps_projects']['project_status'] == 'Active'
            ].shape[0] if 'project_status' in data['aps_projects'].columns else 0
        else:
            metrics['total_projects'] = 0
            metrics['active_projects'] = 0
        
        # Customer metrics
        if 'customers' in data:
            customers = data['customers']
            metrics['total_customers'] = len(customers)
            metrics['customers_fully_mapped'] = (
                (customers['customer_id_5digit'].notna()) & 
                (customers['customer_id_9digit'].notna())
            ).sum()
        else:
            metrics['total_customers'] = 0
            metrics['customers_fully_mapped'] = 0
        
        return metrics
    
    def run_custom_query(self, query: str) -> pd.DataFrame:
        """
        Run a custom SQL query
        
        Args:
            query: SQL query string
            
        Returns:
            Query results as DataFrame
        """
        conn = sqlite3.connect(self.db_path)
        try:
            return pd.read_sql_query(query, conn)
        finally:
            conn.close()
    
    def get_table_info(self) -> pd.DataFrame:
        """Get information about all tables in the database"""
        conn = sqlite3.connect(self.db_path)
        try:
            return pd.read_sql_query("""
                SELECT 
                    name as table_name,
                    type as table_type
                FROM sqlite_master 
                WHERE type IN ('table', 'view')
                ORDER BY type, name
            """, conn)
        finally:
            conn.close()


# Compatibility wrapper for existing code
class OneleadDataLoaderV2:
    """Wrapper class for backward compatibility with existing code"""
    
    def __init__(self, data_path: str = None):
        """Initialize with SQLite loader"""
        self.loader = OneleadSQLiteLoader()
        self.processed_data = {}
        
    def process_all_data(self) -> Dict[str, pd.DataFrame]:
        """Load and process all data from SQLite"""
        return self.loader.load_all_data()


# Feature engineering compatibility
class OneleadFeatureEngineerV2:
    """Feature engineering compatibility wrapper"""
    
    def __init__(self, processed_data: Dict[str, pd.DataFrame]):
        self.processed_data = processed_data
        
    def build_feature_set(self) -> pd.DataFrame:
        """Build feature set for ML models"""
        # For now, return a simple feature set
        # This would need to be properly implemented based on your ML needs
        features = pd.DataFrame()
        
        if 'customers' in self.processed_data:
            features = self.processed_data['customers'].copy()
            
        return features