import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Callable, List
from ..base_agent import BaseAgent

class MonitoringAgent(BaseAgent):
    """
    Autonomous monitoring agent that continuously watches for:
    - Inventory level changes
    - Supplier performance deviations
    - Market condition changes
    - System anomalies
    """
    
    def __init__(self, message_bus=None):
        super().__init__("ContinuousMonitor")
        self.message_bus = message_bus
        self.monitoring_active = False
        self.alert_thresholds = {
            'critical_stock_level': 0,
            'supplier_score_drop': 10,
            'order_delay_threshold': 3,  # days
            'cost_spike_threshold': 0.2  # 20% increase
        }
        self.last_check = {}
        self.trend_data = {}
    
    async def start_monitoring(self):
        """Start continuous monitoring loop"""
        self.monitoring_active = True
        print("🔍 Monitoring Agent: Starting continuous surveillance...")
        
        while self.monitoring_active:
            try:
                await self._check_inventory_levels()
                await self._monitor_supplier_performance()
                await self._detect_anomalies()
                await self._predict_future_issues()
                
                # Sleep for monitoring interval (5 minutes in production)
                await asyncio.sleep(10)  # 10 seconds for demo
                
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                await asyncio.sleep(30)
    
    async def _check_inventory_levels(self):
        """Proactively check for inventory issues"""
        from ..data_loader_agent import DataLoaderAgent
        
        data_loader = DataLoaderAgent()
        inventory = data_loader.load_inventory()
        
        for _, item in inventory.iterrows():
            sku_id = item['sku_id']
            current_stock = item['stock_quantity']
            reorder_level = item['reorder_level']
            
            # Detect critical situations
            if current_stock == 0 and sku_id not in self.last_check.get('critical_alerts', set()):
                await self._send_alert({
                    'type': 'CRITICAL_STOCKOUT',
                    'sku_id': sku_id,
                    'message': f"SKU {sku_id} is completely out of stock!",
                    'urgency': 'IMMEDIATE',
                    'suggested_action': 'place_emergency_order'
                })
                self.last_check.setdefault('critical_alerts', set()).add(sku_id)
            
            # Predict upcoming stockouts
            elif current_stock <= reorder_level * 0.8:
                velocity = self._calculate_consumption_velocity(sku_id)
                if velocity > 0:
                    days_left = current_stock / velocity
                    if days_left <= 7:  # Will run out in a week
                        await self._send_alert({
                            'type': 'PREDICTED_STOCKOUT',
                            'sku_id': sku_id,
                            'message': f"SKU {sku_id} will run out in {days_left:.1f} days",
                            'urgency': 'HIGH',
                            'suggested_action': 'schedule_reorder'
                        })
    
    async def _monitor_supplier_performance(self):
        """Continuously monitor supplier performance changes"""
        from ..supplier_analysis_agent import SupplierAnalysisAgent
        from ..data_loader_agent import DataLoaderAgent
        
        data_loader = DataLoaderAgent()
        supplier_analyzer = SupplierAnalysisAgent()
        
        current_performance = supplier_analyzer.analyze_supplier_reliability(
            data_loader.get_supplier_performance()
        )
        
        # Check for performance degradation
        for _, supplier in current_performance.iterrows():
            supplier_id = supplier['supplier_id']
            current_score = supplier['reliability_score']
            
            if supplier_id in self.trend_data:
                last_score = self.trend_data[supplier_id]['last_score']
                score_change = current_score - last_score
                
                if score_change <= -self.alert_thresholds['supplier_score_drop']:
                    await self._send_alert({
                        'type': 'SUPPLIER_DEGRADATION',
                        'supplier_id': supplier_id,
                        'message': f"Supplier {supplier['supplier_name']} score dropped by {abs(score_change):.1f} points",
                        'urgency': 'MEDIUM',
                        'suggested_action': 'review_supplier_contract'
                    })
            
            # Update trend data
            self.trend_data[supplier_id] = {
                'last_score': current_score,
                'last_updated': datetime.now()
            }
    
    async def _detect_anomalies(self):
        """Detect unusual patterns in the data"""
        # Check for unusual order patterns, cost spikes, etc.
        pass
    
    async def _predict_future_issues(self):
        """Use AI to predict potential future problems"""
        trend_summary = self._summarize_trends()
        
        if trend_summary:
            prediction_prompt = f"""
            Based on these supply chain trends, predict potential issues in the next 30 days:
            
            {trend_summary}
            
            Identify:
            1. Likely stockout risks
            2. Supplier performance concerns
            3. Cost optimization opportunities
            4. Recommended preventive actions
            
            Format as JSON with risk_level, description, and recommended_action.
            """
            
            try:
                prediction = self.llm_call(prediction_prompt)
                await self._send_alert({
                    'type': 'PREDICTIVE_INSIGHT',
                    'message': 'AI-powered future risk prediction available',
                    'details': prediction,
                    'urgency': 'LOW',
                    'suggested_action': 'review_predictions'
                })
            except Exception as e:
                print(f"Prediction error: {e}")
    
    def _calculate_consumption_velocity(self, sku_id: str) -> float:
        """Calculate recent consumption velocity for SKU"""
        # Simplified - in real implementation would use historical consumption data
        return 2.5  # units per day
    
    def _summarize_trends(self) -> str:
        """Summarize current trends for AI analysis"""
        if not self.trend_data:
            return ""
        
        summary = "Recent supplier performance trends:\n"
        for supplier_id, data in self.trend_data.items():
            summary += f"- {supplier_id}: Score {data['last_score']:.1f}\n"
        
        return summary
    
    async def _send_alert(self, alert: Dict[str, Any]):
        """Send alert to message bus for other agents to process"""
        alert['timestamp'] = datetime.now().isoformat()
        alert['source_agent'] = self.name
        
        print(f"🚨 ALERT: {alert['type']} - {alert['message']}")
        
        if self.message_bus:
            await self.message_bus.publish('alerts', alert)
    
    def stop_monitoring(self):
        """Stop the monitoring loop"""
        self.monitoring_active = False
        print("🛑 Monitoring Agent: Surveillance stopped")
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Traditional process method for compatibility"""
        return {
            'monitoring_status': 'active' if self.monitoring_active else 'inactive',
            'alert_thresholds': self.alert_thresholds,
            'trend_data': self.trend_data
        }
