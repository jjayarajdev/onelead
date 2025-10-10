#!/usr/bin/env python3
"""
HPE OneLead Dataset - Comprehensive Exploratory Data Analysis (EDA)
Generates detailed insights and visualizations from the consolidated dataset
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from data_processing.data_loader import OneleadDataLoader
from data_processing.feature_engineering import OneleadFeatureEngineer

warnings.filterwarnings('ignore')

# Configure matplotlib
plt.style.use('seaborn-v0_8')
plt.rcParams['figure.figsize'] = (12, 8)
sns.set_palette("husl")

class OneleadEDA:
    """Comprehensive EDA for HPE OneLead dataset"""
    
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.loader = OneleadDataLoader(data_path)
        self.raw_data = {}
        self.processed_data = {}
        self.features = pd.DataFrame()
        
    def load_data(self):
        """Load and process all data"""
        print("🔄 Loading HPE OneLead Dataset...")
        self.processed_data = self.loader.process_all_data()
        
        # Generate features
        feature_engineer = OneleadFeatureEngineer(self.processed_data)
        self.features = feature_engineer.build_feature_set()
        
        print(f"✅ Data loaded successfully!")
        print(f"   • Total data sheets: {len(self.processed_data)}")
        print(f"   • Total customers: {len(self.features)}")
        print(f"   • Total features: {len(self.features.columns)}")
        
    def data_overview(self):
        """Comprehensive data overview"""
        print("\n" + "="*80)
        print("📊 DATA OVERVIEW")
        print("="*80)
        
        total_records = sum(len(df) for df in self.processed_data.values())
        total_columns = sum(len(df.columns) for df in self.processed_data.values())
        
        print(f"📈 DATASET SUMMARY")
        print(f"   • Total Records: {total_records:,}")
        print(f"   • Total Columns: {total_columns}")
        print(f"   • Data Sources: {len(self.processed_data)}")
        print(f"   • Unique Customers: {len(self.features)}")
        
        print(f"\n📋 DATA SOURCES BREAKDOWN:")
        for name, df in self.processed_data.items():
            missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
            
            print(f"   {name}:")
            print(f"      Records: {len(df):,}")
            print(f"      Columns: {len(df.columns)}")
            print(f"      Missing Data: {missing_pct:.1f}%")
            print(f"      Memory Usage: {memory_mb:.1f} MB")
            print()
            
    def missing_data_analysis(self):
        """Analyze missing data patterns"""
        print("\n" + "="*80)
        print("🔍 MISSING DATA ANALYSIS")
        print("="*80)
        
        for sheet_name, df in self.processed_data.items():
            print(f"\n📊 {sheet_name.upper()}:")
            
            missing_data = df.isnull().sum()
            missing_pct = (missing_data / len(df)) * 100
            
            missing_summary = pd.DataFrame({
                'Column': missing_data.index,
                'Missing Count': missing_data.values,
                'Missing %': missing_pct.values
            }).sort_values('Missing %', ascending=False)
            
            # Show only columns with missing data
            missing_cols = missing_summary[missing_summary['Missing Count'] > 0]
            
            if len(missing_cols) > 0:
                print(missing_cols.to_string(index=False))
            else:
                print("   ✅ No missing data found!")
                
    def customer_distribution_analysis(self):
        """Analyze customer distribution and characteristics"""
        print("\n" + "="*80)
        print("👥 CUSTOMER DISTRIBUTION ANALYSIS")
        print("="*80)
        
        # Customer counts by data source
        print("📊 CUSTOMER PRESENCE ACROSS DATA SOURCES:")
        
        customer_presence = {}
        for name, df in self.processed_data.items():
            if 'account_sales_territory_id' in df.columns:
                unique_customers = df['account_sales_territory_id'].nunique()
                customer_presence[name] = unique_customers
                print(f"   {name}: {unique_customers} customers")
        
        # Propensity distribution
        if 'propensity_tier' in self.features.columns:
            print(f"\n🎯 CUSTOMER PROPENSITY DISTRIBUTION:")
            propensity_counts = self.features['propensity_tier'].value_counts()
            for tier, count in propensity_counts.items():
                pct = (count / len(self.features)) * 100
                print(f"   {tier}: {count} customers ({pct:.1f}%)")
        
        # Feature statistics
        print(f"\n📈 KEY CUSTOMER METRICS:")
        numeric_features = self.features.select_dtypes(include=[np.number])
        
        key_metrics = [
            'urgency_score', 'rfm_score', 'opportunity_propensity_score',
            'total_products', 'total_opportunities', 'eol_urgency_score'
        ]
        
        for metric in key_metrics:
            if metric in numeric_features.columns:
                series = numeric_features[metric]
                print(f"   {metric}:")
                print(f"      Mean: {series.mean():.2f}")
                print(f"      Median: {series.median():.2f}")
                print(f"      Std: {series.std():.2f}")
                print(f"      Min: {series.min():.2f}")
                print(f"      Max: {series.max():.2f}")
                print(f"      Non-zero count: {(series != 0).sum()}")
                print()
                
    def product_lifecycle_analysis(self):
        """Analyze product lifecycle and EOL patterns"""
        print("\n" + "="*80)
        print("🔄 PRODUCT LIFECYCLE ANALYSIS")
        print("="*80)
        
        if 'Raw_install_base' in self.processed_data:
            install_base = self.processed_data['Raw_install_base']
            
            print("📊 INSTALL BASE OVERVIEW:")
            print(f"   Total Products: {len(install_base):,}")
            print(f"   Unique Customers: {install_base['account_sales_territory_id'].nunique()}")
            
            # Product platform analysis
            if 'product_platform_description_name' in install_base.columns:
                platform_counts = install_base['product_platform_description_name'].value_counts().head(10)
                print(f"\n🏗️ TOP 10 PRODUCT PLATFORMS:")
                for platform, count in platform_counts.items():
                    print(f"   {platform}: {count} products")
            
            # Support status analysis
            if 'support_status' in install_base.columns:
                support_counts = install_base['support_status'].value_counts()
                print(f"\n🛠️ SUPPORT STATUS DISTRIBUTION:")
                for status, count in support_counts.items():
                    pct = (count / len(install_base)) * 100
                    print(f"   {status}: {count} products ({pct:.1f}%)")
            
            # EOL urgency analysis
            if 'eol_urgency_score' in install_base.columns:
                eol_counts = install_base['eol_urgency_score'].value_counts().sort_index()
                print(f"\n⚠️ END-OF-LIFE URGENCY:")
                urgency_labels = {0: 'No Risk', 1: 'Low Risk', 2: 'Medium Risk', 3: 'High Risk'}
                for score, count in eol_counts.items():
                    label = urgency_labels.get(score, f'Score {score}')
                    pct = (count / len(install_base)) * 100
                    print(f"   {label}: {count} products ({pct:.1f}%)")
    
    def opportunity_analysis(self):
        """Analyze opportunities and sales pipeline"""
        print("\n" + "="*80)
        print("💼 OPPORTUNITY ANALYSIS")
        print("="*80)
        
        if 'Raw_opportunities' in self.processed_data:
            opportunities = self.processed_data['Raw_opportunities']
            
            print("📊 OPPORTUNITIES OVERVIEW:")
            print(f"   Total Opportunities: {len(opportunities):,}")
            print(f"   Unique Customers: {opportunities['account_sales_territory_id'].nunique()}")
            
            # Product line analysis
            if 'product_line__c' in opportunities.columns:
                product_line_counts = opportunities['product_line__c'].value_counts()
                print(f"\n📈 OPPORTUNITIES BY PRODUCT LINE:")
                for line, count in product_line_counts.items():
                    pct = (count / len(opportunities)) * 100
                    print(f"   {line}: {count} opportunities ({pct:.1f}%)")
            
            # Opportunity owner analysis
            if 'opportunity_owner__r_name' in opportunities.columns:
                owner_counts = opportunities['opportunity_owner__r_name'].value_counts().head(10)
                print(f"\n👤 TOP 10 OPPORTUNITY OWNERS:")
                for owner, count in owner_counts.items():
                    print(f"   {owner}: {count} opportunities")
            
            # Description analysis
            if 'opportunity_description' in opportunities.columns:
                has_desc = opportunities['opportunity_description'].notna().sum()
                desc_pct = (has_desc / len(opportunities)) * 100
                print(f"\n📝 OPPORTUNITY DESCRIPTIONS:")
                print(f"   With Description: {has_desc} ({desc_pct:.1f}%)")
                print(f"   Without Description: {len(opportunities) - has_desc} ({100-desc_pct:.1f}%)")
                
                if has_desc > 0:
                    avg_length = opportunities['opportunity_description'].str.len().mean()
                    print(f"   Average Description Length: {avg_length:.0f} characters")
    
    def service_credit_analysis(self):
        """Analyze service credit utilization patterns"""
        print("\n" + "="*80)
        print("🎫 SERVICE CREDIT ANALYSIS")
        print("="*80)
        
        if 'Raw_service_credits' in self.processed_data:
            credits = self.processed_data['Raw_service_credits']
            
            print("📊 SERVICE CREDITS OVERVIEW:")
            print(f"   Total Credit Records: {len(credits):,}")
            
            # Credit metrics
            if 'purchasedcredits' in credits.columns:
                total_purchased = credits['purchasedcredits'].sum()
                print(f"   Total Purchased Credits: {total_purchased:,.0f}")
            
            if 'activecredits' in credits.columns:
                total_active = credits['activecredits'].sum()
                print(f"   Total Active Credits: {total_active:,.0f}")
                
                if 'purchasedcredits' in credits.columns:
                    utilization_rate = ((total_purchased - total_active) / total_purchased) * 100
                    print(f"   Overall Utilization Rate: {utilization_rate:.1f}%")
            
            if 'deliveredcredits' in credits.columns:
                total_delivered = credits['deliveredcredits'].sum()
                print(f"   Total Delivered Credits: {total_delivered:,.0f}")
            
            # Practice analysis
            if 'practicename' in credits.columns:
                practice_counts = credits['practicename'].value_counts()
                print(f"\n🏢 CREDITS BY PRACTICE:")
                for practice, count in practice_counts.items():
                    pct = (count / len(credits)) * 100
                    print(f"   {practice}: {count} records ({pct:.1f}%)")
            
            # Contract expiry analysis
            if 'expiryindays' in credits.columns:
                print(f"\n⏰ CONTRACT EXPIRY ANALYSIS:")
                # Try to convert to numeric, handle errors
                try:
                    numeric_expiry = pd.to_numeric(credits['expiryindays'], errors='coerce')
                    if not numeric_expiry.isna().all():
                        expiry_mean = numeric_expiry.mean()
                        expiry_median = numeric_expiry.median()
                        print(f"   Average Days to Expiry: {expiry_mean:.0f}")
                        print(f"   Median Days to Expiry: {expiry_median:.0f}")
                        
                        # Urgency buckets
                        urgent = (numeric_expiry <= 30).sum()
                        medium = ((numeric_expiry > 30) & (numeric_expiry <= 90)).sum()
                        low = (numeric_expiry > 90).sum()
                        
                        print(f"   Urgent (≤30 days): {urgent} contracts")
                        print(f"   Medium (31-90 days): {medium} contracts") 
                        print(f"   Low Risk (>90 days): {low} contracts")
                    else:
                        print("   ⚠️  Expiry data contains non-numeric values")
                        print(f"   Data type: {credits['expiryindays'].dtype}")
                        print(f"   Sample values: {credits['expiryindays'].head(3).tolist()}")
                except Exception as e:
                    print(f"   ⚠️  Unable to analyze expiry data: {str(e)[:100]}...")
                    print(f"   Data type: {credits['expiryindays'].dtype}")
                    unique_vals = credits['expiryindays'].nunique()
                    print(f"   Unique values: {unique_vals}")
    
    def project_performance_analysis(self):
        """Analyze historical project performance"""
        print("\n" + "="*80)
        print("🚀 PROJECT PERFORMANCE ANALYSIS")
        print("="*80)
        
        if 'Raw_projects' in self.processed_data:
            projects = self.processed_data['Raw_projects']
            
            print("📊 PROJECTS OVERVIEW:")
            print(f"   Total Projects: {len(projects):,}")
            print(f"   Unique Customers: {projects['prj_customer_id'].nunique()}")
            
            # Project size analysis
            if 'prj_size' in projects.columns:
                print(f"\n📏 PROJECT SIZE ANALYSIS:")
                try:
                    numeric_size = pd.to_numeric(projects['prj_size'], errors='coerce')
                    if not numeric_size.isna().all():
                        print(f"   Average Size: {numeric_size.mean():.2f}")
                        print(f"   Median Size: {numeric_size.median():.2f}")
                        print(f"   Min Size: {numeric_size.min():.2f}")
                        print(f"   Max Size: {numeric_size.max():.2f}")
                    else:
                        print("   ⚠️  Project size data is non-numeric")
                except Exception as e:
                    print(f"   ⚠️  Unable to analyze project size: {str(e)[:50]}...")
            
            # Project length analysis
            if 'prj_length' in projects.columns:
                print(f"\n⏱️ PROJECT DURATION ANALYSIS:")
                try:
                    numeric_length = pd.to_numeric(projects['prj_length'], errors='coerce')
                    if not numeric_length.isna().all():
                        print(f"   Average Length: {numeric_length.mean():.1f} days")
                        print(f"   Median Length: {numeric_length.median():.1f} days")
                        print(f"   Min Length: {numeric_length.min():.1f} days")
                        print(f"   Max Length: {numeric_length.max():.1f} days")
                    else:
                        print("   ⚠️  Project length data is non-numeric")
                except Exception as e:
                    print(f"   ⚠️  Unable to analyze project length: {str(e)[:50]}...")
            
            # Practice analysis
            if 'prj_practice' in projects.columns:
                practice_counts = projects['prj_practice'].value_counts().head(10)
                print(f"\n🏢 TOP 10 PRACTICES BY PROJECT COUNT:")
                for practice, count in practice_counts.items():
                    pct = (count / len(projects)) * 100
                    print(f"   {practice}: {count} projects ({pct:.1f}%)")
            
            # Status analysis
            if 'prj_status_description' in projects.columns:
                status_counts = projects['prj_status_description'].value_counts()
                print(f"\n✅ PROJECT STATUS DISTRIBUTION:")
                for status, count in status_counts.items():
                    pct = (count / len(projects)) * 100
                    print(f"   {status}: {count} projects ({pct:.1f}%)")
            
            # Geographic analysis
            if 'country_id' in projects.columns:
                country_counts = projects['country_id'].value_counts().head(10)
                print(f"\n🌍 TOP 10 COUNTRIES BY PROJECT COUNT:")
                for country, count in country_counts.items():
                    pct = (count / len(projects)) * 100
                    print(f"   {country}: {count} projects ({pct:.1f}%)")
    
    def correlation_analysis(self):
        """Analyze correlations between key features"""
        print("\n" + "="*80)
        print("🔗 CORRELATION ANALYSIS")
        print("="*80)
        
        # Select numeric features for correlation
        numeric_features = self.features.select_dtypes(include=[np.number])
        
        # Focus on business-relevant features
        key_features = [
            'urgency_score', 'rfm_score', 'opportunity_propensity_score',
            'eol_urgency_score', 'eos_urgency_score', 'total_products',
            'total_opportunities', 'recency_score', 'frequency_score', 'monetary_score'
        ]
        
        available_features = [f for f in key_features if f in numeric_features.columns]
        
        if len(available_features) >= 2:
            correlation_matrix = numeric_features[available_features].corr()
            
            print("📊 CORRELATION MATRIX (Top Business Features):")
            print(correlation_matrix.round(3).to_string())
            
            # Find strongest correlations
            print(f"\n🔍 STRONGEST POSITIVE CORRELATIONS:")
            correlations = []
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    corr_value = correlation_matrix.iloc[i, j]
                    if not pd.isna(corr_value):
                        correlations.append({
                            'Feature 1': correlation_matrix.columns[i],
                            'Feature 2': correlation_matrix.columns[j],
                            'Correlation': corr_value
                        })
            
            # Sort by absolute correlation value
            correlations_df = pd.DataFrame(correlations)
            correlations_df['Abs_Correlation'] = abs(correlations_df['Correlation'])
            top_correlations = correlations_df.nlargest(10, 'Abs_Correlation')
            
            for _, row in top_correlations.iterrows():
                print(f"   {row['Feature 1']} ↔ {row['Feature 2']}: {row['Correlation']:.3f}")
    
    def business_insights(self):
        """Generate actionable business insights"""
        print("\n" + "="*80)
        print("💡 BUSINESS INSIGHTS & RECOMMENDATIONS")
        print("="*80)
        
        insights = []
        
        # Customer propensity insights
        if 'propensity_tier' in self.features.columns:
            high_prop = (self.features['propensity_tier'] == 'High').sum()
            high_pct = (high_prop / len(self.features)) * 100
            insights.append(f"🎯 {high_prop} customers ({high_pct:.1f}%) identified as HIGH propensity opportunities")
        
        # Urgency insights
        if 'urgency_score' in self.features.columns:
            urgent_customers = (self.features['urgency_score'] >= 3).sum()
            if urgent_customers > 0:
                insights.append(f"⚠️  {urgent_customers} customers require IMMEDIATE attention (urgency score ≥ 3)")
        
        # EOL insights
        if 'eol_urgency_score' in self.features.columns:
            eol_risk = (self.features['eol_urgency_score'] >= 2).sum()
            if eol_risk > 0:
                eol_pct = (eol_risk / len(self.features)) * 100
                insights.append(f"🔄 {eol_risk} customers ({eol_pct:.1f}%) have products approaching end-of-life")
        
        # Opportunity coverage
        if 'has_active_opportunities' in self.features.columns:
            has_opps = self.features['has_active_opportunities'].sum()
            coverage_pct = (has_opps / len(self.features)) * 100
            insights.append(f"📈 {has_opps} customers ({coverage_pct:.1f}%) currently have active opportunities")
        
        # Service utilization insights
        if 'low_utilization_risk' in self.features.columns:
            low_util = self.features['low_utilization_risk'].sum()
            if low_util > 0:
                util_pct = (low_util / len(self.features)) * 100
                insights.append(f"🎫 {low_util} customers ({util_pct:.1f}%) are under-utilizing service credits")
        
        # Platform diversity insights
        platform_cols = [col for col in self.features.columns if 'platform' in col.lower()]
        if platform_cols:
            platform_col = platform_cols[0]
            low_diversity = (self.features[platform_col] <= 2).sum()
            if low_diversity > 0:
                div_pct = (low_diversity / len(self.features)) * 100
                insights.append(f"🚀 {low_diversity} customers ({div_pct:.1f}%) have cross-sell potential (low platform diversity)")
        
        print("🔍 KEY INSIGHTS:")
        for i, insight in enumerate(insights, 1):
            print(f"   {i}. {insight}")
        
        # Recommendations
        print(f"\n📋 STRATEGIC RECOMMENDATIONS:")
        recommendations = [
            "Focus immediate consultant efforts on high-urgency customers (urgency score ≥ 3)",
            "Develop proactive renewal campaigns for customers with products approaching EOL",
            "Create service expansion programs for customers with low credit utilization",
            "Target cross-sell initiatives to customers with limited platform diversity",
            "Implement automated alerts for contract renewal deadlines",
            "Establish regular review cycles for high-propensity customers",
            "Develop industry-specific conversation starters based on customer patterns"
        ]
        
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
    
    def generate_summary_report(self):
        """Generate executive summary report"""
        print("\n" + "="*80)
        print("📋 EXECUTIVE SUMMARY REPORT")
        print("="*80)
        
        # Data volume summary
        total_records = sum(len(df) for df in self.processed_data.values())
        
        print("📊 DATA VOLUME:")
        print(f"   • Total Records Processed: {total_records:,}")
        print(f"   • Unique Customers Identified: {len(self.features)}")
        print(f"   • Data Sources Integrated: {len(self.processed_data)}")
        print(f"   • Features Generated: {len(self.features.columns)}")
        
        # Business opportunity summary
        if 'propensity_tier' in self.features.columns:
            prop_counts = self.features['propensity_tier'].value_counts()
            print(f"\n🎯 OPPORTUNITY DISTRIBUTION:")
            for tier in ['High', 'Medium', 'Low']:
                count = prop_counts.get(tier, 0)
                pct = (count / len(self.features)) * 100 if len(self.features) > 0 else 0
                print(f"   • {tier} Priority: {count} customers ({pct:.1f}%)")
        
        # Urgency summary
        urgent_metrics = {}
        if 'urgency_score' in self.features.columns:
            urgent_metrics['High Urgency'] = (self.features['urgency_score'] >= 3).sum()
        if 'eol_urgency_score' in self.features.columns:
            urgent_metrics['EOL Risk'] = (self.features['eol_urgency_score'] >= 2).sum()
        if 'low_utilization_risk' in self.features.columns:
            urgent_metrics['Service Expansion'] = self.features['low_utilization_risk'].sum()
        
        if urgent_metrics:
            print(f"\n⚠️  IMMEDIATE ACTION REQUIRED:")
            for metric, count in urgent_metrics.items():
                print(f"   • {metric}: {count} customers")
        
        # Data quality summary
        print(f"\n✅ DATA QUALITY STATUS:")
        for name, df in self.processed_data.items():
            missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            quality_status = "Excellent" if missing_pct < 5 else "Good" if missing_pct < 15 else "Needs Attention"
            print(f"   • {name}: {quality_status} ({missing_pct:.1f}% missing)")
        
        print(f"\n🚀 NEXT STEPS:")
        print("   1. Launch interactive dashboard for consultant access")
        print("   2. Implement automated alerts for high-urgency customers")
        print("   3. Begin proactive outreach to top-priority opportunities")
        print("   4. Set up regular data refresh cycles")
        print("   5. Track consultant engagement and outcome metrics")
    
    def run_complete_eda(self):
        """Run complete EDA analysis"""
        print("🚀 STARTING HPE ONELEAD COMPREHENSIVE EDA")
        print("="*80)
        
        # Load data
        self.load_data()
        
        # Run all analyses
        self.data_overview()
        self.missing_data_analysis()
        self.customer_distribution_analysis()
        self.product_lifecycle_analysis()
        self.opportunity_analysis()
        self.service_credit_analysis()
        self.project_performance_analysis()
        self.correlation_analysis()
        self.business_insights()
        self.generate_summary_report()
        
        print("\n" + "="*80)
        print("✅ EDA ANALYSIS COMPLETE!")
        print("="*80)
        print("\n📁 For interactive visualizations, run:")
        print("   streamlit run src/main.py")
        print("\n📊 For detailed technical documentation, see:")
        print("   SOLUTION.md")

def main():
    """Main execution function"""
    data_path = "data/onelead_consolidated_data_new.xlsx"
    
    # Create EDA instance and run analysis
    eda = OneleadEDA(data_path)
    eda.run_complete_eda()

if __name__ == "__main__":
    main()