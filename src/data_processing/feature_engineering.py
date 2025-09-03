"""
HPE OneLead Feature Engineering
Creates predictive features for opportunity scoring
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class OneleadFeatureEngineer:
    """Create features for HPE OneLead opportunity prediction"""
    
    def __init__(self, processed_data: Dict[str, pd.DataFrame]):
        self.data = processed_data
        self.features = pd.DataFrame()
        
    def create_customer_master(self) -> pd.DataFrame:
        """Create master customer list with unified identifiers"""
        customers = set()
        
        # Collect all customer identifiers
        if 'Raw_install_base' in self.data:
            customers.update(self.data['Raw_install_base']['account_sales_territory_id'].dropna().unique())
        
        if 'Raw_opportunities' in self.data:
            customers.update(self.data['Raw_opportunities']['account_sales_territory_id'].dropna().unique())
        
        if 'Raw_projects' in self.data:
            customers.update(self.data['Raw_projects']['prj_customer_id'].dropna().unique())
        
        # Create master customer DataFrame
        master_customers = pd.DataFrame({
            'customer_id': list(customers)
        })
        
        return master_customers
    
    def create_install_base_features(self, customers: pd.DataFrame) -> pd.DataFrame:
        """Create features from install base data"""
        if 'Raw_install_base' not in self.data:
            return customers
        
        ib_data = self.data['Raw_install_base']
        
        # Safe aggregation with proper handling of data types
        agg_dict = {}
        
        # Count total products
        if 'product_id' in ib_data.columns:
            agg_dict['product_id'] = 'count'
        
        # EOL metrics - only if numeric
        if 'days_to_eol' in ib_data.columns and pd.api.types.is_numeric_dtype(ib_data['days_to_eol']):
            agg_dict['days_to_eol'] = ['min', 'mean', 'count']
        
        # EOS metrics - only if numeric
        if 'days_to_eos' in ib_data.columns and pd.api.types.is_numeric_dtype(ib_data['days_to_eos']):
            agg_dict['days_to_eos'] = ['min', 'mean', 'count']
        
        # Platform diversity
        if 'product_platform_description_name' in ib_data.columns:
            agg_dict['product_platform_description_name'] = 'nunique'
        
        # Active support count
        if 'support_status' in ib_data.columns:
            agg_dict['support_status'] = lambda x: (x == 'Active').sum()
        
        if not agg_dict:
            return customers
        
        # Aggregate install base metrics by customer
        ib_features = ib_data.groupby('account_sales_territory_id').agg(agg_dict).reset_index()
        
        # Flatten column names dynamically
        new_columns = ['customer_id']
        
        for col in ib_features.columns[1:]:
            if isinstance(col, tuple):
                if col[1] == 'count' and col[0] == 'product_id':
                    new_columns.append('total_products')
                elif col[1] == 'min' and 'eol' in col[0]:
                    new_columns.append('min_days_to_eol')
                elif col[1] == 'mean' and 'eol' in col[0]:
                    new_columns.append('avg_days_to_eol')
                elif col[1] == 'count' and 'eol' in col[0]:
                    new_columns.append('products_with_eol')
                elif col[1] == 'min' and 'eos' in col[0]:
                    new_columns.append('min_days_to_eos')
                elif col[1] == 'mean' and 'eos' in col[0]:
                    new_columns.append('avg_days_to_eos')
                elif col[1] == 'count' and 'eos' in col[0]:
                    new_columns.append('products_with_eos')
                else:
                    new_columns.append('_'.join(col))
            else:
                if 'platform' in col:
                    new_columns.append('platform_diversity')
                elif 'support' in col:
                    new_columns.append('active_support_count')
                else:
                    new_columns.append(col)
        
        ib_features.columns = new_columns
        
        # Create risk flags safely
        if 'min_days_to_eol' in ib_features.columns:
            ib_features['eol_urgency_score'] = np.where(
                ib_features['min_days_to_eol'] < 365, 3,
                np.where(ib_features['min_days_to_eol'] < 730, 2, 1)
            )
        else:
            ib_features['eol_urgency_score'] = 0
        
        if 'min_days_to_eos' in ib_features.columns:
            ib_features['eos_urgency_score'] = np.where(
                ib_features['min_days_to_eos'] < 365, 3,
                np.where(ib_features['min_days_to_eos'] < 730, 2, 1)
            )
        else:
            ib_features['eos_urgency_score'] = 0
        
        # Merge with customers
        return customers.merge(ib_features, on='customer_id', how='left')
    
    def create_opportunity_features(self, customers: pd.DataFrame) -> pd.DataFrame:
        """Create features from opportunities data"""
        if 'Raw_opportunities' not in self.data:
            return customers
        
        opp_data = self.data['Raw_opportunities']
        
        # Safe aggregation with proper handling of data types
        agg_dict = {}
        
        # Count opportunities
        if 'opportunityid__c' in opp_data.columns:
            agg_dict['opportunityid__c'] = 'count'
        
        # Product line diversity
        if 'product_line__c' in opp_data.columns:
            agg_dict['product_line__c'] = 'nunique'
        
        # Description length - only if numeric
        if 'opportunity_description_length' in opp_data.columns and pd.api.types.is_numeric_dtype(opp_data['opportunity_description_length']):
            agg_dict['opportunity_description_length'] = 'mean'
        
        # Has description count
        if 'has_description' in opp_data.columns:
            agg_dict['has_description'] = 'sum'
        
        if not agg_dict:
            return customers
        
        # Aggregate opportunity metrics by customer
        opp_features = opp_data.groupby('account_sales_territory_id').agg(agg_dict).reset_index()
        
        # Create column names dynamically
        new_columns = ['customer_id']
        for col in opp_features.columns[1:]:
            if 'opportunityid' in col:
                new_columns.append('total_opportunities')
            elif 'product_line' in col:
                new_columns.append('opportunity_product_lines')
            elif 'description_length' in col:
                new_columns.append('avg_opp_description_length')
            elif 'has_description' in col:
                new_columns.append('opportunities_with_description')
            else:
                new_columns.append(col)
        
        opp_features.columns = new_columns
        
        # Recent opportunity activity
        if 'total_opportunities' in opp_features.columns:
            opp_features['has_active_opportunities'] = opp_features['total_opportunities'] > 0
        else:
            opp_features['has_active_opportunities'] = False
        
        return customers.merge(opp_features, on='customer_id', how='left')
    
    def create_service_credit_features(self, customers: pd.DataFrame) -> pd.DataFrame:
        """Create features from service credits data"""
        if 'Raw_service_credits' not in self.data:
            return customers
        
        sc_data = self.data['Raw_service_credits']
        
        # Since service credits data might not have direct customer linking,
        # we'll create aggregate metrics but return them as global features
        # or skip if we can't find a proper customer identifier
        
        # Check for common customer identifier columns
        customer_id_cols = ['customer_id', 'account_id', 'account_sales_territory_id']
        customer_col = None
        
        for col in customer_id_cols:
            if col in sc_data.columns:
                customer_col = col
                break
        
        if customer_col is None:
            # No customer identifier found, add default values
            customers['total_purchased_credits'] = 0
            customers['total_contracts'] = 0
            customers['total_active_credits'] = 0
            customers['total_delivered_credits'] = 0
            customers['avg_credit_utilization'] = 0
            customers['avg_delivery_rate'] = 0
            customers['min_days_to_contract_end'] = 999
            customers['practice_diversity'] = 0
            customers['low_utilization_risk'] = False
            customers['contract_renewal_urgency'] = False
            return customers
        
        # Safe aggregation with proper handling of data types
        agg_dict = {}
        
        # Credit metrics - only if numeric
        if 'purchasedcredits' in sc_data.columns and pd.api.types.is_numeric_dtype(sc_data['purchasedcredits']):
            agg_dict['purchasedcredits'] = ['sum', 'count']
        
        if 'activecredits' in sc_data.columns and pd.api.types.is_numeric_dtype(sc_data['activecredits']):
            agg_dict['activecredits'] = 'sum'
        
        if 'deliveredcredits' in sc_data.columns and pd.api.types.is_numeric_dtype(sc_data['deliveredcredits']):
            agg_dict['deliveredcredits'] = 'sum'
        
        if 'credit_utilization' in sc_data.columns and pd.api.types.is_numeric_dtype(sc_data['credit_utilization']):
            agg_dict['credit_utilization'] = 'mean'
        
        if 'delivery_rate' in sc_data.columns and pd.api.types.is_numeric_dtype(sc_data['delivery_rate']):
            agg_dict['delivery_rate'] = 'mean'
        
        if 'days_to_contract_end' in sc_data.columns and pd.api.types.is_numeric_dtype(sc_data['days_to_contract_end']):
            agg_dict['days_to_contract_end'] = 'min'
        
        if 'practicename' in sc_data.columns:
            agg_dict['practicename'] = 'nunique'
        
        if not agg_dict:
            # No valid aggregation columns, add defaults
            customers['total_purchased_credits'] = 0
            customers['total_contracts'] = 0
            customers['total_active_credits'] = 0
            customers['total_delivered_credits'] = 0
            customers['avg_credit_utilization'] = 0
            customers['avg_delivery_rate'] = 0
            customers['min_days_to_contract_end'] = 999
            customers['practice_diversity'] = 0
            customers['low_utilization_risk'] = False
            customers['contract_renewal_urgency'] = False
            return customers
        
        sc_features = sc_data.groupby(customer_col).agg(agg_dict).reset_index()
        
        # Create column names dynamically
        new_columns = ['customer_id']
        for col in sc_features.columns[1:]:
            if isinstance(col, tuple):
                if col[1] == 'sum' and 'purchased' in col[0]:
                    new_columns.append('total_purchased_credits')
                elif col[1] == 'count' and 'purchased' in col[0]:
                    new_columns.append('total_contracts')
                elif col[1] == 'sum' and 'active' in col[0]:
                    new_columns.append('total_active_credits')
                elif col[1] == 'sum' and 'delivered' in col[0]:
                    new_columns.append('total_delivered_credits')
                elif col[1] == 'mean' and 'utilization' in col[0]:
                    new_columns.append('avg_credit_utilization')
                elif col[1] == 'mean' and 'delivery' in col[0]:
                    new_columns.append('avg_delivery_rate')
                elif col[1] == 'min' and 'contract' in col[0]:
                    new_columns.append('min_days_to_contract_end')
                else:
                    new_columns.append('_'.join(col))
            else:
                if 'practice' in col:
                    new_columns.append('practice_diversity')
                else:
                    new_columns.append(col)
        
        sc_features.columns = new_columns
        
        # Create utilization risk flags safely
        if 'avg_credit_utilization' in sc_features.columns:
            sc_features['low_utilization_risk'] = sc_features['avg_credit_utilization'] < 0.5
        else:
            sc_features['low_utilization_risk'] = False
        
        if 'min_days_to_contract_end' in sc_features.columns:
            sc_features['contract_renewal_urgency'] = sc_features['min_days_to_contract_end'] < 90
        else:
            sc_features['contract_renewal_urgency'] = False
        
        return customers.merge(sc_features, on='customer_id', how='left')
    
    def create_project_features(self, customers: pd.DataFrame) -> pd.DataFrame:
        """Create features from projects data"""
        if 'Raw_projects' not in self.data:
            return customers
        
        proj_data = self.data['Raw_projects']
        
        # Safe aggregation with proper handling of data types
        agg_dict = {}
        
        # Count projects
        if 'project' in proj_data.columns:
            agg_dict['project'] = 'count'
        
        # Project size metrics - only if numeric
        if 'prj_size' in proj_data.columns and pd.api.types.is_numeric_dtype(proj_data['prj_size']):
            agg_dict['prj_size'] = ['mean', 'sum']
        
        # Project length - only if numeric
        if 'prj_length' in proj_data.columns and pd.api.types.is_numeric_dtype(proj_data['prj_length']):
            agg_dict['prj_length'] = 'mean'
        
        # Days since start - only if numeric
        if 'days_since_start' in proj_data.columns and pd.api.types.is_numeric_dtype(proj_data['days_since_start']):
            agg_dict['days_since_start'] = 'min'
        
        # Practice diversity
        if 'prj_practice' in proj_data.columns:
            agg_dict['prj_practice'] = 'nunique'
        
        # Geographic diversity
        if 'country_id' in proj_data.columns:
            agg_dict['country_id'] = 'nunique'
        
        # Project success
        if 'project_success' in proj_data.columns:
            agg_dict['project_success'] = lambda x: (x == 'Success').sum()
        
        if not agg_dict:
            return customers
        
        # Aggregate project metrics by customer
        proj_features = proj_data.groupby('prj_customer_id').agg(agg_dict).reset_index()
        
        # Create column names dynamically
        new_columns = ['customer_id']
        for col in proj_features.columns[1:]:
            if isinstance(col, tuple):
                if col[1] == 'count' and col[0] == 'project':
                    new_columns.append('total_projects')
                elif col[1] == 'mean' and 'size' in col[0]:
                    new_columns.append('avg_project_size')
                elif col[1] == 'sum' and 'size' in col[0]:
                    new_columns.append('total_project_value')
                elif col[1] == 'mean' and 'length' in col[0]:
                    new_columns.append('avg_project_length')
                elif col[1] == 'min' and 'days_since' in col[0]:
                    new_columns.append('days_since_last_project')
                else:
                    new_columns.append('_'.join(col))
            else:
                if 'practice' in col:
                    new_columns.append('practice_diversity')
                elif 'country' in col:
                    new_columns.append('geographic_diversity')
                elif 'success' in col:
                    new_columns.append('successful_projects')
                else:
                    new_columns.append(col)
        
        proj_features.columns = new_columns
        
        # Calculate success rate safely
        if 'successful_projects' in proj_features.columns and 'total_projects' in proj_features.columns:
            proj_features['project_success_rate'] = (
                proj_features['successful_projects'] / proj_features['total_projects']
            ).fillna(0)
        else:
            proj_features['project_success_rate'] = 0
        
        # Engagement recency safely
        if 'days_since_last_project' in proj_features.columns:
            proj_features['recent_engagement'] = proj_features['days_since_last_project'] < 90
        else:
            proj_features['recent_engagement'] = False
        
        return customers.merge(proj_features, on='customer_id', how='left')
    
    def create_rfm_features(self, customers: pd.DataFrame) -> pd.DataFrame:
        """Create RFM (Recency, Frequency, Monetary) style features"""
        features = customers.copy()
        
        # Recency - Most recent interaction
        recency_cols = ['days_since_last_project', 'min_days_to_contract_end']
        features['recency_score'] = 0
        
        for col in recency_cols:
            if col in features.columns:
                # Lower days = higher recency score, handle NaN
                col_data = features[col].fillna(999)  # Default to high value for missing
                features['recency_score'] += np.where(
                    col_data < 30, 3,
                    np.where(col_data < 90, 2, 1)
                )
        
        # Frequency - Interaction frequency
        frequency_cols = ['total_projects', 'total_opportunities', 'total_contracts']
        features['frequency_score'] = 0
        
        for col in frequency_cols:
            if col in features.columns:
                col_data = features[col].fillna(0)  # Default to 0 for missing
                q75 = col_data.quantile(0.75)
                q50 = col_data.quantile(0.5)
                features['frequency_score'] += np.where(
                    col_data >= q75, 3,
                    np.where(col_data >= q50, 2, 1)
                )
        
        # Monetary - Value indicators
        monetary_cols = ['total_project_value', 'total_purchased_credits']
        features['monetary_score'] = 0
        
        for col in monetary_cols:
            if col in features.columns:
                col_data = features[col].fillna(0)  # Default to 0 for missing
                q75 = col_data.quantile(0.75)
                q50 = col_data.quantile(0.5)
                features['monetary_score'] += np.where(
                    col_data >= q75, 3,
                    np.where(col_data >= q50, 2, 1)
                )
        
        # Combined RFM score
        features['rfm_score'] = (
            features['recency_score'] + 
            features['frequency_score'] + 
            features['monetary_score']
        )
        
        return features
    
    def create_urgency_features(self, customers: pd.DataFrame) -> pd.DataFrame:
        """Create urgency-based features for opportunity prioritization"""
        features = customers.copy()
        
        # Initialize urgency score
        features['urgency_score'] = 0
        
        # EOL/EOS urgency
        if 'eol_urgency_score' in features.columns:
            features['urgency_score'] += features['eol_urgency_score'].fillna(0)
        
        if 'eos_urgency_score' in features.columns:
            features['urgency_score'] += features['eos_urgency_score'].fillna(0)
        
        # Contract renewal urgency
        if 'contract_renewal_urgency' in features.columns:
            features['urgency_score'] += features['contract_renewal_urgency'].fillna(False).astype(int)
        
        # Low utilization urgency
        if 'low_utilization_risk' in features.columns:
            features['urgency_score'] += features['low_utilization_risk'].fillna(False).astype(int)
        
        return features
    
    def create_opportunity_propensity_score(self, customers: pd.DataFrame) -> pd.DataFrame:
        """Create final opportunity propensity score"""
        features = customers.copy()
        
        # Weighted combination of different factors
        weights = {
            'urgency_score': 0.3,
            'rfm_score': 0.25,
            'project_success_rate': 0.2,
            'platform_diversity': 0.1,
            'practice_diversity': 0.1,
            'has_active_opportunities': 0.05
        }
        
        # Normalize features to 0-1 scale
        propensity_score = 0
        
        for feature, weight in weights.items():
            if feature in features.columns:
                if feature == 'has_active_opportunities':
                    normalized = features[feature].fillna(False).astype(int)
                else:
                    col_data = features[feature].fillna(0)
                    col_max = col_data.max()
                    col_min = col_data.min()
                    if col_max > col_min and not pd.isna(col_max) and not pd.isna(col_min):
                        normalized = (col_data - col_min) / (col_max - col_min)
                    else:
                        normalized = col_data * 0
                
                propensity_score += normalized * weight
        
        features['opportunity_propensity_score'] = propensity_score
        
        # Create propensity tiers
        score_col = features['opportunity_propensity_score']
        score_min = score_col.min()
        score_max = score_col.max()
        
        # Simple tier assignment based on quantiles
        try:
            features['propensity_tier'] = pd.qcut(
                score_col,
                q=3,
                labels=['Low', 'Medium', 'High'],
                duplicates='drop'
            )
        except ValueError:
            # If qcut fails due to duplicate values, use simple thresholds
            q33 = score_col.quantile(0.33)
            q66 = score_col.quantile(0.66)
            
            features['propensity_tier'] = np.where(
                score_col <= q33, 'Low',
                np.where(score_col <= q66, 'Medium', 'High')
            )
        
        return features
    
    def build_feature_set(self) -> pd.DataFrame:
        """Build complete feature set for opportunity scoring"""
        logger.info("Building customer master list")
        customers = self.create_customer_master()
        
        logger.info("Creating install base features")
        customers = self.create_install_base_features(customers)
        
        logger.info("Creating opportunity features")
        customers = self.create_opportunity_features(customers)
        
        logger.info("Creating service credit features")  
        customers = self.create_service_credit_features(customers)
        
        logger.info("Creating project features")
        customers = self.create_project_features(customers)
        
        logger.info("Creating RFM features")
        customers = self.create_rfm_features(customers)
        
        logger.info("Creating urgency features")
        customers = self.create_urgency_features(customers)
        
        logger.info("Creating propensity scores")
        customers = self.create_opportunity_propensity_score(customers)
        
        # Fill missing values
        customers = customers.fillna(0)
        
        self.features = customers
        return customers
    
    def get_top_opportunities(self, n: int = 50) -> pd.DataFrame:
        """Get top N opportunities ranked by propensity score"""
        if self.features.empty:
            self.build_feature_set()
        
        return self.features.nlargest(n, 'opportunity_propensity_score')
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Calculate feature importance for opportunity scoring"""
        if self.features.empty:
            return {}
        
        # Simple correlation with propensity score
        numeric_features = self.features.select_dtypes(include=[np.number]).columns
        numeric_features = [col for col in numeric_features if col != 'opportunity_propensity_score']
        
        importance = {}
        for feature in numeric_features:
            correlation = self.features[feature].corr(self.features['opportunity_propensity_score'])
            importance[feature] = abs(correlation) if not pd.isna(correlation) else 0
        
        # Sort by importance
        return dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))