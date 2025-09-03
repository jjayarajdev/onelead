"""
Utility to map customer IDs to customer names
"""

import pandas as pd
from typing import Dict, Optional, Union

class CustomerNameMapper:
    """Maps customer IDs to their actual names"""
    
    def __init__(self, processed_data: Dict[str, pd.DataFrame]):
        self.id_to_name = self._build_customer_mapping(processed_data)
    
    def _build_customer_mapping(self, processed_data: Dict[str, pd.DataFrame]) -> Dict:
        """Build a mapping of customer IDs to names from available data sources"""
        
        id_to_name = {}
        
        # Try to get names from opportunities data first (most reliable)
        if 'opportunities' in processed_data:
            opp = processed_data['opportunities']
            if 'account_st_id' in opp.columns and 'account_name' in opp.columns:
                for _, row in opp[['account_st_id', 'account_name']].drop_duplicates().iterrows():
                    if pd.notna(row['account_st_id']) and pd.notna(row['account_name']):
                        id_to_name[str(int(row['account_st_id']))] = row['account_name']
        
        # Also check install base data
        if 'install_base' in processed_data:
            ib = processed_data['install_base']
            if 'account_sales_territory_id' in ib.columns and 'account_sales_territory_name' in ib.columns:
                for _, row in ib[['account_sales_territory_id', 'account_sales_territory_name']].drop_duplicates().iterrows():
                    if pd.notna(row['account_sales_territory_id']) and pd.notna(row['account_sales_territory_name']):
                        id_str = str(int(row['account_sales_territory_id']))
                        if id_str not in id_to_name:  # Don't overwrite if already have name
                            id_to_name[id_str] = row['account_sales_territory_name']
        
        # Check A&PS projects data
        if 'aps_projects' in processed_data:
            aps = processed_data['aps_projects']
            if 'customer_id' in aps.columns and 'customer_name' in aps.columns:
                for _, row in aps[['customer_id', 'customer_name']].drop_duplicates().iterrows():
                    if pd.notna(row['customer_id']) and pd.notna(row['customer_name']):
                        id_str = str(row['customer_id'])
                        if id_str not in id_to_name:
                            id_to_name[id_str] = row['customer_name']
        
        return id_to_name
    
    def get_name(self, customer_id: Union[int, str, float], default: Optional[str] = None) -> str:
        """Get customer name for given ID"""
        
        if pd.isna(customer_id) or customer_id == '' or customer_id is None:
            return default or "Unknown"
        
        # Convert to string for lookup
        try:
            if isinstance(customer_id, (int, float)):
                id_str = str(int(customer_id))
            else:
                id_str = str(customer_id).strip()
                # Try to extract numeric part if it's already formatted
                if id_str.startswith('Customer '):
                    return id_str  # Already formatted
                # Try to convert to int then string to normalize
                try:
                    id_str = str(int(float(id_str)))
                except:
                    pass
            
            # Look up the name
            name = self.id_to_name.get(id_str)
            if name:
                return name
            else:
                # Return formatted ID if no name found
                try:
                    return default or f"Customer {int(float(id_str))}"
                except:
                    return default or f"Customer {id_str}"
        except Exception as e:
            return default or "Unknown"
    
    def map_series(self, series: pd.Series, default: Optional[str] = None) -> pd.Series:
        """Map a pandas series of customer IDs to names"""
        return series.apply(lambda x: self.get_name(x, default))
    
    def map_dataframe_column(self, df: pd.DataFrame, column: str, inplace: bool = False) -> pd.DataFrame:
        """Map a specific column in a dataframe from IDs to names"""
        if not inplace:
            df = df.copy()
        
        df[column] = self.map_series(df[column])
        return df
    
    def get_all_customer_names(self) -> Dict[str, str]:
        """Get all customer ID to name mappings"""
        return self.id_to_name.copy()