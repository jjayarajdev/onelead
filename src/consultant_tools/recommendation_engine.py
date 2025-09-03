"""
HPE OneLead Consultant Recommendation Engine
Provides actionable recommendations and conversation starters for HPE consultants
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ConsultantRecommendationEngine:
    """Generate actionable recommendations for HPE consultants"""
    
    def __init__(self):
        self.conversation_templates = self._load_conversation_templates()
        self.action_priorities = self._define_action_priorities()
    
    def _load_conversation_templates(self) -> Dict[str, Dict[str, str]]:
        """Load conversation starter templates for different scenarios"""
        return {
            'product_renewal': {
                'urgent': "Hi {customer_name}, our records show you have critical products reaching end-of-life in the next {days} days. I'd like to schedule a quick call to discuss seamless upgrade options that could improve your ROI by up to 30%.",
                'planned': "Hello {customer_name}, I wanted to reach out about your upcoming product renewals in the next {days} days. Let's explore modernization opportunities that align with your business objectives.",
                'subject': "Critical: Product Lifecycle Planning for {customer_name}"
            },
            'service_expansion': {
                'underutilized': "Hi {customer_name}, I've noticed you're currently utilizing {utilization_rate}% of your service credits. There might be untapped potential we could explore together. Can we schedule 30 minutes to discuss additional use cases?",
                'unused_credits': "Hello {customer_name}, you have {unused_credits} service credits that expire in {days} days. Let's ensure you maximize this investment with additional services that could benefit your operations.",
                'subject': "Maximize Your Service Investment - {customer_name}"
            },
            'cross_sell': {
                'platform_expansion': "Hi {customer_name}, given your success with {current_platform}, I'd love to show you how {recommended_platform} could complement your existing infrastructure and unlock new capabilities.",
                'solution_gap': "Hello {customer_name}, based on your current HPE portfolio, I've identified potential gaps where additional solutions could enhance your {business_area} operations. Are you available for a brief discussion?",
                'subject': "Enhance Your HPE Portfolio - Strategic Opportunities"
            },
            'success_follow_up': {
                'project_completion': "Congratulations {customer_name} on the successful completion of your {project_type} project! With your proven track record, are you ready to tackle the next strategic initiative?",
                'performance_recognition': "Hi {customer_name}, I wanted to acknowledge the excellent results from your recent HPE implementation. Based on this success, I have some ideas for your next phase of growth.",
                'subject': "Building on Your Success - Next Steps for {customer_name}"
            },
            'relationship_building': {
                'new_opportunity': "Hi {customer_name}, I hope you're doing well. I wanted to connect about some new HPE innovations that specifically address challenges in {industry_area}. Would you be interested in a brief overview?",
                'check_in': "Hello {customer_name}, it's been {days} days since our last interaction. I'd love to check in and see how your current initiatives are progressing and if there's any way HPE can support your goals.",
                'subject': "Checking In - How Can HPE Support Your Goals?"
            }
        }
    
    def _define_action_priorities(self) -> Dict[str, int]:
        """Define priority weights for different action types"""
        return {
            'critical_renewal': 10,
            'urgent_renewal': 8,
            'service_expiration': 7,
            'cross_sell_high': 6,
            'service_expansion': 5,
            'planned_renewal': 4,
            'cross_sell_medium': 3,
            'relationship_building': 2,
            'general_follow_up': 1
        }
    
    def generate_customer_recommendations(self, customer_data: pd.Series, 
                                        prediction_data: pd.Series) -> Dict[str, any]:
        """Generate comprehensive recommendations for a specific customer"""
        
        recommendations = {
            'customer_id': customer_data['customer_id'],
            'priority_actions': [],
            'conversation_starters': [],
            'next_steps': [],
            'risk_flags': [],
            'opportunity_areas': []
        }
        
        # Analyze customer situation
        self._analyze_renewal_opportunities(customer_data, prediction_data, recommendations)
        self._analyze_service_opportunities(customer_data, prediction_data, recommendations)
        self._analyze_cross_sell_opportunities(customer_data, prediction_data, recommendations)
        self._analyze_relationship_opportunities(customer_data, prediction_data, recommendations)
        
        # Sort actions by priority
        recommendations['priority_actions'].sort(key=lambda x: x['priority'], reverse=True)
        
        return recommendations
    
    def _analyze_renewal_opportunities(self, customer_data: pd.Series, 
                                     prediction_data: pd.Series, recommendations: Dict):
        """Analyze product and contract renewal opportunities"""
        
        # Product end-of-life urgency
        eol_urgency = customer_data.get('eol_urgency_score', 0)
        days_to_eol = customer_data.get('min_days_to_eol', 999)
        
        if eol_urgency >= 3 and days_to_eol <= 90:
            recommendations['priority_actions'].append({
                'type': 'critical_renewal',
                'priority': self.action_priorities['critical_renewal'],
                'title': 'Critical Product Renewal Required',
                'description': f'Products reaching end-of-life in {days_to_eol} days',
                'urgency': 'Critical',
                'timeline': 'Immediate action required'
            })
            
            recommendations['conversation_starters'].append({
                'scenario': 'product_renewal',
                'template': 'urgent',
                'variables': {'days': days_to_eol}
            })
            
            recommendations['risk_flags'].append('Product end-of-life approaching')
        
        elif eol_urgency >= 2 and days_to_eol <= 365:
            recommendations['priority_actions'].append({
                'type': 'urgent_renewal',
                'priority': self.action_priorities['urgent_renewal'],
                'title': 'Product Renewal Planning',
                'description': f'Products reaching end-of-life in {days_to_eol} days',
                'urgency': 'High',
                'timeline': 'Within next quarter'
            })
            
            recommendations['conversation_starters'].append({
                'scenario': 'product_renewal',
                'template': 'planned',
                'variables': {'days': days_to_eol}
            })
        
        # Contract renewal urgency
        contract_renewal_urgency = customer_data.get('contract_renewal_urgency', 0)
        days_to_contract_end = customer_data.get('min_days_to_contract_end', 999)
        
        if contract_renewal_urgency == 1:
            recommendations['priority_actions'].append({
                'type': 'service_expiration',
                'priority': self.action_priorities['service_expiration'],
                'title': 'Service Contract Renewal',
                'description': f'Service contract expires in {days_to_contract_end} days',
                'urgency': 'High',
                'timeline': 'Within 30 days'
            })
    
    def _analyze_service_opportunities(self, customer_data: pd.Series, 
                                     prediction_data: pd.Series, recommendations: Dict):
        """Analyze service expansion and utilization opportunities"""
        
        # Low service utilization
        low_utilization = customer_data.get('low_utilization_risk', 0)
        utilization_rate = customer_data.get('avg_credit_utilization', 0)
        
        if low_utilization == 1 and utilization_rate < 0.5:
            recommendations['priority_actions'].append({
                'type': 'service_expansion',
                'priority': self.action_priorities['service_expansion'],
                'title': 'Service Credit Underutilization',
                'description': f'Currently utilizing {utilization_rate:.1%} of service credits',
                'urgency': 'Medium',
                'timeline': 'Within 60 days'
            })
            
            recommendations['conversation_starters'].append({
                'scenario': 'service_expansion',
                'template': 'underutilized',
                'variables': {'utilization_rate': f"{utilization_rate:.1%}"}
            })
            
            recommendations['opportunity_areas'].append('Service portfolio expansion')
        
        # Unused credits approaching expiration
        # This would require additional data about credit expiration dates
        
    def _analyze_cross_sell_opportunities(self, customer_data: pd.Series, 
                                        prediction_data: pd.Series, recommendations: Dict):
        """Analyze cross-selling and upselling opportunities"""
        
        platform_diversity = customer_data.get('platform_diversity', 0)
        predicted_propensity = prediction_data.get('predicted_propensity', 'Low')
        
        # Low platform diversity = cross-sell opportunity
        if platform_diversity <= 2 and predicted_propensity in ['High', 'Medium']:
            priority_type = 'cross_sell_high' if predicted_propensity == 'High' else 'cross_sell_medium'
            
            recommendations['priority_actions'].append({
                'type': priority_type,
                'priority': self.action_priorities[priority_type],
                'title': 'Platform Expansion Opportunity',
                'description': f'Customer using {platform_diversity} platform(s) - expansion potential',
                'urgency': 'Medium' if predicted_propensity == 'High' else 'Low',
                'timeline': 'Within 90 days'
            })
            
            recommendations['conversation_starters'].append({
                'scenario': 'cross_sell',
                'template': 'platform_expansion',
                'variables': {'platform_diversity': platform_diversity}
            })
            
            recommendations['opportunity_areas'].append('Technology portfolio expansion')
    
    def _analyze_relationship_opportunities(self, customer_data: pd.Series, 
                                          prediction_data: pd.Series, recommendations: Dict):
        """Analyze relationship building and engagement opportunities"""
        
        project_success_rate = customer_data.get('project_success_rate', 0)
        recent_engagement = customer_data.get('recent_engagement', 0)
        days_since_last_project = customer_data.get('days_since_last_project', 999)
        
        # High success rate customers
        if project_success_rate >= 0.8:
            recommendations['priority_actions'].append({
                'type': 'relationship_building',
                'priority': self.action_priorities['relationship_building'],
                'title': 'Trusted Partner Opportunity',
                'description': f'{project_success_rate:.1%} project success rate - ready for larger initiatives',
                'urgency': 'Low',
                'timeline': 'Ongoing relationship building'
            })
            
            recommendations['conversation_starters'].append({
                'scenario': 'success_follow_up',
                'template': 'performance_recognition',
                'variables': {}
            })
            
            recommendations['opportunity_areas'].append('Strategic partnership expansion')
        
        # Long time since last engagement
        if days_since_last_project > 180:
            recommendations['priority_actions'].append({
                'type': 'general_follow_up',
                'priority': self.action_priorities['general_follow_up'],
                'title': 'Re-engagement Opportunity',
                'description': f'{days_since_last_project} days since last project',
                'urgency': 'Low',
                'timeline': 'Proactive outreach'
            })
            
            recommendations['conversation_starters'].append({
                'scenario': 'relationship_building',
                'template': 'check_in',
                'variables': {'days': days_since_last_project}
            })
    
    def generate_conversation_starter(self, scenario: str, template: str, 
                                    customer_name: str = None, variables: Dict = None) -> Dict[str, str]:
        """Generate personalized conversation starter"""
        
        if scenario not in self.conversation_templates:
            return {'subject': 'Follow up', 'message': 'Generic follow up message'}
        
        scenario_templates = self.conversation_templates[scenario]
        
        if template not in scenario_templates:
            template = list(scenario_templates.keys())[0]  # Use first available template
        
        message_template = scenario_templates[template]
        subject_template = scenario_templates.get('subject', 'HPE Follow Up')
        
        # Fill in variables
        variables = variables or {}
        if customer_name:
            variables['customer_name'] = customer_name
        
        try:
            message = message_template.format(**variables)
            subject = subject_template.format(**variables)
        except KeyError as e:
            logger.warning(f"Missing variable {e} in conversation template")
            message = message_template
            subject = subject_template
        
        return {
            'subject': subject,
            'message': message,
            'scenario': scenario,
            'template': template
        }
    
    def batch_generate_recommendations(self, features_df: pd.DataFrame, 
                                     predictions_df: pd.DataFrame, 
                                     top_n: int = 50) -> pd.DataFrame:
        """Generate recommendations for top N customers"""
        
        # Merge features and predictions
        combined_data = features_df.merge(
            predictions_df[['customer_id', 'predicted_propensity', 'prediction_confidence']], 
            on='customer_id', 
            how='left'
        )
        
        # Get top N customers by prediction confidence and propensity
        top_customers = combined_data[
            combined_data['predicted_propensity'].isin(['High', 'Medium'])
        ].nlargest(top_n, 'prediction_confidence')
        
        recommendations_list = []
        
        for _, row in top_customers.iterrows():
            customer_features = row
            prediction_data = row
            
            rec = self.generate_customer_recommendations(customer_features, prediction_data)
            
            # Flatten for DataFrame
            if rec['priority_actions']:
                top_action = rec['priority_actions'][0]
                recommendations_list.append({
                    'customer_id': rec['customer_id'],
                    'predicted_propensity': prediction_data['predicted_propensity'],
                    'prediction_confidence': prediction_data['prediction_confidence'],
                    'top_action_type': top_action['type'],
                    'top_action_title': top_action['title'],
                    'top_action_urgency': top_action['urgency'],
                    'top_action_timeline': top_action['timeline'],
                    'num_actions': len(rec['priority_actions']),
                    'num_opportunities': len(rec['opportunity_areas']),
                    'risk_flags': '; '.join(rec['risk_flags']) if rec['risk_flags'] else 'None'
                })
            else:
                recommendations_list.append({
                    'customer_id': rec['customer_id'],
                    'predicted_propensity': prediction_data['predicted_propensity'],
                    'prediction_confidence': prediction_data['prediction_confidence'],
                    'top_action_type': 'general_follow_up',
                    'top_action_title': 'General Follow-up',
                    'top_action_urgency': 'Low',
                    'top_action_timeline': 'Ongoing',
                    'num_actions': 0,
                    'num_opportunities': 0,
                    'risk_flags': 'None'
                })
        
        return pd.DataFrame(recommendations_list)
    
    def get_action_summary(self, recommendations_df: pd.DataFrame) -> Dict[str, int]:
        """Get summary of recommended actions"""
        
        action_counts = recommendations_df['top_action_type'].value_counts().to_dict()
        urgency_counts = recommendations_df['top_action_urgency'].value_counts().to_dict()
        
        return {
            'total_recommendations': len(recommendations_df),
            'action_breakdown': action_counts,
            'urgency_breakdown': urgency_counts,
            'high_priority_actions': len(recommendations_df[
                recommendations_df['top_action_urgency'] == 'Critical'
            ]) + len(recommendations_df[
                recommendations_df['top_action_urgency'] == 'High'
            ])
        }