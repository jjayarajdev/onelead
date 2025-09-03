"""
HPE OneLead Feature Engineering V2
Creates predictive features for opportunity scoring with new data structure
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class OneleadFeatureEngineerV2:
    """Create features for HPE OneLead opportunity prediction with new data format"""
    
    def __init__(self, processed_data: Dict[str, pd.DataFrame]):
        self.data = processed_data
        self.features = pd.DataFrame()
        self.customer_mapping = processed_data.get('customer_mapping', pd.DataFrame())
        
    def create_customer_master(self) -> pd.DataFrame:
        """Create master customer list with unified identifiers"""
        customers = set()
        customer_records = []
        
        # Collect 5-digit customer IDs from Install Base
        if 'install_base' in self.data:
            df = self.data['install_base']
            for cust_id in df['account_sales_territory_id'].dropna().unique():
                customer_records.append({
                    'customer_id': int(cust_id),
                    'id_type': '5-digit',
                    'source': 'install_base'
                })
        
        # Collect 5-digit customer IDs from Opportunities
        if 'opportunities' in self.data:
            df = self.data['opportunities']
            for cust_id in df['account_st_id'].dropna().unique():
                customer_records.append({
                    'customer_id': int(cust_id),
                    'id_type': '5-digit',
                    'source': 'opportunities'
                })
        
        # Collect 9-digit customer IDs from A&PS Projects
        if 'aps_projects' in self.data:
            df = self.data['aps_projects']
            for cust_id in df['customer_id'].dropna().unique():
                customer_records.append({
                    'customer_id': int(cust_id),
                    'id_type': '9-digit',
                    'source': 'aps_projects'
                })
        
        # Create master dataframe
        if customer_records:
            master_df = pd.DataFrame(customer_records)
            # Deduplicate while keeping track of all sources
            master_customers = master_df.groupby('customer_id').agg({
                'id_type': 'first',
                'source': lambda x: ','.join(x.unique())
            }).reset_index()
        else:
            master_customers = pd.DataFrame(columns=['customer_id', 'id_type', 'source'])
        
        return master_customers
    
    def create_install_base_features(self, customers: pd.DataFrame) -> pd.DataFrame:
        """Create features from install base data"""
        if 'install_base' not in self.data or self.data['install_base'].empty:
            logger.warning("No install base data available")
            return customers
        
        ib_data = self.data['install_base']
        
        # Aggregate install base metrics by customer
        agg_dict = {
            'serial_number_id': 'count',  # Total products
            'product_platform_description_name': lambda x: x.nunique(),  # Platform diversity
            'support_status': lambda x: (x == 'Active Warranty').sum() if 'Active Warranty' in x.values else 0,  # Active support
        }
        
        # Add EOL/EOS metrics if available
        if 'days_to_eol' in ib_data.columns:
            agg_dict['days_to_eol'] = ['min', 'mean']
            agg_dict['eol_urgency_score'] = 'max'
        
        if 'days_to_eos' in ib_data.columns:
            agg_dict['days_to_eos'] = ['min', 'mean']
            agg_dict['eos_urgency_score'] = 'max'
        
        # Group by customer
        ib_features = ib_data.groupby('account_sales_territory_id').agg(agg_dict).reset_index()
        
        # Flatten column names
        ib_features.columns = ['_'.join(col).strip('_') if isinstance(col, tuple) else col 
                               for col in ib_features.columns]
        
        # Rename columns for clarity
        rename_dict = {
            'account_sales_territory_id': 'customer_id',
            'serial_number_id_count': 'total_products',
            'product_platform_description_name_<lambda>': 'platform_diversity',
            'support_status_<lambda>': 'active_warranty_count',
            'days_to_eol_min': 'min_days_to_eol',
            'days_to_eol_mean': 'avg_days_to_eol',
            'days_to_eos_min': 'min_days_to_eos',
            'days_to_eos_mean': 'avg_days_to_eos',
            'eol_urgency_score_max': 'max_eol_urgency',
            'eos_urgency_score_max': 'max_eos_urgency'
        }
        
        ib_features.rename(columns=rename_dict, inplace=True)
        
        # Add risk indicators
        if 'min_days_to_eol' in ib_features.columns:
            ib_features['has_eol_risk'] = ib_features['min_days_to_eol'] < 365
            ib_features['critical_eol_risk'] = ib_features['min_days_to_eol'] < 180
        
        # Merge with customers
        return customers.merge(ib_features, on='customer_id', how='left')
    
    def create_opportunity_features(self, customers: pd.DataFrame) -> pd.DataFrame:
        """Create features from opportunities data"""
        if 'opportunities' not in self.data or self.data['opportunities'].empty:
            logger.warning("No opportunities data available")
            return customers
        
        opp_data = self.data['opportunities']
        
        # Aggregate opportunity metrics by customer
        agg_dict = {
            'opportunity_id': 'count',  # Total opportunities
            'product_line': lambda x: x.nunique(),  # Product line diversity
            'has_opportunity': 'sum'  # Count of opportunities (all should be 1)
        }
        
        if 'product_category' in opp_data.columns:
            agg_dict['product_category'] = lambda x: x.nunique()
        
        # Group by customer
        opp_features = opp_data.groupby('account_st_id').agg(agg_dict).reset_index()
        
        # Flatten column names properly
        new_columns = []
        for col in opp_features.columns:
            if isinstance(col, tuple):
                new_columns.append('_'.join(str(c) for c in col if c != '<lambda>').strip('_'))
            else:
                new_columns.append(col)
        opp_features.columns = new_columns
        
        # Rename columns
        rename_dict = {
            'account_st_id': 'customer_id',
            'opportunity_id': 'total_opportunities',
            'product_line': 'product_line_diversity',
            'product_category': 'product_category_diversity',
            'has_opportunity': 'opportunity_count'
        }
        
        # Apply renames only if columns exist
        for old_name, new_name in rename_dict.items():
            if old_name in opp_features.columns:
                opp_features.rename(columns={old_name: new_name}, inplace=True)
        
        # Add opportunity intensity (check if column exists first)
        if 'total_opportunities' in opp_features.columns:
            opp_features['has_active_opportunities'] = opp_features['total_opportunities'] > 0
            opp_features['multi_opportunity'] = opp_features['total_opportunities'] > 1
        else:
            # Use opportunity_count if available
            if 'opportunity_count' in opp_features.columns:
                opp_features['has_active_opportunities'] = opp_features['opportunity_count'] > 0
                opp_features['multi_opportunity'] = opp_features['opportunity_count'] > 1
                opp_features['total_opportunities'] = opp_features['opportunity_count']
            else:
                opp_features['has_active_opportunities'] = False
                opp_features['multi_opportunity'] = False
                opp_features['total_opportunities'] = 0
        
        # Merge with customers
        return customers.merge(opp_features, on='customer_id', how='left')
    
    def create_project_features(self, customers: pd.DataFrame) -> pd.DataFrame:
        """Create features from A&PS projects data"""
        if 'aps_projects' not in self.data or self.data['aps_projects'].empty:
            logger.warning("No A&PS projects data available")
            return customers
        
        proj_data = self.data['aps_projects']
        
        # Aggregate project metrics by customer
        agg_dict = {
            'project_id': 'count',  # Total projects
        }
        
        # Add optional fields if they exist
        optional_aggs = {
            'practice': lambda x: x.nunique(),
            'practice_category': lambda x: x.nunique(),
            'country': lambda x: x.nunique(),
            'is_active': 'sum',
            'project_size_numeric': ['mean', 'sum'],  # Use numeric version
            'project_duration': 'mean',
            'days_since_start': 'min'
        }
        
        for col, agg_func in optional_aggs.items():
            if col in proj_data.columns:
                agg_dict[col] = agg_func
        
        # Group by customer
        proj_features = proj_data.groupby('customer_id').agg(agg_dict).reset_index()
        
        # Flatten column names
        new_columns = []
        for col in proj_features.columns:
            if isinstance(col, tuple):
                if col[1] in ['mean', 'sum', 'min', 'max']:
                    new_columns.append(f"{col[0]}_{col[1]}")
                else:
                    new_columns.append(col[0])
            else:
                new_columns.append(col)
        proj_features.columns = new_columns
        
        # Rename columns
        rename_dict = {
            'project_id': 'total_aps_projects',
            'practice': 'aps_practice_diversity',
            'practice_category': 'aps_practice_categories',
            'country': 'project_countries',
            'is_active': 'active_projects',
            'project_size_numeric_mean': 'avg_project_size',
            'project_size_numeric_sum': 'total_project_value',
            'project_duration': 'avg_project_duration',
            'days_since_start': 'days_since_last_project'
        }
        
        for old_name, new_name in rename_dict.items():
            if old_name in proj_features.columns:
                proj_features.rename(columns={old_name: new_name}, inplace=True)
        
        # Add engagement indicators
        if 'days_since_last_project' in proj_features.columns:
            proj_features['recent_aps_engagement'] = proj_features['days_since_last_project'] < 180
            proj_features['very_recent_aps_engagement'] = proj_features['days_since_last_project'] < 90
        
        # Note: A&PS projects use different customer IDs, so direct merge won't work
        # We'll need to handle this separately or use customer mapping
        return customers
    
    def create_service_credit_features(self, customers: pd.DataFrame) -> pd.DataFrame:
        """Create aggregated features from service credits data"""
        if 'service_credits' not in self.data or self.data['service_credits'].empty:
            logger.warning("No service credits data available")
            return customers
        
        sc_data = self.data['service_credits']
        
        # Since service credits are at project level and don't have customer IDs,
        # we'll create overall metrics
        overall_metrics = {
            'total_service_credit_projects': len(sc_data),
            'total_purchased_credits': sc_data['purchased_credits'].sum() if 'purchased_credits' in sc_data.columns else 0,
            'total_delivered_credits': sc_data['delivered_credits'].sum() if 'delivered_credits' in sc_data.columns else 0,
            'avg_credit_utilization': sc_data['credit_utilization'].mean() if 'credit_utilization' in sc_data.columns else 0,
        }
        
        # Add these as broadcast features (same for all customers)
        for metric_name, metric_value in overall_metrics.items():
            customers[f'org_{metric_name}'] = metric_value
        
        # Count projects with different urgency levels
        if 'contract_urgency' in sc_data.columns:
            urgency_counts = sc_data['contract_urgency'].value_counts()
            customers['org_critical_contracts'] = urgency_counts.get('Critical', 0)
            customers['org_high_urgency_contracts'] = urgency_counts.get('High', 0)
        
        return customers
    
    def create_rfm_features(self, customers: pd.DataFrame) -> pd.DataFrame:
        """Create RFM (Recency, Frequency, Monetary) style features"""
        features = customers.copy()
        
        # Recency Score - based on various time-based metrics
        features['recency_score'] = 0
        
        recency_metrics = {
            'days_since_last_project': lambda x: 3 if x < 90 else 2 if x < 180 else 1,
            'min_days_to_eol': lambda x: 3 if x < 365 else 2 if x < 730 else 1,
            'min_days_to_eos': lambda x: 3 if x < 365 else 2 if x < 730 else 1
        }
        
        for col, scoring_func in recency_metrics.items():
            if col in features.columns:
                features['recency_score'] += features[col].fillna(999).apply(scoring_func)
        
        # Frequency Score - based on volume metrics
        features['frequency_score'] = 0
        
        frequency_cols = ['total_products', 'total_opportunities', 'total_aps_projects']
        for col in frequency_cols:
            if col in features.columns:
                col_data = features[col].fillna(0)
                if col_data.max() > 0:
                    q75 = col_data.quantile(0.75)
                    q50 = col_data.quantile(0.50)
                    features['frequency_score'] += np.where(
                        col_data >= q75, 3,
                        np.where(col_data >= q50, 2, 1)
                    )
        
        # Monetary Score - based on value indicators
        features['monetary_score'] = 0
        
        monetary_cols = ['total_project_value', 'platform_diversity', 'product_line_diversity']
        for col in monetary_cols:
            if col in features.columns:
                col_data = features[col].fillna(0)
                if col_data.max() > 0:
                    q75 = col_data.quantile(0.75)
                    q50 = col_data.quantile(0.50)
                    features['monetary_score'] += np.where(
                        col_data >= q75, 3,
                        np.where(col_data >= q50, 2, 1)
                    )
        
        # Combined RFM score
        features['rfm_score'] = (
            features['recency_score'] * 0.3 + 
            features['frequency_score'] * 0.4 + 
            features['monetary_score'] * 0.3
        )
        
        return features
    
    def create_urgency_features(self, customers: pd.DataFrame) -> pd.DataFrame:
        """Create urgency-based features for opportunity prioritization"""
        features = customers.copy()
        
        # Composite urgency score
        features['urgency_score'] = 0
        
        # EOL/EOS urgency
        urgency_cols = {
            'max_eol_urgency': 1.0,
            'max_eos_urgency': 1.0,
            'critical_eol_risk': 2.0,
            'has_eol_risk': 1.0
        }
        
        for col, weight in urgency_cols.items():
            if col in features.columns:
                if features[col].dtype == bool:
                    features['urgency_score'] += features[col].astype(int) * weight
                else:
                    features['urgency_score'] += features[col].fillna(0) * weight
        
        # Normalize urgency score
        if features['urgency_score'].max() > 0:
            features['urgency_score'] = features['urgency_score'] / features['urgency_score'].max() * 10
        
        return features
    
    def create_opportunity_propensity_score(self, customers: pd.DataFrame) -> pd.DataFrame:
        """Create final opportunity propensity score"""
        features = customers.copy()
        
        # Define weights for different factors
        score_components = []
        weights = []
        
        # Add urgency component
        if 'urgency_score' in features.columns:
            score_components.append(features['urgency_score'].fillna(0) / 10)  # Normalize to 0-1
            weights.append(0.3)
        
        # Add RFM component
        if 'rfm_score' in features.columns:
            max_rfm = features['rfm_score'].max()
            if max_rfm > 0:
                score_components.append(features['rfm_score'].fillna(0) / max_rfm)
                weights.append(0.25)
        
        # Add opportunity presence
        if 'has_active_opportunities' in features.columns:
            score_components.append(features['has_active_opportunities'].fillna(0).astype(float))
            weights.append(0.15)
        
        # Add product diversity
        if 'platform_diversity' in features.columns:
            max_diversity = features['platform_diversity'].max()
            if max_diversity > 0:
                score_components.append(features['platform_diversity'].fillna(0) / max_diversity)
                weights.append(0.15)
        
        # Add engagement metrics
        engagement_cols = ['recent_aps_engagement', 'multi_opportunity']
        engagement_score = 0
        engagement_count = 0
        for col in engagement_cols:
            if col in features.columns:
                engagement_score += features[col].fillna(0).astype(float)
                engagement_count += 1
        
        if engagement_count > 0:
            score_components.append(engagement_score / engagement_count)
            weights.append(0.15)
        
        # Calculate weighted propensity score
        if score_components:
            # Normalize weights to sum to 1
            weights = np.array(weights)
            weights = weights / weights.sum()
            
            propensity_score = sum(comp * weight for comp, weight in zip(score_components, weights))
            features['opportunity_propensity_score'] = propensity_score
        else:
            features['opportunity_propensity_score'] = 0
        
        # Create propensity tiers
        score_col = features['opportunity_propensity_score']
        if score_col.std() > 0:
            q33 = score_col.quantile(0.33)
            q66 = score_col.quantile(0.66)
            
            features['propensity_tier'] = np.where(
                score_col >= q66, 'High',
                np.where(score_col >= q33, 'Medium', 'Low')
            )
        else:
            features['propensity_tier'] = 'Medium'
        
        return features
    
    def build_feature_set(self) -> pd.DataFrame:
        """Build complete feature set for opportunity scoring"""
        logger.info("Building customer master list")
        customers = self.create_customer_master()
        
        # Only process 5-digit customer IDs for now (Install Base + Opportunities)
        customers_5digit = customers[customers['id_type'] == '5-digit'].copy()
        
        if not customers_5digit.empty:
            logger.info("Creating install base features")
            customers_5digit = self.create_install_base_features(customers_5digit)
            
            logger.info("Creating opportunity features")
            customers_5digit = self.create_opportunity_features(customers_5digit)
            
            logger.info("Creating service credit features")
            customers_5digit = self.create_service_credit_features(customers_5digit)
            
            logger.info("Creating RFM features")
            customers_5digit = self.create_rfm_features(customers_5digit)
            
            logger.info("Creating urgency features")
            customers_5digit = self.create_urgency_features(customers_5digit)
            
            logger.info("Creating propensity scores")
            customers_5digit = self.create_opportunity_propensity_score(customers_5digit)
        
        # Process 9-digit customers separately (A&PS Projects)
        customers_9digit = customers[customers['id_type'] == '9-digit'].copy()
        if not customers_9digit.empty:
            logger.info("Processing A&PS project customers")
            customers_9digit = self.create_project_features(customers_9digit)
            customers_9digit = self.create_service_credit_features(customers_9digit)
            
            # Simple scoring for 9-digit customers
            customers_9digit['opportunity_propensity_score'] = 0.5  # Default medium score
            customers_9digit['propensity_tier'] = 'Medium'
        
        # Combine both customer types
        if not customers_5digit.empty and not customers_9digit.empty:
            all_customers = pd.concat([customers_5digit, customers_9digit], ignore_index=True)
        elif not customers_5digit.empty:
            all_customers = customers_5digit
        elif not customers_9digit.empty:
            all_customers = customers_9digit
        else:
            all_customers = pd.DataFrame()
        
        # Fill missing values
        if not all_customers.empty:
            all_customers = all_customers.fillna(0)
        
        self.features = all_customers
        return all_customers
    
    def get_top_opportunities(self, n: int = 50) -> pd.DataFrame:
        """Get top N opportunities ranked by propensity score"""
        if self.features.empty:
            self.build_feature_set()
        
        if not self.features.empty and 'opportunity_propensity_score' in self.features.columns:
            return self.features.nlargest(n, 'opportunity_propensity_score')
        else:
            return pd.DataFrame()
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Calculate feature importance for opportunity scoring"""
        if self.features.empty:
            return {}
        
        # Simple correlation with propensity score
        numeric_features = self.features.select_dtypes(include=[np.number]).columns
        numeric_features = [col for col in numeric_features 
                          if col not in ['opportunity_propensity_score', 'customer_id']]
        
        importance = {}
        for feature in numeric_features:
            if 'opportunity_propensity_score' in self.features.columns:
                correlation = self.features[feature].corr(self.features['opportunity_propensity_score'])
                importance[feature] = abs(correlation) if not pd.isna(correlation) else 0
        
        # Sort by importance
        return dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))