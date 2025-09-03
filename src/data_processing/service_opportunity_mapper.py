"""
HPE OneLead Service-Opportunity Mapping Module
Maps opportunities to relevant HPE services based on product lines and business needs
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class ServiceOpportunityMapper:
    """Maps HPE opportunities to relevant services and recommendations"""
    
    def __init__(self):
        # Product Line to Service Practice mapping
        self.product_to_service_mapping = {
            # Server/Compute related product lines
            'SY - x86 Premium and Scale-up Rack': {
                'primary_practice': 'Hybrid Cloud Consulting',
                'services': [
                    'Compute environment analysis services',
                    'Performance and Firmware Analysis',
                    'HPE Compute Transformation',
                    'Migration to HPE Compute Readiness Assessment'
                ],
                'service_type': 'Infrastructure Modernization'
            },
            '96 - Industry Standard Servers Support': {
                'primary_practice': 'Technical Services',
                'services': [
                    'HPE Complete Care',
                    'HPE Proactive Care',
                    'Firmware and Driver Updates',
                    'Performance Optimization Services'
                ],
                'service_type': 'Support & Maintenance'
            },
            'TR - BCS x-86 Servers': {
                'primary_practice': 'Hybrid Cloud Consulting',
                'services': [
                    'Server Consolidation Assessment',
                    'Virtualization Planning Services',
                    'Compute Optimization Workshop'
                ],
                'service_type': 'Infrastructure Optimization'
            },
            'OK - Cray XD Support': {
                'primary_practice': 'Technical Services',
                'services': [
                    'HPC Support Services',
                    'Performance Tuning for HPC',
                    'Cray System Administration Training'
                ],
                'service_type': 'Specialized Support'
            },
            
            # Networking related product lines
            'VR - WLAN HW Svcs': {
                'primary_practice': 'Network Services',
                'services': [
                    'Wireless Network Assessment',
                    'WLAN Design and Deployment',
                    'Network Security Assessment',
                    'Aruba Central Configuration Services'
                ],
                'service_type': 'Network Services'
            },
            'VL - WLAN HW': {
                'primary_practice': 'Network Services',
                'services': [
                    'Wireless Infrastructure Design',
                    'RF Coverage Planning',
                    'Network Migration Services'
                ],
                'service_type': 'Network Infrastructure'
            },
            'V3 - Ntwk Mngmt Svcs': {
                'primary_practice': 'Network Services',
                'services': [
                    'Network Management Platform Implementation',
                    'Network Monitoring and Analytics Setup',
                    'AIOps for Networks Implementation'
                ],
                'service_type': 'Network Management'
            },
            'SC - SD-WAN Support': {
                'primary_practice': 'Network Services',
                'services': [
                    'SD-WAN Design and Implementation',
                    'WAN Optimization Services',
                    'Branch Office Connectivity Solutions'
                ],
                'service_type': 'WAN Services'
            },
            'NV - CX Campus Agg-Core': {
                'primary_practice': 'Network Services',
                'services': [
                    'Campus Network Design',
                    'Core Network Modernization',
                    'Network Segmentation Services'
                ],
                'service_type': 'Campus Networks'
            },
            'WB - CX Campus Access': {
                'primary_practice': 'Network Services',
                'services': [
                    'Access Layer Design and Implementation',
                    'NAC Implementation Services',
                    'Zero Trust Network Architecture'
                ],
                'service_type': 'Network Access'
            },
            
            # Platform and Software related
            'HA - Integrated Platforms': {
                'primary_practice': 'Hybrid Cloud Engineering',
                'services': [
                    'Hyperconverged Infrastructure Assessment',
                    'SimpliVity Implementation Services',
                    'Platform Integration Services',
                    'Hybrid Cloud Design Workshop'
                ],
                'service_type': 'Platform Services'
            },
            'WQ - MCSeN IPS': {
                'primary_practice': 'Security Services',
                'services': [
                    'Security Assessment Services',
                    'Intrusion Prevention System Setup',
                    'Security Operations Center Design'
                ],
                'service_type': 'Security Services'
            },
            'KJ - MCSeN SW Support': {
                'primary_practice': 'Technical Services',
                'services': [
                    'Software Support Services',
                    'Patch Management Services',
                    'Software Lifecycle Management'
                ],
                'service_type': 'Software Support'
            },
            'K3 - Software Support': {
                'primary_practice': 'Technical Services',
                'services': [
                    'Application Support Services',
                    'Software Optimization Services',
                    'License Management Services'
                ],
                'service_type': 'Software Support'
            },
            'XG - MCx86 Software': {
                'primary_practice': 'Hybrid Cloud Engineering',
                'services': [
                    'Container Platform Services',
                    'Kubernetes Implementation',
                    'DevOps Transformation Services'
                ],
                'service_type': 'Software Modernization'
            },
            
            # Cloud Management
            'L5 - GL_Cloud Mgmt AAE': {
                'primary_practice': 'Hybrid Cloud Consulting',
                'services': [
                    'Cloud Management Platform Assessment',
                    'Multi-Cloud Strategy Workshop',
                    'Cloud Cost Optimization Services',
                    'CloudOps Implementation'
                ],
                'service_type': 'Cloud Management'
            },
            'X6 - GL_Cloud Mgmt AAS': {
                'primary_practice': 'Hybrid Cloud Consulting',
                'services': [
                    'Cloud Migration Planning',
                    'Application Modernization Assessment',
                    'Cloud Native Transformation'
                ],
                'service_type': 'Cloud Services'
            },
            
            # Complete Care and Lifecycle
            '9X - Complete Care Svcs': {
                'primary_practice': 'Technical Services',
                'services': [
                    'HPE Complete Care',
                    'Predictive Analytics for IT',
                    'Digital Experience Monitoring',
                    'IT Health Check Services'
                ],
                'service_type': 'Managed Services'
            },
            'UW - Generic Cust Lifecyc': {
                'primary_practice': 'Technical Services',
                'services': [
                    'Asset Lifecycle Management',
                    'Technology Refresh Planning',
                    'End-of-Life Migration Services'
                ],
                'service_type': 'Lifecycle Services'
            },
            'SI - Server Storage & Inf': {
                'primary_practice': 'Hybrid Cloud Engineering',
                'services': [
                    'Storage Assessment and Design',
                    'Data Migration Services',
                    'Backup and Recovery Planning',
                    'Storage Optimization Services'
                ],
                'service_type': 'Storage Services'
            }
        }
        
        # Service value scores (for prioritization)
        self.service_value_scores = {
            'Infrastructure Modernization': 0.9,
            'Cloud Management': 0.85,
            'Cloud Services': 0.85,
            'Platform Services': 0.8,
            'Security Services': 0.8,
            'Network Services': 0.75,
            'Storage Services': 0.75,
            'Software Modernization': 0.7,
            'Network Infrastructure': 0.7,
            'Network Management': 0.65,
            'WAN Services': 0.65,
            'Campus Networks': 0.6,
            'Network Access': 0.6,
            'Managed Services': 0.6,
            'Support & Maintenance': 0.5,
            'Infrastructure Optimization': 0.5,
            'Software Support': 0.4,
            'Lifecycle Services': 0.4,
            'Specialized Support': 0.3
        }
    
    def map_opportunity_to_services(self, opportunities_df: pd.DataFrame) -> pd.DataFrame:
        """Map opportunities to relevant services based on product lines"""
        
        mapped_data = []
        
        for _, opp in opportunities_df.iterrows():
            # Use standardized lowercase column names from data_loader_v2
            product_line = opp.get('product_line') or opp.get('Product Line')
            opp_id = opp.get('opportunity_id') or opp.get('HPE Opportunity ID') or ''
            account_id = opp.get('account_st_id') or opp.get('Account ST ID') or ''
            account_name = opp.get('account_name') or opp.get('Account Name') or ''
            
            if pd.isna(product_line) or product_line not in self.product_to_service_mapping:
                # Default mapping for unknown product lines
                service_info = {
                    'primary_practice': 'Technical Services',
                    'services': ['General Consulting Services', 'Technology Assessment'],
                    'service_type': 'General Services'
                }
            else:
                service_info = self.product_to_service_mapping[product_line]
            
            mapped_data.append({
                'opportunity_id': opp_id,
                'account_id': account_id,
                'account_name': account_name,
                'product_line': product_line,
                'primary_practice': service_info['primary_practice'],
                'recommended_services': ', '.join(service_info['services'][:3]),  # Top 3 services
                'all_services': service_info['services'],
                'service_type': service_info['service_type'],
                'service_priority': self.service_value_scores.get(service_info['service_type'], 0.5)
            })
        
        return pd.DataFrame(mapped_data)
    
    def get_customer_service_recommendations(self, opportunities_df: pd.DataFrame, 
                                            install_base_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """Generate comprehensive service recommendations per customer"""
        
        # Map opportunities to services
        opp_services = self.map_opportunity_to_services(opportunities_df)
        
        # Aggregate by customer
        customer_recommendations = opp_services.groupby('account_id').agg({
            'account_name': 'first',
            'opportunity_id': 'count',
            'product_line': lambda x: list(x.unique()),
            'primary_practice': lambda x: list(x.unique()),
            'service_type': lambda x: list(x.unique()),
            'service_priority': 'mean'
        }).reset_index()
        
        customer_recommendations.columns = [
            'customer_id', 'customer_name', 'opportunity_count',
            'product_lines', 'recommended_practices', 'service_types', 'avg_priority'
        ]
        
        # Add install base context if available
        if install_base_df is not None:
            # Add EOL urgency
            eol_summary = install_base_df.groupby('account_sales_territory_id').agg({
                'days_to_eol': lambda x: (x < 0).sum(),
                'days_to_eos': lambda x: (x < 0).sum()
            }).reset_index()
            eol_summary.columns = ['customer_id', 'expired_products', 'eos_products']
            
            # Ensure customer_id types match
            customer_recommendations['customer_id'] = customer_recommendations['customer_id'].astype(str)
            eol_summary['customer_id'] = eol_summary['customer_id'].astype(str)
            
            customer_recommendations = customer_recommendations.merge(
                eol_summary, on='customer_id', how='left'
            )
            
            # Adjust priority based on EOL urgency
            customer_recommendations['expired_products'] = customer_recommendations['expired_products'].fillna(0)
            customer_recommendations['urgency_adjusted_priority'] = (
                customer_recommendations['avg_priority'] * 
                (1 + customer_recommendations['expired_products'] * 0.1)
            ).clip(upper=1.0)
        
        # Create actionable recommendations
        customer_recommendations['primary_recommendation'] = customer_recommendations.apply(
            self._generate_primary_recommendation, axis=1
        )
        
        return customer_recommendations.sort_values('avg_priority', ascending=False)
    
    def _generate_primary_recommendation(self, row) -> str:
        """Generate primary service recommendation for a customer"""
        
        service_types = row.get('service_types', [])
        expired = row.get('expired_products', 0)
        
        if expired > 0:
            return f"Immediate Action: {int(expired)} expired products. Recommend Technology Refresh Planning and Migration Services"
        elif 'Cloud Management' in service_types or 'Cloud Services' in service_types:
            return "Strategic: Cloud transformation opportunity. Recommend Multi-Cloud Strategy Workshop"
        elif 'Security Services' in service_types:
            return "Critical: Security enhancement needed. Recommend Security Assessment Services"
        elif 'Infrastructure Modernization' in service_types:
            return "High Value: Infrastructure refresh opportunity. Recommend Compute Transformation Services"
        elif 'Network Services' in service_types:
            return "Operational: Network optimization opportunity. Recommend Network Assessment"
        else:
            return "Standard: Technology assessment recommended to identify optimization opportunities"
    
    def get_service_catalog_mapping(self, services_df: pd.DataFrame) -> pd.DataFrame:
        """Create a structured service catalog from the services sheet"""
        
        # Clean and structure the service catalog
        services_clean = services_df.dropna(subset=['Services']).copy()
        services_clean['Practice'] = services_clean['Practice'].fillna(method='ffill')
        services_clean['Sub-Practice'] = services_clean['Sub-Practice'].fillna('General')
        
        return services_clean
    
    def calculate_service_coverage(self, opportunities_df: pd.DataFrame, 
                                  service_credits_df: Optional[pd.DataFrame] = None) -> Dict:
        """Calculate service coverage metrics for opportunities"""
        
        # Map opportunities to services
        opp_services = self.map_opportunity_to_services(opportunities_df)
        
        coverage_metrics = {
            'total_opportunities': len(opportunities_df),
            'mapped_opportunities': len(opp_services),
            'unique_service_types': opp_services['service_type'].nunique(),
            'avg_service_priority': opp_services['service_priority'].mean(),
            'high_priority_opportunities': len(opp_services[opp_services['service_priority'] >= 0.8]),
            'service_type_distribution': opp_services['service_type'].value_counts().to_dict(),
            'practice_distribution': opp_services['primary_practice'].value_counts().to_dict()
        }
        
        # Add service credit utilization if available
        if service_credits_df is not None and len(service_credits_df) > 0:
            # Use lowercase column names as they're standardized in data_loader_v2
            purchased_col = 'purchased_credits' if 'purchased_credits' in service_credits_df.columns else 'PurchasedCredits'
            delivered_col = 'delivered_credits' if 'delivered_credits' in service_credits_df.columns else 'DeliveredCredits'
            
            if purchased_col in service_credits_df.columns and delivered_col in service_credits_df.columns:
                total_purchased = service_credits_df[purchased_col].sum()
                total_delivered = service_credits_df[delivered_col].sum()
                utilization = (total_delivered / total_purchased * 100) if total_purchased > 0 else 0
                
                coverage_metrics['service_credit_utilization'] = utilization
                coverage_metrics['unused_credits'] = total_purchased - total_delivered
        
        return coverage_metrics