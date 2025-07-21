import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List
from .base_agent import BaseAgent

class StockoutPredictionAgent(BaseAgent):
    def __init__(self):
        super().__init__("StockoutPrediction")
    
    def calculate_velocity(self, sku_id: str, purchase_orders_df: pd.DataFrame, days: int = 30) -> float:
        # Calculate average consumption velocity for an SKU
        recent_orders = purchase_orders_df[
            (purchase_orders_df['sku_id'] == sku_id) & 
            (purchase_orders_df['order_date'] >= datetime.now() - timedelta(days=days))
        ]
        
        if len(recent_orders) == 0:
            return 0.0
        
        total_quantity = recent_orders['quantity_received'].sum()
        return total_quantity / days
    
    def predict_stockout_risk(self, inventory_df: pd.DataFrame, 
                            purchase_orders_df: pd.DataFrame) -> pd.DataFrame:
        predictions = []
        
        for _, item in inventory_df.iterrows():
            sku_id = item['sku_id']
            current_stock = item['stock_quantity']
            reorder_level = item['reorder_level']
            
            # Calculate velocity
            velocity = self.calculate_velocity(sku_id, purchase_orders_df)
            
            # Calculate days until stockout
            if velocity > 0:
                days_until_stockout = current_stock / velocity
            else:
                days_until_stockout = float('inf')
            
            # Calculate risk level
            if current_stock <= 0:
                risk_level = "CRITICAL"
                priority = 1
            elif current_stock <= reorder_level * 0.5:
                risk_level = "HIGH"
                priority = 2
            elif current_stock <= reorder_level:
                risk_level = "MEDIUM"
                priority = 3
            elif days_until_stockout <= 14:
                risk_level = "LOW"
                priority = 4
            else:
                risk_level = "STABLE"
                priority = 5
            
            predictions.append({
                'sku_id': sku_id,
                'current_stock': current_stock,
                'reorder_level': reorder_level,
                'velocity_per_day': round(velocity, 2),
                'days_until_stockout': round(days_until_stockout, 1) if days_until_stockout != float('inf') else None,
                'risk_level': risk_level,
                'priority': priority,
                'recommended_action': self._get_recommended_action(risk_level, days_until_stockout)
            })
        
        return pd.DataFrame(predictions).sort_values('priority')
    
    def _get_recommended_action(self, risk_level: str, days_until_stockout: float) -> str:
        if risk_level == "CRITICAL":
            return "IMMEDIATE ORDER - Stock depleted"
        elif risk_level == "HIGH":
            return "URGENT ORDER - Stock critically low"
        elif risk_level == "MEDIUM":
            return "ORDER SOON - Below reorder level"
        elif risk_level == "LOW":
            return "MONITOR - May need ordering within 2 weeks"
        else:
            return "STABLE - No immediate action needed"
    
    def get_ai_stockout_analysis(self, predictions_df: pd.DataFrame) -> str:
        critical_items = len(predictions_df[predictions_df['risk_level'] == 'CRITICAL'])
        high_risk_items = len(predictions_df[predictions_df['risk_level'] == 'HIGH'])
        medium_risk_items = len(predictions_df[predictions_df['risk_level'] == 'MEDIUM'])
        
        prompt = f"""
        Analyze this inventory stockout situation:
        
        Critical stockouts (0 inventory): {critical_items} items
        High risk (very low stock): {high_risk_items} items  
        Medium risk (below reorder level): {medium_risk_items} items
        
        Top 5 priority items:
        {predictions_df.head().to_string()}
        
        Provide a brief executive summary (3-4 sentences) covering:
        1. Overall inventory health assessment
        2. Immediate actions needed
        3. Resource allocation recommendations
        4. Potential business impact if not addressed
        """
        
        return self.llm_call(prompt)
    
    def identify_substitute_candidates(self, sku_id: str, purchase_orders_df: pd.DataFrame) -> List[str]:
        # Find SKUs that have been used as substitutes for this SKU
        substitution_orders = purchase_orders_df[
            (purchase_orders_df['sku_id'] == sku_id) & 
            (purchase_orders_df['was_substitution'] == True)
        ]
        
        # This is simplified - in real implementation, you'd have product similarity data
        # For now, return SKUs from same category (first 3 digits)
        sku_category = sku_id[:7]  # e.g., "SKU-101" -> "SKU-10"
        category_skus = purchase_orders_df[
            purchase_orders_df['sku_id'].str.startswith(sku_category)
        ]['sku_id'].unique()
        
        return [s for s in category_skus if s != sku_id][:3]  # Return top 3 candidates
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        inventory_df = data['inventory']
        purchase_orders_df = data['purchase_orders']
        
        predictions = self.predict_stockout_risk(inventory_df, purchase_orders_df)
        
        # Get critical and high-risk items
        critical_items = predictions[predictions['risk_level'].isin(['CRITICAL', 'HIGH'])]
        
        # Generate substitution candidates for critical items
        substitution_candidates = {}
        for sku in critical_items['sku_id'].tolist():
            substitution_candidates[sku] = self.identify_substitute_candidates(sku, purchase_orders_df)
        
        # Generate AI analysis
        ai_analysis = self.get_ai_stockout_analysis(predictions)
        
        return {
            'stockout_predictions': predictions,
            'critical_items': critical_items,
            'substitution_candidates': substitution_candidates,
            'ai_analysis': ai_analysis,
            'summary': {
                'total_items': len(predictions),
                'critical_count': len(predictions[predictions['risk_level'] == 'CRITICAL']),
                'high_risk_count': len(predictions[predictions['risk_level'] == 'HIGH']),
                'medium_risk_count': len(predictions[predictions['risk_level'] == 'MEDIUM'])
            }
        }
