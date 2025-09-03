"""
HPE OneLead Data Loader
Handles Excel file ingestion and initial preprocessing
"""

import pandas as pd
from typing import Dict, List, Optional
import logging
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OneleadDataLoader:
    """Load and preprocess HPE OneLead consolidated data"""
    
    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self.raw_data = {}
        self.processed_data = {}
        
    def load_excel_data(self) -> Dict[str, pd.DataFrame]:
        """Load all sheets from the Excel file"""
        try:
            logger.info(f"Loading data from {self.data_path}")
            
            # Load all sheets
            excel_file = pd.ExcelFile(self.data_path)
            
            for sheet_name in excel_file.sheet_names:
                logger.info(f"Loading sheet: {sheet_name}")
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                self.raw_data[sheet_name] = df
                logger.info(f"Loaded {len(df)} records from {sheet_name}")
                
            return self.raw_data
            
        except Exception as e:
            logger.error(f"Error loading Excel data: {e}")
            raise
    
    def preprocess_install_base(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and enhance install base data"""
        processed = df.copy()
        
        # Convert dates
        date_columns = ['product_end_of_life_date', 'product_end_of_service_life_date', 
                       'final_service_start_date']
        for col in date_columns:
            if col in processed.columns:
                processed[col] = pd.to_datetime(processed[col], errors='coerce')
        
        # Calculate days until end-of-life/service
        if 'product_end_of_life_date' in processed.columns:
            processed['days_to_eol'] = (processed['product_end_of_life_date'] - pd.Timestamp.now()).dt.days
            processed['eol_risk'] = processed['days_to_eol'].apply(
                lambda x: 'High' if x < 365 else 'Medium' if x < 730 else 'Low' if pd.notna(x) else 'Unknown'
            )
        
        if 'product_end_of_service_life_date' in processed.columns:
            processed['days_to_eos'] = (processed['product_end_of_service_life_date'] - pd.Timestamp.now()).dt.days
            processed['eos_risk'] = processed['days_to_eos'].apply(
                lambda x: 'High' if x < 365 else 'Medium' if x < 730 else 'Low' if pd.notna(x) else 'Unknown'
            )
        
        return processed
    
    def preprocess_opportunities(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and enhance opportunities data"""
        processed = df.copy()
        
        # Extract opportunity value if available in description
        # This would need to be customized based on actual data patterns
        processed['opportunity_description_length'] = processed['opportunity_description'].fillna('').str.len()
        processed['has_description'] = processed['opportunity_description'].notna()
        
        return processed
    
    def preprocess_service_credits(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and enhance service credits data"""
        processed = df.copy()
        
        # Convert dates
        if 'contractenddate' in processed.columns:
            processed['contractenddate'] = pd.to_datetime(processed['contractenddate'], errors='coerce')
            processed['days_to_contract_end'] = (processed['contractenddate'] - pd.Timestamp.now()).dt.days
        
        # Calculate utilization metrics
        if 'purchasedcredits' in processed.columns and 'activecredits' in processed.columns:
            processed['credit_utilization'] = (
                processed['purchasedcredits'] - processed['activecredits']
            ) / processed['purchasedcredits']
            processed['credit_utilization'] = processed['credit_utilization'].fillna(0)
        
        if 'deliveredcredits' in processed.columns and 'purchasedcredits' in processed.columns:
            processed['delivery_rate'] = processed['deliveredcredits'] / processed['purchasedcredits']
            processed['delivery_rate'] = processed['delivery_rate'].fillna(0)
        
        # Risk flags
        processed['contract_renewal_risk'] = processed['days_to_contract_end'].apply(
            lambda x: 'High' if x < 90 else 'Medium' if x < 180 else 'Low' if pd.notna(x) else 'Unknown'
        )
        
        return processed
    
    def preprocess_projects(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and enhance projects data"""
        processed = df.copy()
        
        # Convert dates
        date_columns = ['prj_start_date', 'prj_end_date']
        for col in date_columns:
            if col in processed.columns:
                processed[col] = pd.to_datetime(processed[col], errors='coerce')
        
        # Calculate project metrics
        if 'prj_start_date' in processed.columns:
            processed['days_since_start'] = (pd.Timestamp.now() - processed['prj_start_date']).dt.days
            processed['project_recency'] = processed['days_since_start'].apply(
                lambda x: 'Recent' if x < 90 else 'Medium' if x < 365 else 'Old' if pd.notna(x) else 'Unknown'
            )
        
        # Project success indicators
        if 'prj_status_description' in processed.columns:
            processed['project_success'] = processed['prj_status_description'].apply(
                lambda x: 'Success' if pd.notna(x) and 'complete' in str(x).lower() else 'In Progress'
            )
        
        return processed
    
    def preprocess_services(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and enhance services data"""
        processed = df.copy()
        
        # Create service hierarchy
        processed['service_category'] = processed['practice'].fillna('Unknown')
        processed['service_subcategory'] = processed['sub_practice'].fillna('Unknown')
        
        return processed
    
    def process_all_data(self) -> Dict[str, pd.DataFrame]:
        """Process all data sheets with appropriate preprocessing"""
        if not self.raw_data:
            self.load_excel_data()
        
        processing_functions = {
            'Raw_install_base': self.preprocess_install_base,
            'Raw_opportunities': self.preprocess_opportunities,
            'Raw_service_credits': self.preprocess_service_credits,
            'Raw_projects': self.preprocess_projects,
            'Raw_services': self.preprocess_services
        }
        
        for sheet_name, df in self.raw_data.items():
            if sheet_name in processing_functions:
                logger.info(f"Processing {sheet_name}")
                self.processed_data[sheet_name] = processing_functions[sheet_name](df)
            else:
                logger.warning(f"No preprocessing function for {sheet_name}")
                self.processed_data[sheet_name] = df
        
        return self.processed_data
    
    def get_data_summary(self) -> Dict[str, Dict]:
        """Get summary statistics for all datasets"""
        summary = {}
        
        for name, df in self.processed_data.items():
            summary[name] = {
                'records': len(df),
                'columns': len(df.columns),
                'missing_data_pct': (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
                'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024
            }
        
        return summary