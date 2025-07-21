import json
from datetime import datetime
from typing import Dict, Any
from .base_agent import BaseAgent
from .data_loader_agent import DataLoaderAgent
from .supplier_analysis_agent import SupplierAnalysisAgent
from .stockout_prediction_agent import StockoutPredictionAgent
from .recommendation_agent import RecommendationAgent
from typing import List

class OrchestratorAgent(BaseAgent):
    def __init__(self):
        super().__init__("Orchestrator")
        self.data_loader = DataLoaderAgent()
        self.supplier_analyzer = SupplierAnalysisAgent()
        self.stockout_predictor = StockoutPredictionAgent()
        self.recommendation_engine = RecommendationAgent()
        self.session_log = []
    
    def log_action(self, agent_name: str, action: str, result_summary: str):
        self.session_log.append({
            'timestamp': datetime.now().isoformat(),
            'agent': agent_name,
            'action': action,
            'result': result_summary
        })
    
    def run_full_analysis(self) -> Dict[str, Any]:
        print("🚀 Starting Intelligent Buying System Analysis...")
        
        # Step 1: Load and prepare data
        print("📊 Loading ERP data...")
        data = self.data_loader.process({})
        self.log_action("DataLoader", "load_data", f"Loaded {len(data['suppliers'])} suppliers, {len(data['inventory'])} inventory items")
        
        # Step 2: Analyze supplier performance
        print("🔍 Analyzing supplier performance...")
        supplier_analysis = self.supplier_analyzer.process(data)
        data.update(supplier_analysis)
        tier1_count = len(supplier_analysis['tier_1_suppliers'])
        self.log_action("SupplierAnalysis", "analyze_performance", f"Classified {tier1_count} Tier 1 suppliers")
        
        # Step 3: Predict stockout risks
        print("⚠️  Predicting stockout risks...")
        stockout_analysis = self.stockout_predictor.process(data)
        data.update(stockout_analysis)
        critical_count = stockout_analysis['summary']['critical_count']
        self.log_action("StockoutPredictor", "predict_risks", f"Identified {critical_count} critical stockout items")
        
        # Step 4: Generate recommendations
        print("💡 Generating procurement recommendations...")
        recommendations = self.recommendation_engine.process(data)
        data.update(recommendations)
        rec_count = len(recommendations['recommendations'])
        self.log_action("RecommendationEngine", "generate_recommendations", f"Created {rec_count} procurement recommendations")
        
        # Step 5: Generate executive dashboard
        print("📈 Preparing executive dashboard...")
        dashboard = self.create_executive_dashboard(data)
        
        print("✅ Analysis complete!")
        return {
            'dashboard': dashboard,
            'detailed_results': data,
            'session_log': self.session_log,
            'metadata': {
                'analysis_timestamp': datetime.now().isoformat(),
                'total_processing_time': len(self.session_log) * 2,  # Simplified
                'data_freshness': 'Real-time'
            }
        }
    
    def create_executive_dashboard(self, data: Dict[str, Any]) -> Dict[str, Any]:
        dashboard = {
            'summary_metrics': {
                'total_suppliers': len(data['suppliers']),
                'tier_1_suppliers': len(data['tier_1_suppliers']),
                'total_inventory_items': len(data['inventory']),
                'critical_stockouts': data['summary']['critical_count'],
                'high_risk_items': data['summary']['high_risk_count'],
                'active_recommendations': len(data['recommendations']),
                'estimated_cost_impact': data['business_impact']['estimated_total_cost'],
                'potential_savings': data['business_impact']['potential_batch_savings']
            },
            'key_alerts': self._generate_key_alerts(data),
            'top_recommendations': data['recommendations'][:5],
            'supplier_performance_summary': self._summarize_supplier_performance(data),
            'roi_projection': self._calculate_roi_projection(data),
            'next_actions': self._generate_next_actions(data)
        }
        
        return dashboard
    
    def _generate_key_alerts(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        alerts = []
        
        # Critical stockout alert
        if data['summary']['critical_count'] > 0:
            alerts.append({
                'type': 'CRITICAL',
                'title': 'Immediate Stockout Risk',
                'message': f"{data['summary']['critical_count']} items are completely out of stock",
                'action_required': 'Expedite orders immediately'
            })
        
        # High-risk supplier alert
        tier3_suppliers = len(data['tier_3_suppliers'])
        if tier3_suppliers > 0:
            alerts.append({
                'type': 'WARNING',
                'title': 'Supplier Performance Issues',
                'message': f"{tier3_suppliers} suppliers are performing below standards",
                'action_required': 'Review supplier contracts and consider alternatives'
            })
        
        # Cost impact alert
        high_cost_items = len([r for r in data['recommendations'] if r['estimated_cost_impact']['cost_premium'] > 1000])
        if high_cost_items > 0:
            alerts.append({
                'type': 'INFO',
                'title': 'High Cost Impact Items',
                'message': f"{high_cost_items} items will require expedited shipping premiums",
                'action_required': 'Consider negotiating expedite rates with suppliers'
            })
        
        return alerts
    
    def _summarize_supplier_performance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        performance_df = data['analyzed_performance']
        
        return {
            'best_performer': {
                'supplier': performance_df.iloc[performance_df['reliability_score'].idxmax()]['supplier_name'],
                'score': performance_df['reliability_score'].max()
            },
            'worst_performer': {
                'supplier': performance_df.iloc[performance_df['reliability_score'].idxmin()]['supplier_name'],
                'score': performance_df['reliability_score'].min()
            },
            'average_reliability': performance_df['reliability_score'].mean().round(2),
            'average_lead_time': performance_df['standard_lead_time_days'].mean().round(1)
        }
    
    def _calculate_roi_projection(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Based on the business case from the image
        annual_savings = {
            'buyer_automation': 36000,  # 1 FTE buyer-equivalent
            'stockout_reduction': 63000,  # Average of $54k-$72k range
            'total_projected': 99000
        }
        
        implementation_cost = len(data['recommendations']) * 100  # Simplified
        
        return {
            'projected_annual_savings': annual_savings,
            'implementation_cost': implementation_cost,
            'payback_period_months': max(1, implementation_cost / (annual_savings['total_projected'] / 12)),
            'roi_percentage': ((annual_savings['total_projected'] - implementation_cost) / implementation_cost * 100)
        }
    
    def _generate_next_actions(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        actions = []
        
        # Immediate actions for critical items
        critical_items = [r for r in data['recommendations'] if r['risk_level'] == 'CRITICAL']
        if critical_items:
            actions.append({
                'priority': 1,
                'action': 'Place emergency orders',
                'details': f"Process {len(critical_items)} critical stockout orders immediately",
                'timeline': 'Today',
                'responsible': 'Procurement Team'
            })
        
        # Supplier optimization
        tier3_count = len(data['tier_3_suppliers'])
        if tier3_count > 0:
            actions.append({
                'priority': 2,
                'action': 'Review underperforming suppliers',
                'details': f"Evaluate {tier3_count} Tier 3 suppliers for contract renegotiation",
                'timeline': 'This week',
                'responsible': 'Supplier Relations'
            })
        
        # Process optimization
        actions.append({
            'priority': 3,
            'action': 'Implement automated monitoring',
            'details': 'Set up daily stockout prediction runs and alerts',
            'timeline': 'Next 2 weeks',
            'responsible': 'IT/Procurement'
        })
        
        return actions
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self.run_full_analysis()
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"buying_system_analysis_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"💾 Results saved to {filename}")
        return filename
