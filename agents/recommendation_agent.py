import pandas as pd
import numpy as np
from typing import Dict, Any, List
from .base_agent import BaseAgent

class RecommendationAgent(BaseAgent):
    def __init__(self):
        super().__init__("Recommendation")
    
    def generate_supplier_recommendations(self, 
                                        critical_items: pd.DataFrame,
                                        supplier_performance: pd.DataFrame,
                                        substitution_candidates: Dict[str, List[str]],
                                        purchase_orders_df: pd.DataFrame) -> List[Dict[str, Any]]:
        recommendations = []
        
        for _, item in critical_items.iterrows():
            sku_id = item['sku_id']
            risk_level = item['risk_level']
            
            # Get historical suppliers for this SKU
            sku_suppliers = purchase_orders_df[
                purchase_orders_df['sku_id'] == sku_id
            ]['supplier_id'].unique()
            
            # Rank suppliers by performance
            available_suppliers = []
            for supplier_id in sku_suppliers:
                if supplier_id in supplier_performance.index:
                    supplier_data = supplier_performance.loc[supplier_id]
                    available_suppliers.append({
                        'supplier_id': supplier_id,
                        'supplier_name': supplier_data['supplier_name'],
                        'reliability_score': supplier_data['reliability_score'],
                        'lead_time': supplier_data['standard_lead_time_days'],
                        'tier': supplier_data['supplier_tier']
                    })
            
            # Sort by reliability score
            available_suppliers.sort(key=lambda x: x['reliability_score'], reverse=True)
            
            # Calculate recommended order quantity
            recommended_qty = max(item['reorder_level'] * 2, 100)  # Simple logic
            
            recommendation = {
                'sku_id': sku_id,
                'risk_level': risk_level,
                'current_stock': item['current_stock'],
                'days_until_stockout': item['days_until_stockout'],
                'recommended_quantity': recommended_qty,
                'primary_supplier': available_suppliers[0] if available_suppliers else None,
                'alternative_suppliers': available_suppliers[1:3] if len(available_suppliers) > 1 else [],
                'substitution_options': substitution_candidates.get(sku_id, []),
                'urgency_score': self._calculate_urgency_score(item),
                'estimated_cost_impact': self._estimate_cost_impact(risk_level, recommended_qty),
                'ai_reasoning': self._get_ai_recommendation_reasoning(item, available_suppliers)
            }
            
            recommendations.append(recommendation)
        
        # Sort by urgency score
        recommendations.sort(key=lambda x: x['urgency_score'], reverse=True)
        return recommendations
    
    def _calculate_urgency_score(self, item: pd.Series) -> int:
        # Calculate urgency based on risk level and days until stockout
        risk_weights = {
            'CRITICAL': 100,
            'HIGH': 80,
            'MEDIUM': 60,
            'LOW': 40
        }
        
        base_score = risk_weights.get(item['risk_level'], 20)
        
        # Adjust based on days until stockout
        if pd.notna(item['days_until_stockout']):
            if item['days_until_stockout'] <= 3:
                base_score += 20
            elif item['days_until_stockout'] <= 7:
                base_score += 10
            elif item['days_until_stockout'] <= 14:
                base_score += 5
        
        return min(base_score, 100)
    
    def _estimate_cost_impact(self, risk_level: str, quantity: int) -> Dict[str, float]:
        # Simplified cost impact estimation
        base_cost_per_unit = 50.0  # Placeholder
        
        expedite_multiplier = {
            'CRITICAL': 2.5,
            'HIGH': 1.8,
            'MEDIUM': 1.2,
            'LOW': 1.0
        }
        
        normal_cost = quantity * base_cost_per_unit
        expedited_cost = normal_cost * expedite_multiplier.get(risk_level, 1.0)
        
        return {
            'normal_order_cost': normal_cost,
            'expedited_cost': expedited_cost,
            'cost_premium': expedited_cost - normal_cost,
            'stockout_risk_cost': quantity * base_cost_per_unit * 0.3  # 30% markup for stockout risk
        }
    
    def _get_ai_recommendation_reasoning(self, item: pd.Series, suppliers: List[Dict]) -> str:
        primary_supplier = suppliers[0] if suppliers else {'supplier_name': 'No supplier data'}
        
        prompt = f"""
        Provide a concise procurement recommendation for this situation:
        
        SKU: {item['sku_id']}
        Risk Level: {item['risk_level']}
        Current Stock: {item['current_stock']}
        Days Until Stockout: {item.get('days_until_stockout', 'Unknown')}
        Recommended Primary Supplier: {primary_supplier['supplier_name']}
        Supplier Reliability: {primary_supplier.get('reliability_score', 'Unknown')}/100
        
        In 2-3 sentences, explain:
        1. Why this order should be prioritized
        2. Key considerations for supplier selection
        3. Risk mitigation approach
        """
        
        return self.llm_call(prompt)
    
    def optimize_order_batching(self, recommendations: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        # Group recommendations by supplier for efficient batching
        supplier_batches = {}
        
        for rec in recommendations:
            if rec['primary_supplier']:
                supplier_id = rec['primary_supplier']['supplier_id']
                if supplier_id not in supplier_batches:
                    supplier_batches[supplier_id] = []
                supplier_batches[supplier_id].append(rec)
        
        # Optimize batches by lead time and urgency
        optimized_batches = {}
        for supplier_id, orders in supplier_batches.items():
            # Sort by urgency and group by timing requirements
            orders.sort(key=lambda x: x['urgency_score'], reverse=True)
            
            urgent_batch = [o for o in orders if o['urgency_score'] >= 80]
            standard_batch = [o for o in orders if o['urgency_score'] < 80]
            
            optimized_batches[supplier_id] = {
                'urgent_orders': urgent_batch,
                'standard_orders': standard_batch,
                'total_orders': len(orders),
                'estimated_savings': len(orders) * 50  # Simplified savings calculation
            }
        
        return optimized_batches
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        critical_items = data['critical_items']
        supplier_performance = data['analyzed_performance']
        substitution_candidates = data['substitution_candidates']
        purchase_orders_df = data['purchase_orders']
        
        # Generate recommendations
        recommendations = self.generate_supplier_recommendations(
            critical_items, supplier_performance, substitution_candidates, purchase_orders_df
        )
        
        # Optimize order batching
        optimized_batches = self.optimize_order_batching(recommendations)
        
        # Calculate business impact
        total_cost_impact = sum(r['estimated_cost_impact']['expedited_cost'] for r in recommendations)
        potential_savings = sum(batch['estimated_savings'] for batch in optimized_batches.values())
        
        return {
            'recommendations': recommendations,
            'optimized_batches': optimized_batches,
            'business_impact': {
                'total_items_requiring_action': len(recommendations),
                'estimated_total_cost': total_cost_impact,
                'potential_batch_savings': potential_savings,
                'high_urgency_items': len([r for r in recommendations if r['urgency_score'] >= 80]),
                'suppliers_involved': len(optimized_batches)
            },
            'executive_summary': self._generate_executive_summary(recommendations, total_cost_impact)
        }
    
    def _generate_executive_summary(self, recommendations: List[Dict], total_cost: float) -> str:
        high_urgency = len([r for r in recommendations if r['urgency_score'] >= 80])
        
        prompt = f"""
        Generate an executive summary for procurement recommendations:
        
        Total items requiring immediate action: {len(recommendations)}
        High urgency items: {high_urgency}
        Estimated total procurement cost: ${total_cost:,.2f}
        
        Top 3 most urgent items:
        {[r['sku_id'] + ' (' + r['risk_level'] + ')' for r in recommendations[:3]]}
        
        Provide a brief executive summary (3-4 sentences) covering:
        1. Overall situation assessment
        2. Financial impact and risk
        3. Recommended immediate actions
        4. Expected timeline for resolution
        """
        
        return self.llm_call(prompt)
