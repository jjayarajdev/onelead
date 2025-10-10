#!/usr/bin/env python3
"""
Create SQLite Database for HPE OneLead System
This script creates a complete SQLite database from the Excel data
with fixed relationships and proper schema design.
"""

import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, Optional, List, Tuple
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OneleadSQLiteDatabase:
    """Create and manage SQLite database for OneLead system"""
    
    def __init__(self, excel_path: str = "data/DataExportAug29th.xlsx", 
                 db_path: str = "data/onelead.db"):
        """
        Initialize database creator
        
        Args:
            excel_path: Path to Excel data file
            db_path: Path for SQLite database
        """
        self.excel_path = Path(excel_path)
        self.db_path = Path(db_path)
        self.conn = None
        self.cursor = None
        self.data = {}
        
    def create_database(self):
        """Main method to create complete database"""
        try:
            logger.info("=" * 60)
            logger.info("HPE OneLead SQLite Database Creation")
            logger.info("=" * 60)
            
            # Step 1: Load Excel data
            self._load_excel_data()
            
            # Step 2: Create database connection
            self._create_connection()
            
            # Step 3: Create schema
            self._create_schema()
            
            # Step 4: Create mapping tables
            self._create_mapping_tables()
            
            # Step 5: Load dimension tables
            self._load_dimension_tables()
            
            # Step 6: Load fact tables
            self._load_fact_tables()
            
            # Step 7: Fix relationships
            self._fix_relationships()
            
            # Step 8: Create views
            self._create_views()
            
            # Step 9: Create indexes
            self._create_indexes()
            
            # Step 10: Validate database
            self._validate_database()
            
            # Commit and close
            self.conn.commit()
            logger.info("✅ Database created successfully!")
            logger.info(f"📁 Location: {self.db_path.absolute()}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Database creation failed: {e}")
            if self.conn:
                self.conn.rollback()
            raise
        finally:
            if self.conn:
                self.conn.close()
    
    def _load_excel_data(self):
        """Load data from Excel file"""
        logger.info("\n📊 Step 1: Loading Excel data...")
        
        if not self.excel_path.exists():
            raise FileNotFoundError(f"Excel file not found: {self.excel_path}")
        
        excel_file = pd.ExcelFile(self.excel_path)
        
        # Map sheet names to internal keys
        sheet_mapping = {
            'Install Base': 'install_base',
            'Opportunity': 'opportunities',
            'A&PS Project sample': 'aps_projects',
            'Services': 'services',
            'Service Credits': 'service_credits'
        }
        
        for sheet_name in excel_file.sheet_names:
            logger.info(f"  Loading: {sheet_name}")
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            
            # Standardize column names (lowercase, replace spaces with underscores)
            df.columns = [col.lower().replace(' ', '_').replace('-', '_') 
                         for col in df.columns]
            
            key = sheet_mapping.get(sheet_name, sheet_name.lower().replace(' ', '_'))
            self.data[key] = df
            logger.info(f"    ✓ Loaded {len(df):,} records")
    
    def _create_connection(self):
        """Create SQLite database connection"""
        logger.info(f"\n💾 Step 2: Creating database: {self.db_path}")
        
        # Remove existing database if it exists
        if self.db_path.exists():
            self.db_path.unlink()
            logger.info("  Removed existing database")
        
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        # Enable foreign keys
        self.cursor.execute("PRAGMA foreign_keys = ON")
        logger.info("  ✓ Database connection established")
    
    def _create_schema(self):
        """Create database schema"""
        logger.info("\n🏗️ Step 3: Creating database schema...")
        
        schema_sql = """
        -- ========================================
        -- DIMENSION TABLES
        -- ========================================
        
        -- Unified Customer Dimension
        CREATE TABLE dim_customer (
            customer_key INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id_5digit VARCHAR(5),
            customer_id_9digit VARCHAR(9),
            customer_name VARCHAR(255),
            territory VARCHAR(100),
            region VARCHAR(50),
            country VARCHAR(100),
            customer_type VARCHAR(50),
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(customer_id_5digit),
            UNIQUE(customer_id_9digit)
        );
        
        -- Product Dimension
        CREATE TABLE dim_product (
            product_key INTEGER PRIMARY KEY AUTOINCREMENT,
            product_serial_number VARCHAR(100) UNIQUE,
            product_number VARCHAR(50),
            product_description TEXT,
            product_platform VARCHAR(100),
            product_business VARCHAR(50),
            product_portfolio VARCHAR(100),
            product_sub_portfolio VARCHAR(100),
            hw_sw VARCHAR(20),
            eol_date DATE,
            eos_date DATE,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Service Dimension
        CREATE TABLE dim_service (
            service_key INTEGER PRIMARY KEY AUTOINCREMENT,
            practice VARCHAR(100),
            sub_practice VARCHAR(100),
            service_name VARCHAR(255),
            service_category VARCHAR(100),
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(practice, sub_practice, service_name)
        );
        
        -- Project Dimension
        CREATE TABLE dim_project (
            project_key INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id_aps VARCHAR(20),
            project_id_credit VARCHAR(20),
            project_name VARCHAR(255),
            project_type VARCHAR(100),
            practice VARCHAR(100),
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(project_id_aps),
            UNIQUE(project_id_credit)
        );
        
        -- Date Dimension (simplified)
        CREATE TABLE dim_date (
            date_key INTEGER PRIMARY KEY,
            full_date DATE UNIQUE,
            year INTEGER,
            quarter INTEGER,
            month INTEGER,
            day INTEGER,
            weekday INTEGER,
            is_weekend BOOLEAN
        );
        
        -- ========================================
        -- FACT TABLES
        -- ========================================
        
        -- Install Base Fact
        CREATE TABLE fact_install_base (
            install_key INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_key INTEGER,
            product_key INTEGER,
            date_key INTEGER,
            support_status VARCHAR(50),
            support_business VARCHAR(100),
            service_start_date DATE,
            service_end_date DATE,
            days_to_eol INTEGER,
            days_to_eos INTEGER,
            quantity INTEGER DEFAULT 1,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
            FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
            FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
        );
        
        -- Opportunity Fact
        CREATE TABLE fact_opportunity (
            opportunity_key INTEGER PRIMARY KEY AUTOINCREMENT,
            opportunity_id VARCHAR(50) UNIQUE,
            customer_key INTEGER,
            date_key INTEGER,
            opportunity_name TEXT,
            product_line VARCHAR(100),
            opportunity_stage VARCHAR(50),
            opportunity_value DECIMAL(12,2),
            probability DECIMAL(5,2),
            weighted_value DECIMAL(12,2),
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
            FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
        );
        
        -- APS Project Fact
        CREATE TABLE fact_aps_project (
            aps_project_key INTEGER PRIMARY KEY AUTOINCREMENT,
            project_key INTEGER,
            customer_key INTEGER,
            start_date_key INTEGER,
            end_date_key INTEGER,
            project_description TEXT,
            project_status VARCHAR(50),
            project_size VARCHAR(20),
            project_length VARCHAR(50),
            revenue DECIMAL(12,2),
            cost DECIMAL(12,2),
            margin DECIMAL(5,2),
            resource_count INTEGER,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_key) REFERENCES dim_project(project_key),
            FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
            FOREIGN KEY (start_date_key) REFERENCES dim_date(date_key),
            FOREIGN KEY (end_date_key) REFERENCES dim_date(date_key)
        );
        
        -- Service Credit Fact
        CREATE TABLE fact_service_credit (
            credit_key INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_id VARCHAR(50) UNIQUE,
            project_key INTEGER,
            customer_key INTEGER,
            date_key INTEGER,
            contract_number VARCHAR(50),
            purchased_credits DECIMAL(10,2),
            delivered_credits DECIMAL(10,2),
            active_credits DECIMAL(10,2),
            expired_credits DECIMAL(10,2),
            utilization_rate DECIMAL(5,2),
            contract_end_date DATE,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_key) REFERENCES dim_project(project_key),
            FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
            FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
        );
        
        -- ========================================
        -- MAPPING TABLES
        -- ========================================
        
        -- Customer ID Mapping
        CREATE TABLE map_customer_id (
            mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id_5digit VARCHAR(5),
            customer_id_9digit VARCHAR(9),
            customer_name VARCHAR(255),
            confidence_score DECIMAL(5,2),
            mapping_method VARCHAR(50),
            verified BOOLEAN DEFAULT FALSE,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Project ID Mapping
        CREATE TABLE map_project_id (
            mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id_aps VARCHAR(20),
            project_id_credit VARCHAR(20),
            project_name VARCHAR(255),
            confidence_score DECIMAL(5,2),
            mapping_method VARCHAR(50),
            verified BOOLEAN DEFAULT FALSE,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Service Practice Mapping
        CREATE TABLE map_service_practice (
            mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_practice VARCHAR(100),
            standardized_practice VARCHAR(100),
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Execute schema creation
        for statement in schema_sql.split(';'):
            if statement.strip():
                self.cursor.execute(statement)
        
        self.conn.commit()
        logger.info("  ✓ Schema created successfully")
    
    def _create_mapping_tables(self):
        """Create and populate mapping tables"""
        logger.info("\n🔗 Step 4: Creating mapping tables...")
        
        # Customer ID mappings (example mappings - would need real data analysis)
        customer_mappings = [
            ('56088', '110079582', 'Territory Alpha Customer', 85.0, 'manual'),
            ('56769', '110085660', 'Territory Beta Customer', 80.0, 'manual'),
            ('55692', '110002949', 'Territory Gamma Customer', 75.0, 'manual'),
        ]
        
        self.cursor.executemany("""
            INSERT INTO map_customer_id 
            (customer_id_5digit, customer_id_9digit, customer_name, confidence_score, mapping_method, verified)
            VALUES (?, ?, ?, ?, ?, TRUE)
        """, customer_mappings)
        
        # Service practice mappings
        practice_mappings = [
            ('CLD & PLT', 'Cloud & Platform'),
            ('NTWK & CYB', 'Network & Cybersecurity'),
            ('AI & D', 'AI & Data'),
            ('Hybrid Cloud Engineering', 'Cloud & Platform'),
            ('Data AI & IOT', 'AI & Data'),
            ('Technical Services', 'Support Services'),
            ('PS - HPE Complete Care', 'Support Services'),
        ]
        
        self.cursor.executemany("""
            INSERT INTO map_service_practice (original_practice, standardized_practice)
            VALUES (?, ?)
        """, practice_mappings)
        
        self.conn.commit()
        logger.info(f"  ✓ Created {len(customer_mappings)} customer mappings")
        logger.info(f"  ✓ Created {len(practice_mappings)} practice mappings")
    
    def _load_dimension_tables(self):
        """Load dimension tables"""
        logger.info("\n📦 Step 5: Loading dimension tables...")
        
        # Load customers
        self._load_customers()
        
        # Load products
        self._load_products()
        
        # Load services
        self._load_services()
        
        # Load projects
        self._load_projects()
        
        # Load date dimension
        self._load_dates()
        
        self.conn.commit()
    
    def _load_customers(self):
        """Load unified customer dimension"""
        customers = set()
        
        # From Install Base (5-digit)
        if 'install_base' in self.data:
            df = self.data['install_base']
            if 'account_sales_territory_id' in df.columns:
                for cust_id in df['account_sales_territory_id'].unique():
                    if pd.notna(cust_id):
                        customers.add((str(cust_id), None, f"Customer {cust_id}"))
        
        # From Opportunities (5-digit)
        if 'opportunities' in self.data:
            df = self.data['opportunities']
            if 'account_st_id' in df.columns:
                for idx, row in df[['account_st_id', 'account_name']].drop_duplicates().iterrows():
                    if pd.notna(row['account_st_id']):
                        customers.add((str(row['account_st_id']), None, row.get('account_name', f"Customer {row['account_st_id']}")))
        
        # From APS Projects (9-digit)
        if 'aps_projects' in self.data:
            df = self.data['aps_projects']
            if 'prj_customer_id' in df.columns:
                for idx, row in df[['prj_customer_id', 'prj_customer']].drop_duplicates().iterrows():
                    if pd.notna(row['prj_customer_id']):
                        # Check if we have a mapping
                        self.cursor.execute("""
                            SELECT customer_id_5digit FROM map_customer_id 
                            WHERE customer_id_9digit = ?
                        """, (str(row['prj_customer_id']),))
                        result = self.cursor.fetchone()
                        
                        if result:
                            # Update existing customer with 9-digit ID
                            customers.add((result[0], str(row['prj_customer_id']), row.get('prj_customer', '')))
                        else:
                            # New customer with only 9-digit ID
                            customers.add((None, str(row['prj_customer_id']), row.get('prj_customer', '')))
        
        # Insert customers
        for cust_5d, cust_9d, cust_name in customers:
            try:
                self.cursor.execute("""
                    INSERT OR IGNORE INTO dim_customer 
                    (customer_id_5digit, customer_id_9digit, customer_name)
                    VALUES (?, ?, ?)
                """, (cust_5d, cust_9d, cust_name))
            except sqlite3.IntegrityError:
                # Update if mapping exists
                if cust_5d and cust_9d:
                    self.cursor.execute("""
                        UPDATE dim_customer 
                        SET customer_id_9digit = ?
                        WHERE customer_id_5digit = ?
                    """, (cust_9d, cust_5d))
        
        logger.info(f"  ✓ Loaded {len(customers)} customers")
    
    def _load_products(self):
        """Load product dimension"""
        if 'install_base' not in self.data:
            return
        
        df = self.data['install_base']
        products = []
        
        for _, row in df.iterrows():
            product = {
                'serial': row.get('product_serial_number'),
                'number': row.get('product_number'),
                'description': row.get('product_description'),
                'platform': row.get('product_platform_description_name'),
                'business': row.get('product_business'),
                'portfolio': row.get('product_portfolio_name'),
                'sub_portfolio': row.get('product_sub_portfolio'),
                'hw_sw': row.get('hw___sw') or row.get('hw_sw'),
                'eol': pd.to_datetime(row.get('product_end_of_life_date'), errors='coerce'),
                'eos': pd.to_datetime(row.get('product_end_of_service_life_date'), errors='coerce')
            }
            
            if pd.notna(product['serial']):
                products.append(product)
        
        # Insert products
        for prod in products:
            self.cursor.execute("""
                INSERT OR IGNORE INTO dim_product 
                (product_serial_number, product_number, product_description,
                 product_platform, product_business, product_portfolio,
                 product_sub_portfolio, hw_sw, eol_date, eos_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (prod['serial'], prod['number'], prod['description'],
                  prod['platform'], prod['business'], prod['portfolio'],
                  prod['sub_portfolio'], prod['hw_sw'], 
                  prod['eol'].date() if pd.notna(prod['eol']) else None,
                  prod['eos'].date() if pd.notna(prod['eos']) else None))
        
        logger.info(f"  ✓ Loaded {len(products)} products")
    
    def _load_services(self):
        """Load service dimension"""
        if 'services' not in self.data:
            return
        
        df = self.data['services']
        services = []
        
        for _, row in df.iterrows():
            services.append((
                row.get('practice'),
                row.get('sub_practice') or row.get('sub-practice'),
                row.get('services')
            ))
        
        self.cursor.executemany("""
            INSERT OR IGNORE INTO dim_service (practice, sub_practice, service_name)
            VALUES (?, ?, ?)
        """, services)
        
        logger.info(f"  ✓ Loaded {len(services)} services")
    
    def _load_projects(self):
        """Load project dimension"""
        projects = []
        
        # From APS Projects
        if 'aps_projects' in self.data:
            df = self.data['aps_projects']
            for _, row in df.iterrows():
                if pd.notna(row.get('project')):
                    projects.append({
                        'aps_id': row.get('project'),
                        'credit_id': None,
                        'name': row.get('prj_description'),
                        'type': row.get('prj_type'),
                        'practice': row.get('prj_practice')
                    })
        
        # From Service Credits
        if 'service_credits' in self.data:
            df = self.data['service_credits']
            for _, row in df[['projectid']].drop_duplicates().iterrows():
                if pd.notna(row.get('projectid')):
                    projects.append({
                        'aps_id': None,
                        'credit_id': row.get('projectid'),
                        'name': f"Project {row.get('projectid')}",
                        'type': 'Service Credit',
                        'practice': 'Support Services'
                    })
        
        # Insert projects
        for proj in projects:
            self.cursor.execute("""
                INSERT OR IGNORE INTO dim_project 
                (project_id_aps, project_id_credit, project_name, project_type, practice)
                VALUES (?, ?, ?, ?, ?)
            """, (proj['aps_id'], proj['credit_id'], proj['name'], 
                  proj['type'], proj['practice']))
        
        logger.info(f"  ✓ Loaded {len(projects)} projects")
    
    def _load_dates(self):
        """Load date dimension with relevant dates"""
        dates = set()
        
        # Collect all dates from data
        for df_name, df in self.data.items():
            for col in df.columns:
                if 'date' in col.lower():
                    for date_val in df[col].dropna():
                        try:
                            date_obj = pd.to_datetime(date_val, errors='coerce')
                            if pd.notna(date_obj):
                                dates.add(date_obj.date())
                        except:
                            pass
        
        # Insert dates
        for date_val in dates:
            date_key = int(date_val.strftime('%Y%m%d'))
            self.cursor.execute("""
                INSERT OR IGNORE INTO dim_date 
                (date_key, full_date, year, quarter, month, day, weekday, is_weekend)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (date_key, date_val, date_val.year, 
                  (date_val.month - 1) // 3 + 1, date_val.month, 
                  date_val.day, date_val.weekday(), 
                  date_val.weekday() >= 5))
        
        logger.info(f"  ✓ Loaded {len(dates)} dates")
    
    def _load_fact_tables(self):
        """Load fact tables"""
        logger.info("\n📊 Step 6: Loading fact tables...")
        
        # Load Install Base facts
        self._load_fact_install_base()
        
        # Load Opportunity facts
        self._load_fact_opportunities()
        
        # Load APS Project facts
        self._load_fact_aps_projects()
        
        # Load Service Credit facts
        self._load_fact_service_credits()
        
        self.conn.commit()
    
    def _load_fact_install_base(self):
        """Load install base facts"""
        if 'install_base' not in self.data:
            return
        
        df = self.data['install_base']
        facts = []
        
        for _, row in df.iterrows():
            # Get customer key
            cust_id = str(row.get('account_sales_territory_id'))
            self.cursor.execute("""
                SELECT customer_key FROM dim_customer 
                WHERE customer_id_5digit = ?
            """, (cust_id,))
            cust_result = self.cursor.fetchone()
            
            # Get product key
            prod_serial = row.get('product_serial_number')
            self.cursor.execute("""
                SELECT product_key FROM dim_product 
                WHERE product_serial_number = ?
            """, (prod_serial,))
            prod_result = self.cursor.fetchone()
            
            if cust_result and prod_result:
                # Calculate days to EOL/EOS
                eol_date = pd.to_datetime(row.get('product_end_of_life_date'), errors='coerce')
                eos_date = pd.to_datetime(row.get('product_end_of_service_life_date'), errors='coerce')
                
                days_to_eol = (eol_date - pd.Timestamp.now()).days if pd.notna(eol_date) else None
                days_to_eos = (eos_date - pd.Timestamp.now()).days if pd.notna(eos_date) else None
                
                service_start = pd.to_datetime(row.get('final_service_start_date'), errors='coerce')
                service_end = pd.to_datetime(row.get('final_service_end_date'), errors='coerce')
                
                facts.append((
                    cust_result[0],  # customer_key
                    prod_result[0],  # product_key
                    20240901,  # date_key (placeholder)
                    row.get('support_status'),
                    row.get('support_business'),
                    service_start.strftime('%Y-%m-%d') if pd.notna(service_start) else None,
                    service_end.strftime('%Y-%m-%d') if pd.notna(service_end) else None,
                    days_to_eol,
                    days_to_eos
                ))
        
        self.cursor.executemany("""
            INSERT INTO fact_install_base 
            (customer_key, product_key, date_key, support_status, support_business,
             service_start_date, service_end_date, days_to_eol, days_to_eos)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, facts)
        
        logger.info(f"  ✓ Loaded {len(facts)} install base facts")
    
    def _load_fact_opportunities(self):
        """Load opportunity facts"""
        if 'opportunities' not in self.data:
            return
        
        df = self.data['opportunities']
        facts = []
        
        for _, row in df.iterrows():
            # Get customer key
            cust_id = str(row.get('account_st_id'))
            self.cursor.execute("""
                SELECT customer_key FROM dim_customer 
                WHERE customer_id_5digit = ?
            """, (cust_id,))
            cust_result = self.cursor.fetchone()
            
            if cust_result:
                facts.append((
                    row.get('hpe_opportunity_id'),
                    cust_result[0],
                    20240901,  # date_key
                    row.get('opportunity_name') or row.get('opportunity_nam'),
                    row.get('product_line')
                ))
        
        self.cursor.executemany("""
            INSERT OR IGNORE INTO fact_opportunity 
            (opportunity_id, customer_key, date_key, opportunity_name, product_line)
            VALUES (?, ?, ?, ?, ?)
        """, facts)
        
        logger.info(f"  ✓ Loaded {len(facts)} opportunity facts")
    
    def _load_fact_aps_projects(self):
        """Load APS project facts"""
        if 'aps_projects' not in self.data:
            return
        
        df = self.data['aps_projects']
        facts = []
        
        for _, row in df.iterrows():
            # Get project key
            proj_id = row.get('project')
            self.cursor.execute("""
                SELECT project_key FROM dim_project 
                WHERE project_id_aps = ?
            """, (proj_id,))
            proj_result = self.cursor.fetchone()
            
            # Get customer key
            cust_id = str(row.get('prj_customer_id'))
            self.cursor.execute("""
                SELECT customer_key FROM dim_customer 
                WHERE customer_id_9digit = ?
            """, (cust_id,))
            cust_result = self.cursor.fetchone()
            
            if proj_result and cust_result:
                facts.append((
                    proj_result[0],  # project_key
                    cust_result[0],  # customer_key
                    20240901,  # start_date_key
                    20240930,  # end_date_key
                    row.get('prj_description'),
                    row.get('prj_status_description'),
                    row.get('prj_size'),
                    row.get('prj_length')
                ))
        
        self.cursor.executemany("""
            INSERT INTO fact_aps_project 
            (project_key, customer_key, start_date_key, end_date_key,
             project_description, project_status, project_size, project_length)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, facts)
        
        logger.info(f"  ✓ Loaded {len(facts)} APS project facts")
    
    def _load_fact_service_credits(self):
        """Load service credit facts"""
        if 'service_credits' not in self.data:
            return
        
        df = self.data['service_credits']
        facts = []
        
        for _, row in df.iterrows():
            # Get project key
            proj_id = row.get('projectid')
            self.cursor.execute("""
                SELECT project_key FROM dim_project 
                WHERE project_id_credit = ?
            """, (proj_id,))
            proj_result = self.cursor.fetchone()
            
            # Calculate utilization
            purchased = float(row.get('purchasedcredits', 0) or 0)
            delivered = float(row.get('deliveredcredits', 0) or 0)
            utilization = (delivered / purchased * 100) if purchased > 0 else 0
            
            contract_end = pd.to_datetime(row.get('contractenddate'), errors='coerce')
            contract_end_str = contract_end.strftime('%Y-%m-%d') if pd.notna(contract_end) else None
            
            facts.append((
                row.get('contractid'),
                proj_result[0] if proj_result else None,
                None,  # customer_key (would need mapping)
                20240901,  # date_key
                row.get('contractnumber'),
                purchased,
                delivered,
                float(row.get('activecredits', 0) or 0),
                float(row.get('expiredcredits', 0) or 0),
                utilization,
                contract_end_str
            ))
        
        self.cursor.executemany("""
            INSERT OR IGNORE INTO fact_service_credit 
            (contract_id, project_key, customer_key, date_key, contract_number,
             purchased_credits, delivered_credits, active_credits, expired_credits,
             utilization_rate, contract_end_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, facts)
        
        logger.info(f"  ✓ Loaded {len(facts)} service credit facts")
    
    def _fix_relationships(self):
        """Apply relationship fixes using mapping tables"""
        logger.info("\n🔧 Step 7: Fixing relationships...")
        
        # Update customers with mapped IDs
        self.cursor.execute("""
            UPDATE dim_customer
            SET customer_id_9digit = (
                SELECT m.customer_id_9digit 
                FROM map_customer_id m
                WHERE m.customer_id_5digit = dim_customer.customer_id_5digit
                AND m.verified = TRUE
            )
            WHERE customer_id_9digit IS NULL
            AND EXISTS (
                SELECT 1 FROM map_customer_id m
                WHERE m.customer_id_5digit = dim_customer.customer_id_5digit
            )
        """)
        
        rows_updated = self.cursor.rowcount
        logger.info(f"  ✓ Updated {rows_updated} customer relationships")
        
        # Update projects with mapped IDs
        self.cursor.execute("""
            UPDATE dim_project
            SET project_id_credit = (
                SELECT m.project_id_credit 
                FROM map_project_id m
                WHERE m.project_id_aps = dim_project.project_id_aps
                AND m.verified = TRUE
            )
            WHERE project_id_credit IS NULL
            AND EXISTS (
                SELECT 1 FROM map_project_id m
                WHERE m.project_id_aps = dim_project.project_id_aps
            )
        """)
        
        rows_updated = self.cursor.rowcount
        logger.info(f"  ✓ Updated {rows_updated} project relationships")
    
    def _create_views(self):
        """Create analytical views"""
        logger.info("\n👁️ Step 8: Creating views...")
        
        views_sql = """
        -- Customer 360 View
        CREATE VIEW IF NOT EXISTS v_customer_360 AS
        SELECT 
            c.customer_key,
            c.customer_id_5digit,
            c.customer_id_9digit,
            c.customer_name,
            COUNT(DISTINCT ib.install_key) as product_count,
            COUNT(DISTINCT o.opportunity_key) as opportunity_count,
            COUNT(DISTINCT p.aps_project_key) as project_count,
            SUM(CASE WHEN ib.days_to_eol < 0 THEN 1 ELSE 0 END) as expired_products,
            SUM(CASE WHEN ib.days_to_eol BETWEEN 0 AND 180 THEN 1 ELSE 0 END) as products_expiring_soon,
            AVG(sc.utilization_rate) as avg_credit_utilization
        FROM dim_customer c
        LEFT JOIN fact_install_base ib ON c.customer_key = ib.customer_key
        LEFT JOIN fact_opportunity o ON c.customer_key = o.customer_key
        LEFT JOIN fact_aps_project p ON c.customer_key = p.customer_key
        LEFT JOIN fact_service_credit sc ON c.customer_key = sc.customer_key
        GROUP BY c.customer_key, c.customer_id_5digit, c.customer_id_9digit, c.customer_name;
        
        -- Product Risk View
        CREATE VIEW IF NOT EXISTS v_product_risk AS
        SELECT 
            p.product_platform as platform,
            COUNT(*) as total_products,
            SUM(CASE WHEN ib.days_to_eol < 0 THEN 1 ELSE 0 END) as expired,
            SUM(CASE WHEN ib.days_to_eol BETWEEN 0 AND 365 THEN 1 ELSE 0 END) as expiring_1year,
            AVG(ib.days_to_eol) as avg_days_to_eol
        FROM fact_install_base ib
        JOIN dim_product p ON ib.product_key = p.product_key
        GROUP BY p.product_platform;
        
        -- Service Credit Summary View
        CREATE VIEW IF NOT EXISTS v_service_credit_summary AS
        SELECT 
            SUM(purchased_credits) as total_purchased,
            SUM(delivered_credits) as total_delivered,
            SUM(active_credits) as total_active,
            SUM(expired_credits) as total_expired,
            AVG(utilization_rate) as avg_utilization,
            COUNT(DISTINCT project_key) as project_count,
            COUNT(*) as contract_count
        FROM fact_service_credit;
        
        -- Opportunity Pipeline View
        CREATE VIEW IF NOT EXISTS v_opportunity_pipeline AS
        SELECT 
            c.customer_name,
            COUNT(*) as opportunity_count,
            GROUP_CONCAT(DISTINCT o.product_line) as product_lines,
            o.opportunity_stage
        FROM fact_opportunity o
        JOIN dim_customer c ON o.customer_key = c.customer_key
        GROUP BY c.customer_name, o.opportunity_stage;
        """
        
        for statement in views_sql.split(';'):
            if statement.strip():
                self.cursor.execute(statement)
        
        logger.info("  ✓ Created 4 analytical views")
    
    def _create_indexes(self):
        """Create database indexes for performance"""
        logger.info("\n⚡ Step 9: Creating indexes...")
        
        indexes = [
            # Customer indexes
            "CREATE INDEX IF NOT EXISTS idx_customer_5digit ON dim_customer(customer_id_5digit)",
            "CREATE INDEX IF NOT EXISTS idx_customer_9digit ON dim_customer(customer_id_9digit)",
            
            # Product indexes
            "CREATE INDEX IF NOT EXISTS idx_product_serial ON dim_product(product_serial_number)",
            "CREATE INDEX IF NOT EXISTS idx_product_eol ON dim_product(eol_date)",
            
            # Install base indexes
            "CREATE INDEX IF NOT EXISTS idx_ib_customer ON fact_install_base(customer_key)",
            "CREATE INDEX IF NOT EXISTS idx_ib_product ON fact_install_base(product_key)",
            "CREATE INDEX IF NOT EXISTS idx_ib_eol ON fact_install_base(days_to_eol)",
            
            # Opportunity indexes
            "CREATE INDEX IF NOT EXISTS idx_opp_customer ON fact_opportunity(customer_key)",
            
            # Project indexes
            "CREATE INDEX IF NOT EXISTS idx_proj_customer ON fact_aps_project(customer_key)",
            
            # Credit indexes
            "CREATE INDEX IF NOT EXISTS idx_credit_project ON fact_service_credit(project_key)",
        ]
        
        for idx_sql in indexes:
            self.cursor.execute(idx_sql)
        
        logger.info(f"  ✓ Created {len(indexes)} indexes")
    
    def _validate_database(self):
        """Validate database integrity"""
        logger.info("\n✅ Step 10: Validating database...")
        
        # Check record counts
        tables = [
            'dim_customer', 'dim_product', 'dim_service', 'dim_project',
            'fact_install_base', 'fact_opportunity', 'fact_aps_project', 
            'fact_service_credit'
        ]
        
        print("\n" + "="*60)
        print("DATABASE VALIDATION REPORT")
        print("="*60)
        
        for table in tables:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = self.cursor.fetchone()[0]
            print(f"  {table:.<30} {count:>6} records")
        
        # Check relationships
        print("\n📊 Relationship Coverage:")
        
        # Customer mapping coverage
        self.cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN customer_id_5digit IS NOT NULL THEN 1 ELSE 0 END) as with_5digit,
                SUM(CASE WHEN customer_id_9digit IS NOT NULL THEN 1 ELSE 0 END) as with_9digit,
                SUM(CASE WHEN customer_id_5digit IS NOT NULL 
                    AND customer_id_9digit IS NOT NULL THEN 1 ELSE 0 END) as fully_mapped
            FROM dim_customer
        """)
        result = self.cursor.fetchone()
        print(f"  Customers: {result[0]} total, {result[3]} fully mapped ({result[3]/result[0]*100:.1f}%)")
        
        # Check views
        print("\n👁️ Views Created:")
        self.cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='view' 
            ORDER BY name
        """)
        for view in self.cursor.fetchall():
            print(f"  ✓ {view[0]}")
        
        print("="*60 + "\n")


# Main execution
if __name__ == "__main__":
    db_creator = OneleadSQLiteDatabase()
    db_creator.create_database()
    
    print("\n🎉 Database creation complete!")
    print(f"📁 Database location: {db_creator.db_path.absolute()}")
    print("\n📝 Next steps:")
    print("  1. Test queries: sqlite3 data/onelead.db")
    print("  2. View schema: .schema")
    print("  3. Query data: SELECT * FROM v_customer_360;")