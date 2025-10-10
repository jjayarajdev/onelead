#!/usr/bin/env python3
"""
HPE OneLead Data Analysis Script
Analyzes the consolidated Excel data to understand structure and identify key fields
for building a predictive model to identify high-propensity OneLead opportunities.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import warnings
warnings.filterwarnings('ignore')

def analyze_excel_file(filepath):
    """
    Comprehensive analysis of the HPE OneLead Excel file
    """
    print("="*80)
    print("HPE ONELEAD DATA ANALYSIS REPORT")
    print("="*80)
    print(f"Analyzing file: {filepath}")
    print()
    
    try:
        # Load the Excel file and get all sheet names
        excel_file = pd.ExcelFile(filepath)
        sheet_names = excel_file.sheet_names
        
        print(f"📊 SHEET OVERVIEW")
        print(f"Total sheets found: {len(sheet_names)}")
        for i, sheet in enumerate(sheet_names, 1):
            print(f"  {i}. {sheet}")
        print()
        
        # Dictionary to store analysis results
        analysis_results = {}
        
        # Analyze each sheet
        for sheet_name in sheet_names:
            print("="*60)
            print(f"ANALYZING SHEET: {sheet_name}")
            print("="*60)
            
            try:
                # Read the sheet
                df = pd.read_excel(filepath, sheet_name=sheet_name)
                
                # Basic info
                print(f"📈 BASIC STATISTICS:")
                print(f"  Rows: {len(df):,}")
                print(f"  Columns: {len(df.columns):,}")
                print(f"  Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
                print()
                
                # Column analysis
                print(f"📋 COLUMN STRUCTURE:")
                column_info = []
                for col in df.columns:
                    dtype = str(df[col].dtype)
                    null_count = df[col].isnull().sum()
                    null_pct = (null_count / len(df)) * 100
                    unique_vals = df[col].nunique()
                    
                    column_info.append({
                        'column': col,
                        'dtype': dtype,
                        'null_count': null_count,
                        'null_pct': null_pct,
                        'unique_values': unique_vals,
                        'sample_values': df[col].dropna().head(3).tolist() if len(df[col].dropna()) > 0 else []
                    })
                
                # Display column information
                for info in column_info:
                    print(f"  📌 {info['column']}")
                    print(f"     Type: {info['dtype']}")
                    print(f"     Nulls: {info['null_count']:,} ({info['null_pct']:.1f}%)")
                    print(f"     Unique: {info['unique_values']:,}")
                    if info['sample_values']:
                        sample_str = ', '.join([str(x)[:50] for x in info['sample_values']])
                        print(f"     Sample: {sample_str}")
                    print()
                
                # Identify potential key fields for opportunity scoring
                print(f"🎯 KEY FIELDS ANALYSIS:")
                key_fields = identify_key_fields(df, column_info)
                for category, fields in key_fields.items():
                    if fields:
                        print(f"  {category}:")
                        for field in fields:
                            print(f"    • {field}")
                print()
                
                # Data quality assessment
                print(f"🔍 DATA QUALITY ASSESSMENT:")
                assess_data_quality(df)
                print()
                
                # Pattern analysis for buying intent
                print(f"💡 BUYING INTENT PATTERNS:")
                analyze_buying_patterns(df, column_info)
                print()
                
                # Store results
                analysis_results[sheet_name] = {
                    'df': df,
                    'column_info': column_info,
                    'key_fields': key_fields,
                    'shape': df.shape
                }
                
            except Exception as e:
                print(f"❌ Error analyzing sheet '{sheet_name}': {str(e)}")
                print()
        
        # Generate final recommendations
        print("="*80)
        print("🚀 PREDICTIVE MODEL RECOMMENDATIONS")
        print("="*80)
        generate_model_recommendations(analysis_results)
        
    except Exception as e:
        print(f"❌ Error loading Excel file: {str(e)}")
        return None
    
    return analysis_results

def identify_key_fields(df, column_info):
    """
    Identify columns that could be useful for opportunity scoring
    """
    key_fields = {
        'Customer Information': [],
        'Engagement Metrics': [],
        'Purchase History': [],
        'Solution/Product Data': [],
        'Temporal Data': [],
        'Performance Metrics': [],
        'Contact Information': [],
        'Geographic Data': []
    }
    
    for info in column_info:
        col_name = info['column'].lower()
        
        # Customer information
        if any(keyword in col_name for keyword in ['customer', 'company', 'account', 'client', 'organization']):
            key_fields['Customer Information'].append(info['column'])
        
        # Engagement metrics
        elif any(keyword in col_name for keyword in ['engagement', 'interaction', 'activity', 'visit', 'click', 'view', 'download']):
            key_fields['Engagement Metrics'].append(info['column'])
        
        # Purchase history
        elif any(keyword in col_name for keyword in ['purchase', 'order', 'revenue', 'sales', 'transaction', 'deal', 'contract']):
            key_fields['Purchase History'].append(info['column'])
        
        # Solution/Product data
        elif any(keyword in col_name for keyword in ['product', 'solution', 'service', 'offering', 'category', 'segment']):
            key_fields['Solution/Product Data'].append(info['column'])
        
        # Temporal data
        elif any(keyword in col_name for keyword in ['date', 'time', 'created', 'updated', 'last', 'first']):
            key_fields['Temporal Data'].append(info['column'])
        
        # Performance metrics
        elif any(keyword in col_name for keyword in ['score', 'rating', 'value', 'amount', 'count', 'frequency', 'rate']):
            key_fields['Performance Metrics'].append(info['column'])
        
        # Contact information
        elif any(keyword in col_name for keyword in ['contact', 'email', 'phone', 'name', 'title', 'role']):
            key_fields['Contact Information'].append(info['column'])
        
        # Geographic data
        elif any(keyword in col_name for keyword in ['country', 'region', 'city', 'state', 'location', 'geography']):
            key_fields['Geographic Data'].append(info['column'])
    
    return key_fields

def assess_data_quality(df):
    """
    Assess data quality issues
    """
    total_cells = len(df) * len(df.columns)
    null_cells = df.isnull().sum().sum()
    null_percentage = (null_cells / total_cells) * 100
    
    print(f"  Overall completeness: {100 - null_percentage:.1f}%")
    print(f"  Missing values: {null_cells:,} out of {total_cells:,} cells")
    
    # Check for duplicate rows
    duplicates = df.duplicated().sum()
    print(f"  Duplicate rows: {duplicates:,}")
    
    # Check for columns with high cardinality (potential IDs)
    high_cardinality_cols = []
    for col in df.columns:
        if df[col].nunique() / len(df) > 0.9 and df[col].nunique() > 100:
            high_cardinality_cols.append(col)
    
    if high_cardinality_cols:
        print(f"  High cardinality columns (potential IDs): {', '.join(high_cardinality_cols)}")

def analyze_buying_patterns(df, column_info):
    """
    Look for patterns that might indicate buying intent
    """
    patterns = []
    
    # Look for numeric columns that might indicate engagement or value
    numeric_cols = [info['column'] for info in column_info if 'int' in info['dtype'] or 'float' in info['dtype']]
    if numeric_cols:
        patterns.append(f"Numeric columns for scoring: {', '.join(numeric_cols[:5])}")
    
    # Look for status or stage columns
    status_cols = [info['column'] for info in column_info if any(keyword in info['column'].lower() for keyword in ['status', 'stage', 'phase', 'state'])]
    if status_cols:
        patterns.append(f"Status/Stage tracking: {', '.join(status_cols)}")
    
    # Look for time-based columns for recency analysis
    date_cols = [info['column'] for info in column_info if 'datetime' in info['dtype'] or any(keyword in info['column'].lower() for keyword in ['date', 'time'])]
    if date_cols:
        patterns.append(f"Temporal analysis opportunities: {', '.join(date_cols[:3])}")
    
    # Look for categorical columns with reasonable cardinality
    categorical_cols = [info['column'] for info in column_info if info['unique_values'] > 1 and info['unique_values'] < len(df) * 0.1 and 'object' in info['dtype']]
    if categorical_cols:
        patterns.append(f"Segmentation opportunities: {', '.join(categorical_cols[:3])}")
    
    if patterns:
        for pattern in patterns:
            print(f"  • {pattern}")
    else:
        print("  • Manual review needed to identify specific patterns")

def generate_model_recommendations(analysis_results):
    """
    Generate recommendations for the predictive model
    """
    print("Based on the data analysis, here are recommendations for building the OneLead predictive model:")
    print()
    
    print("1. 🎯 MODEL APPROACH:")
    print("   • Consider a multi-class classification model to predict opportunity likelihood")
    print("   • Use ensemble methods (Random Forest, Gradient Boosting) for robust predictions")
    print("   • Implement feature engineering for temporal patterns and engagement metrics")
    print()
    
    print("2. 📊 KEY FEATURE CATEGORIES TO FOCUS ON:")
    print("   • Customer engagement frequency and recency")
    print("   • Historical purchase patterns and deal sizes")
    print("   • Solution category preferences and fit scores")
    print("   • Geographic and industry segment data")
    print("   • Contact interaction patterns and response rates")
    print()
    
    print("3. 🔧 DATA PREPROCESSING RECOMMENDATIONS:")
    print("   • Handle missing values through imputation or feature flags")
    print("   • Create interaction features between customer and solution attributes")
    print("   • Engineer time-based features (days since last interaction, etc.)")
    print("   • Normalize numeric features and encode categorical variables")
    print()
    
    print("4. 📈 MODEL EVALUATION STRATEGY:")
    print("   • Use precision and recall metrics focusing on high-value opportunities")
    print("   • Implement time-based validation to avoid data leakage")
    print("   • Consider business metrics like potential revenue and consultant efficiency")
    print()
    
    print("5. 🚀 DEPLOYMENT CONSIDERATIONS:")
    print("   • Build a scoring pipeline that can update daily/weekly")
    print("   • Create interpretable features for consultant actionability")
    print("   • Implement feedback loops to continuously improve the model")
    print()
    
    total_records = sum([results['shape'][0] for results in analysis_results.values()])
    total_features = sum([results['shape'][1] for results in analysis_results.values()])
    
    print(f"📊 DATASET SUMMARY:")
    print(f"   • Total records across all sheets: {total_records:,}")
    print(f"   • Total potential features: {total_features:,}")
    print(f"   • Sheets available for analysis: {len(analysis_results)}")

if __name__ == "__main__":
    # File path
    excel_path = "/Users/jjayaraj/workspaces/HPE/onelead_system/data/onelead_consolidated_data_new.xlsx"
    
    # Check if file exists
    if not Path(excel_path).exists():
        print(f"❌ File not found: {excel_path}")
        sys.exit(1)
    
    # Run analysis
    results = analyze_excel_file(excel_path)
    
    if results:
        print("\n" + "="*80)
        print("✅ ANALYSIS COMPLETE")
        print("="*80)
        print("The analysis has been completed successfully.")
        print("Use the insights above to build your OneLead predictive model.")
    else:
        print("\n❌ Analysis failed. Please check the file format and try again.")