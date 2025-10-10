#!/usr/bin/env python3
"""
HPE OneLead Dataset - Generate Comprehensive Visualizations
Creates charts and graphs to supplement the EDA analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from data_processing.data_loader import OneleadDataLoader
from data_processing.feature_engineering import OneleadFeatureEngineer

warnings.filterwarnings('ignore')

# Configure plotting
plt.style.use('seaborn-v0_8')
plt.rcParams['figure.figsize'] = (12, 8)
sns.set_palette("husl")

def create_data_overview_charts(processed_data, output_dir="visualizations"):
    """Create data overview visualizations"""
    Path(output_dir).mkdir(exist_ok=True)
    
    # 1. Data volume by source
    data_volumes = {name: len(df) for name, df in processed_data.items()}
    
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(data_volumes.keys(), data_volumes.values(), color='skyblue', alpha=0.8)
    ax.set_title('HPE OneLead Dataset - Records by Data Source', fontsize=16, fontweight='bold')
    ax.set_ylabel('Number of Records', fontsize=12)
    ax.set_xlabel('Data Source', fontsize=12)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 50,
                f'{int(height):,}', ha='center', va='bottom', fontweight='bold')
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/data_volumes_by_source.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Missing data heatmap
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()
    
    for i, (name, df) in enumerate(processed_data.items()):
        if i >= len(axes):
            break
            
        missing_data = df.isnull().sum()
        missing_pct = (missing_data / len(df)) * 100
        
        # Only show columns with missing data
        missing_cols = missing_pct[missing_pct > 0].head(10)
        
        if len(missing_cols) > 0:
            ax = axes[i]
            bars = ax.barh(range(len(missing_cols)), missing_cols.values, color='coral', alpha=0.7)
            ax.set_yticks(range(len(missing_cols)))
            ax.set_yticklabels([col[:20] + '...' if len(col) > 20 else col for col in missing_cols.index])
            ax.set_xlabel('Missing Data %')
            ax.set_title(f'{name}\nMissing Data by Column', fontweight='bold')
            
            # Add percentage labels
            for j, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                        f'{width:.1f}%', ha='left', va='center', fontsize=8)
        else:
            axes[i].text(0.5, 0.5, f'{name}\n✅ No Missing Data', 
                        ha='center', va='center', transform=axes[i].transAxes,
                        fontsize=12, fontweight='bold')
            axes[i].set_xlim(0, 1)
            axes[i].set_ylim(0, 1)
    
    # Hide unused subplots
    for i in range(len(processed_data), len(axes)):
        axes[i].set_visible(False)
    
    plt.suptitle('HPE OneLead Dataset - Missing Data Analysis', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/missing_data_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_customer_analysis_charts(features, processed_data, output_dir="visualizations"):
    """Create customer-focused visualizations"""
    
    # 1. Customer propensity distribution
    if 'propensity_tier' in features.columns:
        propensity_counts = features['propensity_tier'].value_counts()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Pie chart
        colors = ['#ff6b6b', '#ffd93d', '#6bcf7f']
        wedges, texts, autotexts = ax1.pie(propensity_counts.values, labels=propensity_counts.index,
                                          autopct='%1.1f%%', colors=colors, startangle=90,
                                          textprops={'fontsize': 12, 'fontweight': 'bold'})
        ax1.set_title('Customer Propensity Distribution', fontsize=14, fontweight='bold')
        
        # Bar chart
        bars = ax2.bar(propensity_counts.index, propensity_counts.values, color=colors, alpha=0.8)
        ax2.set_title('Customer Count by Propensity Level', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Number of Customers')
        ax2.set_xlabel('Propensity Level')
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/customer_propensity_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    # 2. Key metrics distribution
    key_metrics = ['urgency_score', 'opportunity_propensity_score', 'total_products', 'total_opportunities']
    available_metrics = [metric for metric in key_metrics if metric in features.columns]
    
    if available_metrics:
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        axes = axes.flatten()
        
        for i, metric in enumerate(available_metrics[:4]):
            ax = axes[i]
            data = features[metric]
            
            # Histogram
            ax.hist(data, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            ax.set_title(f'Distribution of {metric.replace("_", " ").title()}', fontweight='bold')
            ax.set_xlabel(metric.replace("_", " ").title())
            ax.set_ylabel('Frequency')
            
            # Add statistics text
            stats_text = f'Mean: {data.mean():.2f}\nMedian: {data.median():.2f}\nStd: {data.std():.2f}'
            ax.text(0.7, 0.8, stats_text, transform=ax.transAxes, 
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
                   verticalalignment='top', fontsize=10)
        
        # Hide unused subplots
        for i in range(len(available_metrics), 4):
            axes[i].set_visible(False)
        
        plt.suptitle('HPE OneLead - Key Customer Metrics Distribution', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(f'{output_dir}/key_metrics_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()

def create_business_analysis_charts(processed_data, output_dir="visualizations"):
    """Create business-focused visualizations"""
    
    # 1. Product platform analysis
    if 'Raw_install_base' in processed_data:
        install_base = processed_data['Raw_install_base']
        
        if 'product_platform_description_name' in install_base.columns:
            platform_counts = install_base['product_platform_description_name'].value_counts().head(10)
            
            fig, ax = plt.subplots(figsize=(14, 8))
            bars = ax.barh(range(len(platform_counts)), platform_counts.values, color='lightcoral', alpha=0.8)
            ax.set_yticks(range(len(platform_counts)))
            ax.set_yticklabels([platform[:30] + '...' if len(platform) > 30 else platform 
                               for platform in platform_counts.index])
            ax.set_xlabel('Number of Products')
            ax.set_title('Top 10 Product Platforms by Volume', fontsize=16, fontweight='bold')
            
            # Add value labels
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(width + 50, bar.get_y() + bar.get_height()/2,
                        f'{int(width):,}', ha='left', va='center', fontweight='bold')
            
            plt.tight_layout()
            plt.savefig(f'{output_dir}/product_platforms_analysis.png', dpi=300, bbox_inches='tight')
            plt.close()
    
    # 2. Opportunity analysis
    if 'Raw_opportunities' in processed_data:
        opportunities = processed_data['Raw_opportunities']
        
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Product line analysis
        if 'product_line__c' in opportunities.columns:
            product_line_counts = opportunities['product_line__c'].value_counts()
            
            # Pie chart for product lines
            ax1 = axes[0]
            wedges, texts, autotexts = ax1.pie(product_line_counts.values, 
                                              labels=[line[:20] + '...' if len(line) > 20 else line 
                                                     for line in product_line_counts.index],
                                              autopct='%1.1f%%', startangle=90)
            ax1.set_title('Opportunities by Product Line', fontsize=14, fontweight='bold')
        
        # Opportunity owners
        if 'opportunity_owner__r_name' in opportunities.columns:
            owner_counts = opportunities['opportunity_owner__r_name'].value_counts().head(8)
            
            ax2 = axes[1]
            bars = ax2.bar(range(len(owner_counts)), owner_counts.values, color='lightgreen', alpha=0.8)
            ax2.set_xticks(range(len(owner_counts)))
            ax2.set_xticklabels([name.split()[0] for name in owner_counts.index], rotation=45)
            ax2.set_ylabel('Number of Opportunities')
            ax2.set_title('Top 8 Opportunity Owners', fontsize=14, fontweight='bold')
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                        f'{int(height)}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/opportunity_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    # 3. Service credits analysis
    if 'Raw_service_credits' in processed_data:
        credits = processed_data['Raw_service_credits']
        
        if 'practicename' in credits.columns:
            practice_counts = credits['practicename'].value_counts()
            
            fig, ax = plt.subplots(figsize=(12, 8))
            bars = ax.barh(range(len(practice_counts)), practice_counts.values, color='gold', alpha=0.8)
            ax.set_yticks(range(len(practice_counts)))
            ax.set_yticklabels([practice[:25] + '...' if len(practice) > 25 else practice 
                               for practice in practice_counts.index])
            ax.set_xlabel('Number of Credit Records')
            ax.set_title('Service Credits by Practice Area', fontsize=16, fontweight='bold')
            
            # Add value labels and percentages
            total_records = len(credits)
            for i, bar in enumerate(bars):
                width = bar.get_width()
                pct = (width / total_records) * 100
                ax.text(width + 5, bar.get_y() + bar.get_height()/2,
                        f'{int(width)} ({pct:.1f}%)', ha='left', va='center', fontweight='bold')
            
            plt.tight_layout()
            plt.savefig(f'{output_dir}/service_credits_analysis.png', dpi=300, bbox_inches='tight')
            plt.close()

def create_correlation_heatmap(features, output_dir="visualizations"):
    """Create correlation heatmap for key features"""
    
    # Select numeric features
    numeric_features = features.select_dtypes(include=[np.number])
    
    # Focus on business-relevant features
    key_features = [
        'urgency_score', 'opportunity_propensity_score', 'eol_urgency_score',
        'total_products', 'total_opportunities', 'rfm_score'
    ]
    
    available_features = [f for f in key_features if f in numeric_features.columns]
    
    if len(available_features) >= 3:
        correlation_matrix = numeric_features[available_features].corr()
        
        plt.figure(figsize=(10, 8))
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
        
        # Create heatmap
        sns.heatmap(correlation_matrix, annot=True, cmap='RdYlBu_r', center=0,
                   square=True, mask=mask, cbar_kws={"shrink": .8},
                   fmt='.3f', linewidths=0.5)
        
        plt.title('HPE OneLead - Feature Correlation Matrix', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Features', fontsize=12)
        plt.ylabel('Features', fontsize=12)
        
        # Rotate labels for better readability
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/correlation_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()

def create_interactive_dashboard_preview(features, processed_data, output_dir="visualizations"):
    """Create interactive plotly visualizations"""
    
    # 1. Customer propensity scatter plot
    if all(col in features.columns for col in ['urgency_score', 'opportunity_propensity_score', 'propensity_tier']):
        fig = px.scatter(features, 
                        x='urgency_score', 
                        y='opportunity_propensity_score',
                        color='propensity_tier',
                        size='total_products' if 'total_products' in features.columns else None,
                        hover_data=['customer_id'],
                        title='Customer Opportunity Analysis - Urgency vs Propensity',
                        color_discrete_map={'High': '#ff4444', 'Medium': '#ffaa00', 'Low': '#44ff44'})
        
        fig.update_layout(
            title_font_size=16,
            xaxis_title="Urgency Score",
            yaxis_title="Opportunity Propensity Score",
            width=800,
            height=600
        )
        
        fig.write_html(f'{output_dir}/interactive_customer_analysis.html')
    
    # 2. Data volume treemap
    data_volumes = {name.replace('Raw_', ''): len(df) for name, df in processed_data.items()}
    
    fig = go.Figure(go.Treemap(
        labels=list(data_volumes.keys()),
        values=list(data_volumes.values()),
        parents=[""] * len(data_volumes),
        textinfo="label+value+percent parent",
        textfont_size=12,
        marker_colorscale='Viridis'
    ))
    
    fig.update_layout(
        title="HPE OneLead Dataset - Data Volume Distribution",
        title_font_size=16,
        width=800,
        height=600
    )
    
    fig.write_html(f'{output_dir}/data_volume_treemap.html')

def generate_summary_report(features, processed_data, output_dir="visualizations"):
    """Generate a comprehensive summary report"""
    
    report_path = f'{output_dir}/EDA_SUMMARY_REPORT.md'
    
    with open(report_path, 'w') as f:
        f.write("# HPE OneLead Dataset - EDA Summary Report\n\n")
        f.write(f"**Generated on:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Dataset overview
        f.write("## 📊 Dataset Overview\n\n")
        total_records = sum(len(df) for df in processed_data.values())
        f.write(f"- **Total Records:** {total_records:,}\n")
        f.write(f"- **Data Sources:** {len(processed_data)}\n")
        f.write(f"- **Unique Customers:** {len(features)}\n")
        f.write(f"- **Generated Features:** {len(features.columns)}\n\n")
        
        # Data sources breakdown
        f.write("## 📋 Data Sources\n\n")
        f.write("| Source | Records | Columns | Data Quality |\n")
        f.write("|--------|---------|---------|-------------|\n")
        
        for name, df in processed_data.items():
            missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            quality = "Excellent" if missing_pct < 5 else "Good" if missing_pct < 15 else "Needs Attention"
            f.write(f"| {name} | {len(df):,} | {len(df.columns)} | {quality} ({missing_pct:.1f}% missing) |\n")
        
        # Customer insights
        f.write("\n## 🎯 Customer Insights\n\n")
        
        if 'propensity_tier' in features.columns:
            propensity_counts = features['propensity_tier'].value_counts()
            f.write("### Propensity Distribution\n")
            for tier, count in propensity_counts.items():
                pct = (count / len(features)) * 100
                f.write(f"- **{tier} Priority:** {count} customers ({pct:.1f}%)\n")
        
        # Key metrics
        f.write("\n### Key Metrics Summary\n")
        key_metrics = ['urgency_score', 'opportunity_propensity_score', 'total_products', 'total_opportunities']
        
        for metric in key_metrics:
            if metric in features.columns:
                series = features[metric]
                f.write(f"\n**{metric.replace('_', ' ').title()}:**\n")
                f.write(f"- Mean: {series.mean():.2f}\n")
                f.write(f"- Median: {series.median():.2f}\n")
                f.write(f"- Range: {series.min():.2f} - {series.max():.2f}\n")
                f.write(f"- Non-zero count: {(series != 0).sum()}\n")
        
        # Business recommendations
        f.write("\n## 💡 Business Recommendations\n\n")
        f.write("### Immediate Actions\n")
        f.write("1. **Focus on High-Priority Customers:** Target immediate efforts on high-propensity opportunities\n")
        f.write("2. **Proactive Renewal Management:** Implement early warning system for product EOL\n")
        f.write("3. **Service Expansion:** Address service credit underutilization\n")
        f.write("4. **Cross-sell Initiatives:** Leverage platform diversity insights\n\n")
        
        f.write("### Strategic Initiatives\n")
        f.write("1. **Data Quality Improvement:** Address missing data in key sources\n")
        f.write("2. **Predictive Model Enhancement:** Incorporate additional data sources\n")
        f.write("3. **Automated Alerts:** Implement real-time opportunity identification\n")
        f.write("4. **Performance Tracking:** Monitor consultant engagement and outcomes\n\n")
        
        # Generated visualizations
        f.write("## 📈 Generated Visualizations\n\n")
        visualizations = [
            "data_volumes_by_source.png - Data volume comparison across sources",
            "missing_data_analysis.png - Missing data patterns by source",
            "customer_propensity_distribution.png - Customer opportunity distribution",
            "key_metrics_distribution.png - Statistical distribution of key metrics",
            "product_platforms_analysis.png - Product platform volume analysis",
            "opportunity_analysis.png - Sales opportunity breakdown",
            "service_credits_analysis.png - Service utilization patterns",
            "correlation_heatmap.png - Feature correlation analysis",
            "interactive_customer_analysis.html - Interactive customer scatter plot",
            "data_volume_treemap.html - Interactive data volume visualization"
        ]
        
        for viz in visualizations:
            f.write(f"- **{viz}**\n")
        
        f.write(f"\n---\n*Report generated by HPE OneLead EDA System*\n")

def main():
    """Main execution function"""
    print("🎨 GENERATING HPE ONELEAD VISUALIZATIONS")
    print("="*60)
    
    # Load data
    data_path = "data/onelead_consolidated_data_new.xlsx"
    loader = OneleadDataLoader(data_path)
    processed_data = loader.process_all_data()
    
    # Generate features
    feature_engineer = OneleadFeatureEngineer(processed_data)
    features = feature_engineer.build_feature_set()
    
    # Create output directory
    output_dir = "visualizations"
    Path(output_dir).mkdir(exist_ok=True)
    
    print(f"📊 Creating data overview charts...")
    create_data_overview_charts(processed_data, output_dir)
    
    print(f"👥 Creating customer analysis charts...")
    create_customer_analysis_charts(features, processed_data, output_dir)
    
    print(f"💼 Creating business analysis charts...")
    create_business_analysis_charts(processed_data, output_dir)
    
    print(f"🔗 Creating correlation heatmap...")
    create_correlation_heatmap(features, output_dir)
    
    print(f"📱 Creating interactive visualizations...")
    create_interactive_dashboard_preview(features, processed_data, output_dir)
    
    print(f"📋 Generating summary report...")
    generate_summary_report(features, processed_data, output_dir)
    
    print(f"\n✅ ALL VISUALIZATIONS GENERATED!")
    print(f"📁 Output directory: {output_dir}/")
    print(f"📊 Static images: 8 PNG files")
    print(f"🌐 Interactive charts: 2 HTML files") 
    print(f"📄 Summary report: EDA_SUMMARY_REPORT.md")

if __name__ == "__main__":
    main()