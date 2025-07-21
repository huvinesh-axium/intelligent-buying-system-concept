import pandas as pd
import numpy as np
from typing import Dict, Any, List
from .base_agent import BaseAgent

class SupplierAnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__("SupplierAnalysis")
    
    def analyze_supplier_reliability(self, performance_df: pd.DataFrame) -> pd.DataFrame:
        # Calculate reliability score based on multiple factors
        performance_df = performance_df.copy()
        
        # Normalize metrics to 0-100 scale
        performance_df['reliability_score'] = (
            (performance_df['on_time_rate'] * 0.4) +  # 40% weight on on-time delivery
            (100 - np.clip(performance_df['avg_delay_days'] * 5, 0, 100)) * 0.3 +  # 30% weight on delay
            (100 - (performance_df['substitutions'] / performance_df['total_orders'] * 100)) * 0.2 +  # 20% weight on substitutions
            (100 - (performance_df['expedited_orders'] / performance_df['total_orders'] * 100)) * 0.1  # 10% weight on expedited orders
        ).round(2)
        
        # Classify suppliers
        def get_tier(score):
            if score >= 80: return "Tier 1"
            elif score >= 60: return "Tier 2"
            else: return "Tier 3"
        
        performance_df['supplier_tier'] = performance_df['reliability_score'].apply(get_tier)
        return performance_df
    
    def find_alternative_suppliers(self, sku_id: str, purchase_orders_df: pd.DataFrame, 
                                 performance_df: pd.DataFrame) -> List[Dict[str, Any]]:
        # Find suppliers who have previously supplied this SKU
        sku_suppliers = purchase_orders_df[
            purchase_orders_df['sku_id'] == sku_id
        ]['supplier_id'].unique()
        
        # Get performance data for these suppliers
        alternatives = []
        for supplier_id in sku_suppliers:
            if supplier_id in performance_df.index:
                supplier_data = performance_df.loc[supplier_id]
                alternatives.append({
                    'supplier_id': supplier_id,
                    'supplier_name': supplier_data['supplier_name'],
                    'reliability_score': supplier_data['reliability_score'],
                    'avg_delay_days': supplier_data['avg_delay_days'],
                    'on_time_rate': supplier_data['on_time_rate'],
                    'standard_lead_time_days': supplier_data['standard_lead_time_days'],
                    'tier': supplier_data['supplier_tier']
                })
        
        # Sort by reliability score
        alternatives.sort(key=lambda x: x['reliability_score'], reverse=True)
        return alternatives
    
    def get_ai_supplier_insights(self, supplier_data: Dict[str, Any]) -> str:
        prompt = f"""
        Analyze this supplier's performance data and provide actionable insights:
        
        Supplier: {supplier_data['supplier_name']} ({supplier_data['supplier_id']})
        Country: {supplier_data['country']}
        Reliability Score: {supplier_data['reliability_score']}/100
        On-time Rate: {supplier_data['on_time_rate']}%
        Average Delay: {supplier_data['avg_delay_days']} days
        Standard Lead Time: {supplier_data['standard_lead_time_days']} days
        Total Orders: {supplier_data['total_orders']}
        Expedited Orders: {supplier_data['expedited_orders']}
        Substitutions: {supplier_data['substitutions']}
        Tier: {supplier_data['supplier_tier']}
        
        Provide a brief analysis (2-3 sentences) focusing on:
        1. Key strengths and weaknesses
        2. Risk factors to consider
        3. Recommendations for future orders
        """
        
        return self.llm_call(prompt)
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        performance_df = data['supplier_performance']
        analyzed_performance = self.analyze_supplier_reliability(performance_df)
        
        # Generate insights for top performers and problematic suppliers
        insights = {}
        top_suppliers = analyzed_performance.nlargest(3, 'reliability_score')
        bottom_suppliers = analyzed_performance.nsmallest(3, 'reliability_score')
        
        for _, supplier in top_suppliers.iterrows():
            insights[f"top_{supplier['supplier_id']}"] = self.get_ai_supplier_insights(supplier.to_dict())
        
        for _, supplier in bottom_suppliers.iterrows():
            insights[f"concern_{supplier['supplier_id']}"] = self.get_ai_supplier_insights(supplier.to_dict())
        
        return {
            'analyzed_performance': analyzed_performance,
            'supplier_insights': insights,
            'tier_1_suppliers': analyzed_performance[analyzed_performance['supplier_tier'] == 'Tier 1'],
            'tier_2_suppliers': analyzed_performance[analyzed_performance['supplier_tier'] == 'Tier 2'],
            'tier_3_suppliers': analyzed_performance[analyzed_performance['supplier_tier'] == 'Tier 3']
        }
