import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
from ..base_agent import BaseAgent
from .message_bus import MessageBus, AgentCommunicationProtocol, KnowledgeBase
from .monitoring_agent import MonitoringAgent
from .negotiation_agent import NegotiationAgent

class AgenticOrchestrator(BaseAgent):
    """
    Enhanced orchestrator with true agentic capabilities:
    - Autonomous decision making
    - Continuous monitoring and adaptation
    - Inter-agent communication and negotiation
    - Learning from outcomes
    - Proactive problem-solving
    """
    
    def __init__(self):
        super().__init__("AgenticOrchestrator")
        
        # Communication infrastructure
        self.message_bus = MessageBus()
        self.knowledge_base = KnowledgeBase()
        self.communication = AgentCommunicationProtocol("AgenticOrchestrator", self.message_bus)
        
        # Enhanced agents
        self.monitoring_agent = MonitoringAgent(self.message_bus)
        self.negotiation_agent = NegotiationAgent(self.message_bus)
        
        # Core agents (existing)
        from ..data_loader_agent import DataLoaderAgent
        from ..supplier_analysis_agent import SupplierAnalysisAgent
        from ..stockout_prediction_agent import StockoutPredictionAgent
        from ..recommendation_agent import RecommendationAgent
        
        self.data_loader = DataLoaderAgent()
        self.supplier_analyzer = SupplierAnalysisAgent()
        self.stockout_predictor = StockoutPredictionAgent()
        self.recommendation_engine = RecommendationAgent()
        
        # Autonomous capabilities
        self.autonomous_mode = True
        self.decision_log = []
        self.learning_data = {}
        self.performance_metrics = {}
        
        # Decision boundaries
        self.decision_authority = {
            'max_order_value': 50000,  # Can autonomously approve orders up to $50k
            'emergency_stockout_threshold': 0,  # Auto-trigger emergency orders when stock = 0
            'supplier_switch_threshold': 60,  # Switch suppliers if score drops below 60
            'negotiation_attempts': 3,  # Max negotiation rounds before escalation
        }
    
    async def start_autonomous_operations(self):
        """Start autonomous mode with continuous monitoring and decision-making"""
        
        print("🤖 Starting Autonomous Intelligent Buying System...")
        print("🔄 Enabling continuous monitoring, learning, and adaptation...")
        
        # Start communication infrastructure
        await self.message_bus.start()
        await self.communication.listen_for_messages()
        
        # Subscribe to alerts and events
        await self.message_bus.subscribe("alerts", self._handle_alert)
        await self.message_bus.subscribe("supplier_communications", self._handle_supplier_communication)
        await self.message_bus.subscribe("agreements", self._handle_negotiation_outcome)
        
        # Start monitoring agent
        monitoring_task = asyncio.create_task(self.monitoring_agent.start_monitoring())
        
        # Start main autonomous loop
        autonomous_task = asyncio.create_task(self._autonomous_decision_loop())
        
        # Start learning and adaptation loop
        learning_task = asyncio.create_task(self._learning_loop())
        
        print("✅ Autonomous operations started!")
        print("🎯 System will now make autonomous procurement decisions within defined boundaries")
        
        return [monitoring_task, autonomous_task, learning_task]
    
    async def _autonomous_decision_loop(self):
        """Main autonomous decision-making loop"""
        
        while self.autonomous_mode:
            try:
                # Analyze current situation
                situation_analysis = await self._analyze_current_situation()
                
                # Make autonomous decisions
                if situation_analysis['requires_action']:
                    decisions = await self._make_autonomous_decisions(situation_analysis)
                    
                    for decision in decisions:
                        await self._execute_autonomous_decision(decision)
                
                # Store situation for learning
                await self.knowledge_base.store_knowledge(
                    f"situation_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    situation_analysis,
                    self.name
                )
                
                # Wait before next analysis cycle
                await asyncio.sleep(30)  # 30 seconds for demo, would be longer in production
                
            except Exception as e:
                print(f"❌ Autonomous loop error: {e}")
                await asyncio.sleep(60)
    
    async def _analyze_current_situation(self) -> Dict[str, Any]:
        """Continuously analyze the current procurement situation"""
        
        # Load current data
        data = self.data_loader.process({})
        
        # Get stockout predictions
        stockout_analysis = self.stockout_predictor.process(data)
        
        # Check for critical situations
        critical_items = stockout_analysis['critical_items']
        high_risk_items = stockout_analysis['stockout_predictions'][
            stockout_analysis['stockout_predictions']['risk_level'].isin(['HIGH', 'CRITICAL'])
        ]
        
        # Analyze supplier performance changes
        supplier_analysis = self.supplier_analyzer.process(data)
        
        situation = {
            'timestamp': datetime.now().isoformat(),
            'critical_stockouts': len(critical_items),
            'high_risk_items': len(high_risk_items),
            'supplier_issues': len(supplier_analysis['tier_3_suppliers']),
            'requires_action': False,
            'urgency_level': 'normal',
            'recommended_actions': []
        }
        
        # Determine if autonomous action is needed
        if len(critical_items) > 0:
            situation['requires_action'] = True
            situation['urgency_level'] = 'critical'
            situation['recommended_actions'].append('emergency_procurement')
        
        elif len(high_risk_items) > 2:
            situation['requires_action'] = True
            situation['urgency_level'] = 'high'
            situation['recommended_actions'].append('preventive_procurement')
        
        return situation
    
    async def _make_autonomous_decisions(self, situation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Make autonomous decisions based on situation analysis"""
        
        decisions = []
        
        if 'emergency_procurement' in situation['recommended_actions']:
            # Generate emergency procurement decisions
            emergency_decisions = await self._generate_emergency_procurement_decisions()
            decisions.extend(emergency_decisions)
        
        if 'preventive_procurement' in situation['recommended_actions']:
            # Generate preventive procurement decisions
            preventive_decisions = await self._generate_preventive_procurement_decisions()
            decisions.extend(preventive_decisions)
        
        # Store decisions for audit trail
        for decision in decisions:
            self.decision_log.append({
                'decision': decision,
                'situation': situation,
                'timestamp': datetime.now().isoformat(),
                'confidence': decision.get('confidence', 0.8)
            })
        
        return decisions
    
    async def _generate_emergency_procurement_decisions(self) -> List[Dict[str, Any]]:
        """Generate emergency procurement decisions for critical stockouts"""
        
        # Get current data and recommendations
        data = self.data_loader.process({})
        stockout_analysis = self.stockout_predictor.process(data)
        supplier_analysis = self.supplier_analyzer.process(data)
        
        # Update data with supplier analysis
        data.update(supplier_analysis)
        data.update(stockout_analysis)
        
        recommendations = self.recommendation_engine.process(data)
        
        decisions = []
        
        for rec in recommendations['recommendations']:
            if rec['risk_level'] == 'CRITICAL':
                # Check if within autonomous authority
                estimated_cost = rec['estimated_cost_impact']['expedited_cost']
                
                if estimated_cost <= self.decision_authority['max_order_value']:
                    # Can make autonomous decision
                    decision = {
                        'type': 'autonomous_emergency_order',
                        'sku_id': rec['sku_id'],
                        'supplier_id': rec['primary_supplier']['supplier_id'] if rec['primary_supplier'] else None,
                        'quantity': rec['recommended_quantity'],
                        'estimated_cost': estimated_cost,
                        'justification': 'Critical stockout - autonomous emergency procurement',
                        'requires_negotiation': estimated_cost > 10000,  # Negotiate if over $10k
                        'confidence': 0.9,
                        'authority_level': 'autonomous'
                    }
                    decisions.append(decision)
                else:
                    # Escalate to human
                    decision = {
                        'type': 'escalate_emergency_order',
                        'sku_id': rec['sku_id'],
                        'reason': f'Cost ${estimated_cost:,.2f} exceeds autonomous authority ${self.decision_authority["max_order_value"]:,.2f}',
                        'confidence': 0.95,
                        'authority_level': 'human_required'
                    }
                    decisions.append(decision)
        
        return decisions
    
    async def _generate_preventive_procurement_decisions(self) -> List[Dict[str, Any]]:
        """Generate preventive procurement decisions for high-risk items"""
        
        decisions = []
        
        # Get recommendations for high-risk items
        data = self.data_loader.process({})
        stockout_analysis = self.stockout_predictor.process(data)
        
        high_risk_items = stockout_analysis['stockout_predictions'][
            stockout_analysis['stockout_predictions']['risk_level'] == 'HIGH'
        ]
        
        for _, item in high_risk_items.iterrows():
            decision = {
                'type': 'autonomous_preventive_order',
                'sku_id': item['sku_id'],
                'recommended_quantity': max(item['reorder_level'], 50),
                'reasoning': f"Preventive order - {item['days_until_stockout']:.1f} days until stockout",
                'requires_supplier_selection': True,
                'confidence': 0.7,
                'authority_level': 'autonomous'
            }
            decisions.append(decision)
        
        return decisions
    
    async def _execute_autonomous_decision(self, decision: Dict[str, Any]):
        """Execute an autonomous decision"""
        
        print(f"🤖 Executing autonomous decision: {decision['type']}")
        
        if decision['type'] == 'autonomous_emergency_order':
            await self._execute_emergency_order(decision)
        elif decision['type'] == 'autonomous_preventive_order':
            await self._execute_preventive_order(decision)
        elif decision['type'] == 'escalate_emergency_order':
            await self._escalate_to_human(decision)
        
        # Record execution
        decision['executed_at'] = datetime.now().isoformat()
        decision['status'] = 'executed'
    
    async def _execute_emergency_order(self, decision: Dict[str, Any]):
        """Execute an emergency order autonomously"""
        
        if decision.get('requires_negotiation', False):
            # Start autonomous negotiation
            negotiation_requirements = {
                'sku_id': decision['sku_id'],
                'quantity': decision['quantity'],
                'urgency': 'emergency',
                'target_price': decision['estimated_cost'] / decision['quantity'],
                'max_lead_time': 7  # Emergency - need within a week
            }
            
            negotiation_result = await self.negotiation_agent.initiate_negotiation(
                decision['supplier_id'],
                decision['sku_id'],
                negotiation_requirements
            )
            
            print(f"🤝 Started autonomous negotiation: {negotiation_result['negotiation_id']}")
        else:
            # Direct order placement (simulated)
            order_details = {
                'order_id': f"AUTO-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'sku_id': decision['sku_id'],
                'supplier_id': decision['supplier_id'],
                'quantity': decision['quantity'],
                'order_type': 'autonomous_emergency',
                'estimated_cost': decision['estimated_cost']
            }
            
            print(f"📦 Autonomous emergency order placed: {order_details['order_id']}")
            
            # Store order in knowledge base
            await self.knowledge_base.store_knowledge(
                f"autonomous_order_{order_details['order_id']}",
                order_details,
                self.name
            )
    
    async def _execute_preventive_order(self, decision: Dict[str, Any]):
        """Execute a preventive order autonomously"""
        
        # Select best supplier autonomously
        if decision.get('requires_supplier_selection'):
            supplier_selection = await self._autonomous_supplier_selection(decision['sku_id'])
            decision['selected_supplier'] = supplier_selection
        
        print(f"📋 Autonomous preventive order scheduled for SKU {decision['sku_id']}")
    
    async def _autonomous_supplier_selection(self, sku_id: str) -> Dict[str, Any]:
        """Autonomously select the best supplier for an SKU"""
        
        # Get supplier performance data
        data = self.data_loader.process({})
        supplier_analysis = self.supplier_analyzer.process(data)
        
        # Use AI to make selection
        selection_prompt = f"""
        Select the optimal supplier for emergency procurement of SKU {sku_id}.
        
        Available suppliers and their performance:
        {supplier_analysis['analyzed_performance'].to_string()}
        
        Consider:
        1. Reliability score and tier
        2. Lead time capabilities
        3. Historical performance with this SKU
        4. Current capacity
        
        Recommend the best supplier and explain reasoning.
        """
        
        ai_recommendation = self.llm_call(selection_prompt)
        
        # For demo, select tier 1 supplier with highest score
        tier1_suppliers = supplier_analysis['tier_1_suppliers']
        if len(tier1_suppliers) > 0:
            best_supplier = tier1_suppliers.loc[tier1_suppliers['reliability_score'].idxmax()]
            return {
                'supplier_id': best_supplier.name,
                'supplier_name': best_supplier['supplier_name'],
                'reliability_score': best_supplier['reliability_score'],
                'reasoning': ai_recommendation
            }
        
        return {'error': 'No suitable suppliers found'}
    
    async def _escalate_to_human(self, decision: Dict[str, Any]):
        """Escalate decision to human operator"""
        
        escalation_alert = {
            'type': 'HUMAN_ESCALATION',
            'decision': decision,
            'reason': decision.get('reason', 'Requires human approval'),
            'urgency': 'HIGH',
            'timestamp': datetime.now().isoformat()
        }
        
        await self.message_bus.publish('escalations', escalation_alert)
        print(f"🚨 Decision escalated to human: {decision['type']}")
    
    async def _learning_loop(self):
        """Continuous learning and adaptation loop"""
        
        while self.autonomous_mode:
            try:
                # Learn from recent decisions and outcomes
                await self._analyze_decision_outcomes()
                
                # Adapt decision boundaries based on learning
                await self._adapt_decision_boundaries()
                
                # Update performance metrics
                await self._update_performance_metrics()
                
                # Sleep between learning cycles
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                print(f"❌ Learning loop error: {e}")
                await asyncio.sleep(600)
    
    async def _analyze_decision_outcomes(self):
        """Analyze outcomes of previous autonomous decisions"""
        
        # Get recent decisions from last 24 hours
        recent_decisions = [
            decision for decision in self.decision_log
            if datetime.fromisoformat(decision['timestamp']) > datetime.now() - timedelta(hours=24)
        ]
        
        if len(recent_decisions) > 0:
            print(f"📊 Analyzing {len(recent_decisions)} recent autonomous decisions...")
            
            # Analyze decision accuracy, cost effectiveness, timing, etc.
            analysis = {
                'total_decisions': len(recent_decisions),
                'average_confidence': sum(d['confidence'] for d in recent_decisions) / len(recent_decisions),
                'decision_types': [d['decision']['type'] for d in recent_decisions]
            }
            
            await self.knowledge_base.store_knowledge(
                "recent_decision_analysis",
                analysis,
                self.name
            )
    
    async def _adapt_decision_boundaries(self):
        """Adapt decision boundaries based on learning"""
        
        # Get performance data
        performance = await self.knowledge_base.retrieve_knowledge("recent_decision_analysis")
        
        if performance and performance['average_confidence'] > 0.85:
            # Increase autonomy if performing well
            self.decision_authority['max_order_value'] = min(
                self.decision_authority['max_order_value'] * 1.1,
                100000  # Cap at $100k
            )
            print(f"📈 Increasing autonomous authority to ${self.decision_authority['max_order_value']:,.2f}")
    
    async def _update_performance_metrics(self):
        """Update system performance metrics"""
        
        self.performance_metrics.update({
            'decisions_made_24h': len([
                d for d in self.decision_log
                if datetime.fromisoformat(d['timestamp']) > datetime.now() - timedelta(hours=24)
            ]),
            'autonomous_authority_level': self.decision_authority['max_order_value'],
            'knowledge_base_size': len(self.knowledge_base.knowledge_store),
            'last_updated': datetime.now().isoformat()
        })
    
    async def _handle_alert(self, alert: Dict[str, Any]):
        """Handle alerts from monitoring agent"""
        
        print(f"🔔 Orchestrator received alert: {alert['type']}")
        
        if alert['type'] == 'CRITICAL_STOCKOUT' and alert['urgency'] == 'IMMEDIATE':
            # Trigger autonomous emergency response
            emergency_decision = {
                'type': 'autonomous_alert_response',
                'trigger': alert,
                'sku_id': alert['sku_id'],
                'response_time': datetime.now().isoformat()
            }
            await self._execute_autonomous_decision(emergency_decision)
    
    async def _handle_supplier_communication(self, communication: Dict[str, Any]):
        """Handle supplier communications"""
        print(f"📞 Supplier communication: {communication['type']}")
    
    async def _handle_negotiation_outcome(self, agreement: Dict[str, Any]):
        """Handle completed negotiations"""
        print(f"🤝 Negotiation completed: {agreement['negotiation_id']}")
        
        # Learn from negotiation outcome
        await self.knowledge_base.store_knowledge(
            f"negotiation_outcome_{agreement['negotiation_id']}",
            agreement,
            self.name
        )
    
    def get_autonomous_status(self) -> Dict[str, Any]:
        """Get current autonomous operation status"""
        
        return {
            'autonomous_mode': self.autonomous_mode,
            'decision_authority': self.decision_authority,
            'decisions_made': len(self.decision_log),
            'performance_metrics': self.performance_metrics,
            'knowledge_base_stats': self.knowledge_base.get_knowledge_stats(),
            'message_bus_stats': self.message_bus.get_stats()
        }
    
    async def stop_autonomous_operations(self):
        """Stop autonomous operations"""
        
        self.autonomous_mode = False
        self.monitoring_agent.stop_monitoring()
        await self.message_bus.stop()
        
        print("🛑 Autonomous operations stopped")
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Traditional process method - now enhanced with autonomous capabilities"""
        
        # Run traditional analysis
        traditional_results = super().process(data)
        
        # Add autonomous operation status
        traditional_results['autonomous_status'] = self.get_autonomous_status()
        
        return traditional_results
