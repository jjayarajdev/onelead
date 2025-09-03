"""
HPE OneLead Data Loader V2
Handles the new DataExportAug29th.xlsx file structure
"""

import pandas as pd
from typing import Dict, List, Optional
import logging
from pathlib import Path
import warnings
import numpy as np

warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OneleadDataLoaderV2:
    """Load and preprocess HPE OneLead data from new export format"""
    
    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self.raw_data = {}
        self.processed_data = {}
        
    def load_excel_data(self) -> Dict[str, pd.DataFrame]:
        """Load all sheets from the Excel file"""
        try:
            logger.info(f"Loading data from {self.data_path}")
            
            # Load all sheets with their actual names
            excel_file = pd.ExcelFile(self.data_path)
            
            sheet_mapping = {
                'Install Base': 'install_base',
                'Opportunity': 'opportunities', 
                'A&PS Project sample': 'aps_projects',
                'Services': 'services',
                'Service Credits': 'service_credits'
            }
            
            for sheet_name in excel_file.sheet_names:
                logger.info(f"Loading sheet: {sheet_name}")
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                
                # Use mapped name or original if not in mapping
                key_name = sheet_mapping.get(sheet_name, sheet_name)
                self.raw_data[key_name] = df
                logger.info(f"Loaded {len(df)} records from {sheet_name}")
                
            return self.raw_data
            
        except Exception as e:
            logger.error(f"Error loading Excel data: {e}")
            raise
    
    def preprocess_install_base(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and enhance install base data"""
        processed = df.copy()
        
        # Standardize column names
        processed.columns = [col.lower().replace(' ', '_') for col in processed.columns]
        
        # Convert dates
        date_columns = ['product_end_of_life_date', 'product_end_of_service_life_date', 
                       'final_service_start_date', 'final_service_end_date']
        for col in date_columns:
            if col in processed.columns:
                processed[col] = pd.to_datetime(processed[col], errors='coerce')
        
        # Calculate days until end-of-life/service
        if 'product_end_of_life_date' in processed.columns:
            processed['days_to_eol'] = (processed['product_end_of_life_date'] - pd.Timestamp.now()).dt.days
            processed['eol_risk'] = processed['days_to_eol'].apply(
                lambda x: 'Critical' if x < 180 else 'High' if x < 365 else 'Medium' if x < 730 else 'Low' if pd.notna(x) else 'Unknown'
            )
            processed['eol_urgency_score'] = processed['days_to_eol'].apply(
                lambda x: 4 if x < 180 else 3 if x < 365 else 2 if x < 730 else 1 if pd.notna(x) else 0
            )
        
        if 'product_end_of_service_life_date' in processed.columns:
            processed['days_to_eos'] = (processed['product_end_of_service_life_date'] - pd.Timestamp.now()).dt.days
            processed['eos_risk'] = processed['days_to_eos'].apply(
                lambda x: 'Critical' if x < 180 else 'High' if x < 365 else 'Medium' if x < 730 else 'Low' if pd.notna(x) else 'Unknown'
            )
            processed['eos_urgency_score'] = processed['days_to_eos'].apply(
                lambda x: 4 if x < 180 else 3 if x < 365 else 2 if x < 730 else 1 if pd.notna(x) else 0
            )
        
        # Add platform categorization
        if 'product_platform_description_name' in processed.columns:
            processed['platform_category'] = processed['product_platform_description_name'].fillna('Unknown')
        
        return processed
    
    def preprocess_opportunities(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and enhance opportunities data"""
        processed = df.copy()
        
        # Standardize column names
        column_mapping = {
            'HPE Opportunity ID': 'opportunity_id',
            'Opportunity NAme': 'opportunity_name',  # Note the typo in original
            'Account ST ID': 'account_st_id',
            'Account Name': 'account_name',
            'Product Line': 'product_line'
        }
        processed.rename(columns=column_mapping, inplace=True)
        
        # Extract opportunity features
        processed['has_opportunity'] = 1
        
        # Categorize product lines
        if 'product_line' in processed.columns:
            # Extract main product category from product line codes
            processed['product_category'] = processed['product_line'].apply(
                lambda x: str(x).split(' - ')[0] if pd.notna(x) else 'Unknown'
            )
            
        return processed
    
    def preprocess_aps_projects(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and enhance A&PS projects data"""
        processed = df.copy()
        
        # Standardize column names (select key columns)
        column_mapping = {
            'PRJ Customer ID': 'customer_id',
            'Project': 'project_id',
            'PRJ Description': 'project_description',
            'PRJ Practice': 'practice',
            'PRJ Start Date': 'start_date',
            'PRJ End Date': 'end_date',
            'PRJ Status Description': 'status',
            'Country': 'country',
            'PRJ Size': 'project_size',
            'PRJ Length': 'project_length',
            'PRJ Customer': 'customer_name'
        }
        
        # Only rename columns that exist
        rename_dict = {k: v for k, v in column_mapping.items() if k in processed.columns}
        processed.rename(columns=rename_dict, inplace=True)
        
        # Convert dates
        for col in ['start_date', 'end_date']:
            if col in processed.columns:
                processed[col] = pd.to_datetime(processed[col], errors='coerce')
        
        # Calculate project metrics
        if 'start_date' in processed.columns:
            processed['days_since_start'] = (pd.Timestamp.now() - processed['start_date']).dt.days
            processed['project_recency'] = processed['days_since_start'].apply(
                lambda x: 'Active' if x < 90 else 'Recent' if x < 180 else 'Past' if pd.notna(x) else 'Unknown'
            )
        
        if 'start_date' in processed.columns and 'end_date' in processed.columns:
            processed['project_duration'] = (processed['end_date'] - processed['start_date']).dt.days
            processed['is_active'] = processed.apply(
                lambda x: pd.Timestamp.now() >= x['start_date'] and pd.Timestamp.now() <= x['end_date'] 
                if pd.notna(x['start_date']) and pd.notna(x['end_date']) else False, axis=1
            )
        
        # Convert project_size to numeric (it contains text like "$50k-$500k")
        if 'project_size' in processed.columns:
            # Map size ranges to numeric values
            size_mapping = {
                '<$50k': 25000,
                '$50k-$500k': 275000,
                '$500k-$1M': 750000,
                '>$1M': 1500000
            }
            processed['project_size_numeric'] = processed['project_size'].map(size_mapping).fillna(25000)
        
        # Standardize practice names
        if 'practice' in processed.columns:
            practice_mapping = {
                'CLD & PLT': 'Cloud_Platform',
                'NTWK & CYB': 'Network_Cyber',
                'AI & D': 'AI_Data',
                'Other': 'Other'
            }
            processed['practice_category'] = processed['practice'].map(practice_mapping).fillna('Other')
        
        return processed
    
    def preprocess_service_credits(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and enhance service credits data"""
        processed = df.copy()
        
        # Standardize column names
        column_mapping = {
            'ProjectID': 'project_id',
            'ProjectName': 'project_name',
            'PracticeName': 'practice_name',
            'PurchasedCredits': 'purchased_credits',
            'ConvertedCredits': 'converted_credits',
            'DeliveredCredits': 'delivered_credits',
            'ConvertedNotDeliveredCredits': 'converted_not_delivered',
            'ActiveCredits': 'active_credits',
            'ExpiryInDays': 'expiry_days',
            'ContractEndDate': 'contract_end_date'
        }
        processed.rename(columns=column_mapping, inplace=True)
        
        # Convert dates
        if 'contract_end_date' in processed.columns:
            processed['contract_end_date'] = pd.to_datetime(processed['contract_end_date'], errors='coerce')
            processed['days_to_contract_end'] = (processed['contract_end_date'] - pd.Timestamp.now()).dt.days
            processed['contract_urgency'] = processed['days_to_contract_end'].apply(
                lambda x: 'Critical' if x < 30 else 'High' if x < 90 else 'Medium' if x < 180 else 'Low' if pd.notna(x) else 'Unknown'
            )
        
        # Calculate utilization metrics
        if 'purchased_credits' in processed.columns and 'delivered_credits' in processed.columns:
            processed['credit_utilization'] = processed.apply(
                lambda x: x['delivered_credits'] / x['purchased_credits'] 
                if x['purchased_credits'] > 0 else 0, axis=1
            )
            processed['utilization_status'] = processed['credit_utilization'].apply(
                lambda x: 'Fully Utilized' if x >= 0.9 else 'High' if x >= 0.7 else 'Medium' if x >= 0.4 else 'Low'
            )
        
        if 'purchased_credits' in processed.columns and 'active_credits' in processed.columns:
            processed['remaining_credits'] = processed['active_credits']
            processed['consumed_credits'] = processed['purchased_credits'] - processed['active_credits']
        
        return processed
    
    def preprocess_services(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and enhance services catalog data"""
        processed = df.copy()
        
        # Standardize column names
        column_mapping = {
            'Practice': 'practice',
            'Sub-Practice': 'sub_practice',
            'Services': 'service_name'
        }
        processed.rename(columns=column_mapping, inplace=True)
        
        # Create service hierarchy
        processed['service_category'] = processed['practice'].fillna('Unknown')
        processed['service_subcategory'] = processed['sub_practice'].fillna('Unknown')
        
        # Create service ID for referencing
        processed['service_id'] = processed.index + 1
        
        return processed
    
    def create_customer_mapping(self) -> pd.DataFrame:
        """Create mapping between different customer ID systems"""
        mapping_records = []
        
        # Get 5-digit customer IDs from Install Base and Opportunities
        if 'install_base' in self.processed_data:
            ib_customers = self.processed_data['install_base']['account_sales_territory_id'].dropna().unique()
            for cust_id in ib_customers:
                mapping_records.append({
                    'customer_id_5digit': int(cust_id),
                    'source': 'install_base'
                })
        
        if 'opportunities' in self.processed_data:
            opp_customers = self.processed_data['opportunities']['account_st_id'].dropna().unique()
            for cust_id in opp_customers:
                mapping_records.append({
                    'customer_id_5digit': int(cust_id),
                    'source': 'opportunities'
                })
        
        # Get 9-digit customer IDs from A&PS Projects
        if 'aps_projects' in self.processed_data:
            proj_customers = self.processed_data['aps_projects']['customer_id'].dropna().unique()
            for cust_id in proj_customers:
                mapping_records.append({
                    'customer_id_9digit': int(cust_id),
                    'source': 'aps_projects'
                })
        
        # Create mapping dataframe
        mapping_df = pd.DataFrame(mapping_records)
        
        # Deduplicate 5-digit IDs
        if 'customer_id_5digit' in mapping_df.columns:
            mapping_5digit = mapping_df[mapping_df['customer_id_5digit'].notna()][['customer_id_5digit']].drop_duplicates()
            mapping_5digit['unified_customer_id'] = range(1000, 1000 + len(mapping_5digit))
        else:
            mapping_5digit = pd.DataFrame()
        
        # Deduplicate 9-digit IDs
        if 'customer_id_9digit' in mapping_df.columns:
            mapping_9digit = mapping_df[mapping_df['customer_id_9digit'].notna()][['customer_id_9digit']].drop_duplicates()
            start_id = 1000 + len(mapping_5digit) if not mapping_5digit.empty else 1000
            mapping_9digit['unified_customer_id'] = range(start_id, start_id + len(mapping_9digit))
        else:
            mapping_9digit = pd.DataFrame()
        
        # Combine mappings
        if not mapping_5digit.empty and not mapping_9digit.empty:
            customer_mapping = pd.concat([
                mapping_5digit.rename(columns={'customer_id_5digit': 'original_id'}),
                mapping_9digit.rename(columns={'customer_id_9digit': 'original_id'})
            ], ignore_index=True)
        elif not mapping_5digit.empty:
            customer_mapping = mapping_5digit.rename(columns={'customer_id_5digit': 'original_id'})
        elif not mapping_9digit.empty:
            customer_mapping = mapping_9digit.rename(columns={'customer_id_9digit': 'original_id'})
        else:
            customer_mapping = pd.DataFrame(columns=['original_id', 'unified_customer_id'])
        
        return customer_mapping
    
    def process_all_data(self) -> Dict[str, pd.DataFrame]:
        """Process all data sheets with appropriate preprocessing"""
        if not self.raw_data:
            self.load_excel_data()
        
        processing_functions = {
            'install_base': self.preprocess_install_base,
            'opportunities': self.preprocess_opportunities,
            'aps_projects': self.preprocess_aps_projects,
            'service_credits': self.preprocess_service_credits,
            'services': self.preprocess_services
        }
        
        for sheet_name, df in self.raw_data.items():
            if sheet_name in processing_functions:
                logger.info(f"Processing {sheet_name}")
                self.processed_data[sheet_name] = processing_functions[sheet_name](df)
            else:
                logger.warning(f"No preprocessing function for {sheet_name}")
                self.processed_data[sheet_name] = df
        
        # Create customer mapping
        self.processed_data['customer_mapping'] = self.create_customer_mapping()
        
        return self.processed_data
    
    def get_data_summary(self) -> Dict[str, Dict]:
        """Get summary statistics for all datasets"""
        summary = {}
        
        for name, df in self.processed_data.items():
            if name != 'customer_mapping':  # Skip mapping table
                summary[name] = {
                    'records': len(df),
                    'columns': len(df.columns),
                    'missing_data_pct': (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
                    'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024
                }
        
        return summary