"""
Recommendation Engine for Cross-sell and Up-sell opportunities.
Analyzes install base, past projects, and service credits to generate actionable recommendations.
"""

import re
from typing import Dict, List, Tuple
from collections import Counter
from sqlalchemy.orm import Session
from src.models import Account, InstallBase, Project, ServiceCredit, ServiceSKUMapping, ServiceCatalog


class RecommendationEngine:
    """Generate cross-sell and up-sell recommendations for accounts."""

    def __init__(self, session: Session):
        """Initialize recommendation engine."""
        self.session = session

        # Service keywords for matching
        self.service_keywords = {
            'Health Check': ['health', 'アセスメント', 'assessment', '診断'],
            'Firmware Upgrade': ['firmware', 'upgrade', 'vup', 'os更新', '更改'],
            'Migration': ['migration', '移行', '移設'],
            'Installation': ['install', '構築', 'deployment', '導入'],
            'Security': ['security', 'セキュリティ', 'sec'],
            'Virtualization': ['仮想', 'virtual', 'vmware', 'vcenter'],
            'Cloud': ['cloud', 'クラウド'],
            'Network': ['network', 'ネットワーク', 'nw'],
            'Backup': ['backup', 'バックアップ', 'dr'],
            'Storage': ['storage', 'ストレージ', '3par', 'primera']
        }

        # Enhancement paths for up-sell
        self.enhancement_paths = {
            'virtualization': {
                'keywords': ['仮想', 'virtual', 'vmware', 'vcenter'],
                'enhancements': [
                    'Advanced Virtualization Optimization',
                    'Container/Kubernetes Platform'
                ]
            },
            'network': {
                'keywords': ['network', 'ネットワーク', 'nw', 'switch'],
                'enhancements': [
                    'Advanced Network Security (Zero Trust)',
                    'SD-WAN Implementation'
                ]
            },
            'cloud': {
                'keywords': ['cloud', 'クラウド'],
                'enhancements': [
                    'Cloud Cost Optimization',
                    'Multi-Cloud Strategy'
                ]
            },
            'backup': {
                'keywords': ['backup', 'バックアップ', 'dr'],
                'enhancements': [
                    'Enterprise DR/BC Program'
                ]
            }
        }

    def generate_recommendations(self, territory_id: str) -> Dict:
        """
        Generate comprehensive recommendations for an account.

        Args:
            territory_id: Account ST ID / Territory ID

        Returns:
            Dict with cross_sell, up_sell, and priority_actions
        """
        # Get all data for this account
        install_base = self.session.query(InstallBase).filter(
            InstallBase.territory_id == territory_id
        ).all()

        projects = self.session.query(Project).join(Account).filter(
            Account.territory_id == territory_id
        ).all()

        service_credits = self.session.query(ServiceCredit).filter(
            ServiceCredit.territory_id == territory_id
        ).all()

        if not projects and not install_base:
            return {
                'cross_sell': [],
                'up_sell': [],
                'priority_actions': []
            }

        # Analyze data
        hardware_analysis = self._analyze_hardware(install_base)
        project_analysis = self._analyze_projects(projects)
        credit_analysis = self._analyze_credits(service_credits)

        # Generate recommendations
        cross_sell = self._generate_cross_sell(
            hardware_analysis,
            project_analysis,
            install_base,
            projects
        )

        up_sell = self._generate_up_sell(
            project_analysis,
            projects
        )

        priority_actions = self._generate_priority_actions(
            hardware_analysis,
            project_analysis,
            credit_analysis,
            install_base,
            service_credits
        )

        return {
            'cross_sell': cross_sell,
            'up_sell': up_sell,
            'priority_actions': priority_actions,
            'stats': {
                'total_hardware': len(install_base),
                'total_projects': len(projects),
                'active_credits': credit_analysis['total_active'],
                'expired_hardware': hardware_analysis['expired_count']
            }
        }

    def _analyze_hardware(self, install_base: List[InstallBase]) -> Dict:
        """Analyze install base hardware."""
        analysis = {
            'total': len(install_base),
            'expired_count': 0,
            'categories': {},
            'products': []
        }

        for hw in install_base:
            # Check if expired
            if hw.support_status and 'expired' in hw.support_status.lower():
                analysis['expired_count'] += 1

            # Categorize
            category = self._categorize_hardware(hw.product_name)
            if category not in analysis['categories']:
                analysis['categories'][category] = []
            analysis['categories'][category].append(hw)

            analysis['products'].append(hw.product_name)

        return analysis

    def _categorize_hardware(self, product_name: str) -> str:
        """Categorize hardware by type."""
        prod_lower = product_name.lower()

        if any(kw in prod_lower for kw in ['dl', 'ml', 'bl', 'gen', 'server']):
            return 'Servers'
        elif any(kw in prod_lower for kw in ['3par', 'primera', 'alletra', 'nimble', 'msa']):
            return 'Storage'
        elif any(kw in prod_lower for kw in ['aruba', 'switch', 'network']):
            return 'Networking'
        else:
            return 'Other'

    def _analyze_projects(self, projects: List[Project]) -> Dict:
        """Analyze past project patterns."""
        if not projects:
            # Return complete structure even with no projects
            empty_service_usage = {service: 0 for service in self.service_keywords}
            return {
                'total': 0,
                'practice_dist': {},
                'service_usage': empty_service_usage,
                'service_usage_pct': {k: 0 for k in empty_service_usage},
                'size_dist': {},
                'avg_size_category': None
            }

        practice_counter = Counter()
        size_counter = Counter()
        service_usage = {service: 0 for service in self.service_keywords}

        for proj in projects:
            # Practice distribution
            if proj.practice:
                practice_counter[proj.practice] += 1

            # Size distribution
            if proj.size_category:
                size_counter[proj.size_category] += 1

            # Service keyword matching
            if proj.project_description:
                desc_lower = proj.project_description.lower()
                for service_name, keywords in self.service_keywords.items():
                    if any(kw.lower() in desc_lower for kw in keywords):
                        service_usage[service_name] += 1

        # Calculate percentages
        total = len(projects)
        practice_dist = {k: (v / total * 100) for k, v in practice_counter.items()}
        size_dist = {k: (v / total * 100) for k, v in size_counter.items()}

        return {
            'total': total,
            'practice_dist': practice_dist,
            'service_usage': service_usage,
            'service_usage_pct': {k: (v / total * 100) for k, v in service_usage.items()},
            'size_dist': size_dist,
            'avg_size_category': size_counter.most_common(1)[0][0] if size_counter else None
        }

    def _analyze_credits(self, service_credits: List[ServiceCredit]) -> Dict:
        """Analyze service credits."""
        total_active = sum(sc.active_credits for sc in service_credits if sc.active_credits)
        total_purchased = sum(sc.purchased_credits for sc in service_credits if sc.purchased_credits)

        expiring_soon = []
        for sc in service_credits:
            if sc.active_credits > 0 and sc.expiry_in_days:
                if any(exp in sc.expiry_in_days for exp in ['0-45', '46-90']):
                    expiring_soon.append(sc)

        return {
            'total_active': total_active,
            'total_purchased': total_purchased,
            'expiring_soon': expiring_soon,
            'has_credits': total_active > 0
        }

    def _generate_cross_sell(
        self,
        hardware_analysis: Dict,
        project_analysis: Dict,
        install_base: List[InstallBase],
        projects: List[Project]
    ) -> List[Dict]:
        """Generate cross-sell recommendations (services they don't have)."""
        recommendations = []

        # If no projects, all services are cross-sell opportunities
        total_projects = project_analysis.get('total', 0)
        if total_projects == 0:
            # Special handling for accounts with hardware but no project history
            if 'Servers' in hardware_analysis['categories']:
                servers = hardware_analysis['categories']['Servers']
                recommendations.append({
                    'service': 'Server Health Check',
                    'category': 'Hardware-Based',
                    'reason': f'You own {len(servers)} server(s) with no recorded service history',
                    'priority': 'HIGH' if hardware_analysis['expired_count'] > 0 else 'MEDIUM',
                    'hardware_context': [s.product_name for s in servers[:3]],
                    'gap_indicator': 'No service history available'
                })

            if 'Networking' in hardware_analysis['categories']:
                network_devices = hardware_analysis['categories']['Networking']
                recommendations.append({
                    'service': 'Network Assessment',
                    'category': 'Hardware-Based',
                    'reason': f'You own {len(network_devices)} network device(s) with no service history',
                    'priority': 'MEDIUM',
                    'hardware_context': [d.product_name for d in network_devices[:3]],
                    'gap_indicator': 'No service history available'
                })

            return recommendations[:5]  # Limit for no-history accounts

        # Hardware-based cross-sell (with project history)
        if 'Servers' in hardware_analysis['categories']:
            servers = hardware_analysis['categories']['Servers']

            # Check health check usage
            health_check_usage = project_analysis['service_usage_pct'].get('Health Check', 0)
            if health_check_usage < 5:  # Less than 5% usage
                recommendations.append({
                    'service': 'Server Health Check',
                    'category': 'Hardware-Based',
                    'reason': f'You own {len(servers)} server(s) but Health Check was used in only {health_check_usage:.1f}% of projects',
                    'priority': 'HIGH' if hardware_analysis['expired_count'] > 0 else 'MEDIUM',
                    'hardware_context': [s.product_name for s in servers[:3]],
                    'gap_indicator': f'{int(project_analysis["service_usage"]["Health Check"])}/{project_analysis["total"]} projects'
                })

            # Check firmware upgrade usage
            firmware_usage = project_analysis['service_usage_pct'].get('Firmware Upgrade', 0)
            if firmware_usage < 10:
                recommendations.append({
                    'service': 'Firmware Update Service',
                    'category': 'Hardware-Based',
                    'reason': f'Firmware upgrades found in only {firmware_usage:.1f}% of projects',
                    'priority': 'MEDIUM',
                    'hardware_context': [s.product_name for s in servers[:3]],
                    'gap_indicator': f'{int(project_analysis["service_usage"]["Firmware Upgrade"])}/{project_analysis["total"]} projects'
                })

        if 'Networking' in hardware_analysis['categories']:
            network_devices = hardware_analysis['categories']['Networking']
            network_usage = project_analysis['service_usage_pct'].get('Network', 0)

            if network_usage < 15:  # Low network service usage
                recommendations.append({
                    'service': 'Network Health Check & Optimization',
                    'category': 'Hardware-Based',
                    'reason': f'You own {len(network_devices)} network device(s) but network services used in only {network_usage:.1f}% of projects',
                    'priority': 'MEDIUM',
                    'hardware_context': [d.product_name for d in network_devices[:3]],
                    'gap_indicator': f'{int(project_analysis["service_usage"]["Network"])}/{project_analysis["total"]} projects'
                })

        # Practice-based cross-sell
        top_practices = sorted(
            project_analysis['practice_dist'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:2]

        for practice, pct in top_practices:
            if pct > 20:  # Significant practice
                # Cloud & Platform with low backup
                if 'CLD' in practice and project_analysis['service_usage_pct'].get('Backup', 0) < 5:
                    recommendations.append({
                        'service': 'Cloud Backup & Disaster Recovery',
                        'category': 'Practice-Based',
                        'reason': f'{pct:.1f}% of your projects are {practice}, but minimal backup/DR coverage',
                        'priority': 'HIGH',
                        'hardware_context': None,
                        'gap_indicator': f'Backup in only {int(project_analysis["service_usage"]["Backup"])} projects'
                    })

                # Network & Security practice
                if 'NTWK' in practice or 'CYB' in practice:
                    security_usage = project_analysis['service_usage_pct'].get('Security', 0)
                    if security_usage < 10:
                        recommendations.append({
                            'service': 'Advanced Security Assessment',
                            'category': 'Practice-Based',
                            'reason': f'{pct:.1f}% of projects are network/security related, opportunity for advanced services',
                            'priority': 'MEDIUM',
                            'hardware_context': None,
                            'gap_indicator': f'Security in {int(project_analysis["service_usage"]["Security"])} projects'
                        })

        return recommendations[:8]  # Limit to top 8

    def _generate_up_sell(
        self,
        project_analysis: Dict,
        projects: List[Project]
    ) -> List[Dict]:
        """Generate up-sell recommendations (enhanced services)."""
        recommendations = []

        # If no projects, no up-sell opportunities
        if not projects or project_analysis.get('total', 0) == 0:
            return []

        # Enhancement up-sell
        for service_area, config in self.enhancement_paths.items():
            # Check if they're using the basic service
            usage_count = 0
            for proj in projects:
                if proj.project_description:
                    desc_lower = proj.project_description.lower()
                    if any(kw.lower() in desc_lower for kw in config['keywords']):
                        usage_count += 1

            if usage_count > 0:
                usage_pct = (usage_count / len(projects) * 100)

                for enhancement in config['enhancements']:
                    recommendations.append({
                        'service': enhancement,
                        'category': 'Enhancement',
                        'current_service': service_area.title(),
                        'current_usage': f'{usage_count} projects ({usage_pct:.1f}%)',
                        'reason': f'Upgrade from basic {service_area} to {enhancement.lower()}',
                        'priority': 'HIGH' if usage_pct > 10 else 'MEDIUM'
                    })

        # Volume up-sell (consolidate small projects)
        if project_analysis['size_dist'].get('<$50k', 0) > 50:
            small_count = sum(1 for p in projects if p.size_category == '<$50k')
            recommendations.append({
                'service': 'Enterprise Strategic Program',
                'category': 'Volume Consolidation',
                'current_service': f'{small_count} small projects annually',
                'current_usage': f'{project_analysis["size_dist"]["<$50k"]:.1f}% projects are <$50K',
                'reason': 'Consolidate many small projects into strategic program for better value and efficiency',
                'priority': 'HIGH'
            })

        return recommendations[:8]  # Limit to top 8

    def _generate_priority_actions(
        self,
        hardware_analysis: Dict,
        project_analysis: Dict,
        credit_analysis: Dict,
        install_base: List[InstallBase],
        service_credits: List[ServiceCredit]
    ) -> List[Dict]:
        """Generate priority/urgent actions."""
        actions = []

        # Expired hardware without health checks
        if hardware_analysis['expired_count'] > 0:
            health_check_count = project_analysis['service_usage'].get('Health Check', 0)

            if health_check_count < 5:
                actions.append({
                    'action': 'Emergency Health Check Required',
                    'reason': f'{hardware_analysis["expired_count"]} hardware item(s) with EXPIRED support',
                    'urgency': 'IMMEDIATE',
                    'risk': 'Hardware failure with no vendor support',
                    'affected_items': hardware_analysis['expired_count']
                })

        # Service credits expiring soon
        if credit_analysis['expiring_soon']:
            for sc in credit_analysis['expiring_soon'][:3]:  # Top 3
                actions.append({
                    'action': f'Use {sc.active_credits} Service Credits',
                    'reason': f'Credits expire in {sc.expiry_in_days}',
                    'urgency': 'HIGH',
                    'risk': 'Credits will be lost if not used',
                    'affected_items': sc.active_credits
                })

        # High practice activity but missing critical service
        top_practice = max(
            project_analysis['practice_dist'].items(),
            key=lambda x: x[1]
        ) if project_analysis['practice_dist'] else None

        if top_practice and top_practice[1] > 50:
            practice_name, pct = top_practice
            if 'CLD' in practice_name:
                backup_count = project_analysis['service_usage'].get('Backup', 0)
                if backup_count < 10:
                    actions.append({
                        'action': 'Cloud Backup Assessment Needed',
                        'reason': f'High cloud activity ({pct:.1f}%) but minimal backup/DR coverage',
                        'urgency': 'HIGH',
                        'risk': 'Business continuity gap',
                        'affected_items': None
                    })

        return actions

    def get_account_summary(self, territory_id: str) -> Dict:
        """Get quick summary of account for search results."""
        account = self.session.query(Account).filter(
            Account.territory_id == territory_id
        ).first()

        if not account:
            return None

        install_base_count = self.session.query(InstallBase).filter(
            InstallBase.territory_id == territory_id
        ).count()

        project_count = self.session.query(Project).join(Account).filter(
            Account.territory_id == territory_id
        ).count()

        credits = self.session.query(ServiceCredit).filter(
            ServiceCredit.territory_id == territory_id
        ).all()

        total_credits = sum(sc.active_credits for sc in credits if sc.active_credits)

        return {
            'account_id': account.account_id,
            'account_name': account.account_name,
            'territory_id': territory_id,
            'install_base_count': install_base_count,
            'project_count': project_count,
            'active_credits': total_credits
        }
