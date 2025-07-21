import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..base_agent import BaseAgent

class NegotiationAgent(BaseAgent):
    """
    Autonomous negotiation agent that can:
    - Negotiate prices with suppliers
    - Optimize contract terms
    - Handle supplier communications
    - Make autonomous decisions within bounds
    """
    
    def __init__(self, message_bus=None):
        super().__init__("AutoNegotiator")
        self.message_bus = message_bus
        self.negotiation_authority = {
            'max_price_increase': 0.15,  # Can accept up to 15% price increase
            'max_lead_time_extension': 7,  # Can accept up to 7 days extension
            'min_order_quantity': 50,  # Minimum order quantity
            'preferred_payment_terms': 30  # Net 30 payment terms
        }
        self.active_negotiations = {}
        self.negotiation_history = []
    
    async def initiate_negotiation(self, supplier_id: str, sku_id: str, 
                                 requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Start autonomous negotiation with supplier"""
        
        negotiation_id = f"NEG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Analyze negotiation position
        position_analysis = await self._analyze_negotiation_position(
            supplier_id, sku_id, requirements
        )
        
        # Prepare negotiation strategy
        strategy = await self._develop_negotiation_strategy(
            supplier_id, position_analysis, requirements
        )
        
        # Start negotiation
        negotiation = {
            'id': negotiation_id,
            'supplier_id': supplier_id,
            'sku_id': sku_id,
            'requirements': requirements,
            'strategy': strategy,
            'status': 'initiated',
            'rounds': [],
            'started_at': datetime.now().isoformat()
        }
        
        self.active_negotiations[negotiation_id] = negotiation
        
        # Send initial offer
        initial_offer = await self._generate_initial_offer(strategy, requirements)
        await self._send_offer_to_supplier(supplier_id, initial_offer, negotiation_id)
        
        return {
            'negotiation_id': negotiation_id,
            'status': 'initiated',
            'initial_offer': initial_offer,
            'expected_outcome': strategy['expected_outcome']
        }
    
    async def _analyze_negotiation_position(self, supplier_id: str, sku_id: str, 
                                          requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze our negotiation position using AI"""
        
        # Get supplier performance data
        from ..data_loader_agent import DataLoaderAgent
        data_loader = DataLoaderAgent()
        supplier_performance = data_loader.get_supplier_performance()
        
        supplier_data = supplier_performance[
            supplier_performance.index == supplier_id
        ].iloc[0] if supplier_id in supplier_performance.index else None
        
        analysis_prompt = f"""
        Analyze our negotiation position for this procurement scenario:
        
        Supplier: {supplier_id}
        SKU: {sku_id}
        Our Requirements: {json.dumps(requirements, indent=2)}
        
        Supplier Performance Data:
        {supplier_data.to_dict() if supplier_data is not None else 'No data available'}
        
        Current Market Context:
        - Urgency Level: {requirements.get('urgency', 'normal')}
        - Order Quantity: {requirements.get('quantity', 'unknown')}
        - Lead Time Requirement: {requirements.get('max_lead_time', 'flexible')}
        
        Provide analysis on:
        1. Our bargaining power (strong/medium/weak)
        2. Supplier's likely position
        3. Key leverage points
        4. Potential concessions we can make
        5. Deal-breaker boundaries
        
        Respond in JSON format with specific recommendations.
        """
        
        try:
            analysis_response = self.llm_call(analysis_prompt)
            # In real implementation, would parse JSON response
            return {
                'bargaining_power': 'medium',
                'key_leverage': ['order_volume', 'long_term_relationship'],
                'supplier_position': 'flexible',
                'recommended_approach': 'collaborative'
            }
        except Exception as e:
            print(f"Analysis error: {e}")
            return {'bargaining_power': 'medium', 'recommended_approach': 'standard'}
    
    async def _develop_negotiation_strategy(self, supplier_id: str, 
                                          position_analysis: Dict[str, Any],
                                          requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Develop AI-powered negotiation strategy"""
        
        strategy_prompt = f"""
        Develop a negotiation strategy based on this analysis:
        
        Position Analysis: {json.dumps(position_analysis, indent=2)}
        Requirements: {json.dumps(requirements, indent=2)}
        Authority Limits: {json.dumps(self.negotiation_authority, indent=2)}
        
        Create a strategy covering:
        1. Opening position (aggressive/moderate/conservative)
        2. Concession sequence (what to give up first)
        3. Walk-away points
        4. Target outcome ranges
        5. Communication tone (firm/collaborative/urgent)
        
        Format as actionable negotiation plan.
        """
        
        try:
            strategy_response = self.llm_call(strategy_prompt)
            return {
                'approach': 'collaborative',
                'opening_position': 'moderate',
                'priority_items': ['price', 'lead_time', 'quality'],
                'concession_sequence': ['payment_terms', 'quantity_flexibility'],
                'target_price_reduction': 0.05,  # 5%
                'expected_outcome': 'win-win agreement'
            }
        except Exception as e:
            print(f"Strategy error: {e}")
            return {'approach': 'standard', 'expected_outcome': 'acceptable_terms'}
    
    async def _generate_initial_offer(self, strategy: Dict[str, Any], 
                                    requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate the initial offer to supplier"""
        
        base_price = requirements.get('target_price', 100.0)
        target_reduction = strategy.get('target_price_reduction', 0.05)
        
        initial_offer = {
            'price_per_unit': base_price * (1 - target_reduction),
            'quantity': requirements.get('quantity', 100),
            'lead_time_required': requirements.get('max_lead_time', 30),
            'payment_terms': self.negotiation_authority['preferred_payment_terms'],
            'quality_requirements': requirements.get('quality_specs', 'standard'),
            'delivery_terms': 'FOB destination',
            'validity_period': '48 hours'
        }
        
        return initial_offer
    
    async def _send_offer_to_supplier(self, supplier_id: str, offer: Dict[str, Any], 
                                    negotiation_id: str):
        """Send offer to supplier (simulated)"""
        
        # In real implementation, this would integrate with supplier portals/APIs
        print(f"📤 Sending offer to {supplier_id}: {offer}")
        
        if self.message_bus:
            await self.message_bus.publish('supplier_communications', {
                'type': 'offer_sent',
                'supplier_id': supplier_id,
                'negotiation_id': negotiation_id,
                'offer': offer,
                'timestamp': datetime.now().isoformat()
            })
    
    async def process_supplier_response(self, negotiation_id: str, 
                                      supplier_response: Dict[str, Any]) -> Dict[str, Any]:
        """Process supplier's counter-offer and decide on response"""
        
        if negotiation_id not in self.active_negotiations:
            return {'error': 'Negotiation not found'}
        
        negotiation = self.active_negotiations[negotiation_id]
        
        # Analyze supplier's response
        analysis = await self._analyze_supplier_response(
            supplier_response, negotiation['strategy'], negotiation['requirements']
        )
        
        # Make autonomous decision
        decision = await self._make_negotiation_decision(analysis, negotiation)
        
        # Record the round
        negotiation['rounds'].append({
            'round_number': len(negotiation['rounds']) + 1,
            'supplier_response': supplier_response,
            'our_analysis': analysis,
            'our_decision': decision,
            'timestamp': datetime.now().isoformat()
        })
        
        if decision['action'] == 'accept':
            negotiation['status'] = 'agreed'
            await self._finalize_agreement(negotiation, supplier_response)
        elif decision['action'] == 'counter':
            await self._send_counter_offer(negotiation, decision['counter_offer'])
        elif decision['action'] == 'reject':
            negotiation['status'] = 'failed'
            await self._terminate_negotiation(negotiation, decision['reason'])
        
        return {
            'negotiation_id': negotiation_id,
            'action_taken': decision['action'],
            'status': negotiation['status'],
            'reasoning': decision.get('reasoning', '')
        }
    
    async def _analyze_supplier_response(self, response: Dict[str, Any], 
                                       strategy: Dict[str, Any],
                                       requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze supplier's counter-offer using AI"""
        
        analysis_prompt = f"""
        Analyze this supplier response to our offer:
        
        Supplier's Counter-offer: {json.dumps(response, indent=2)}
        Our Strategy: {json.dumps(strategy, indent=2)}
        Our Requirements: {json.dumps(requirements, indent=2)}
        Our Authority Limits: {json.dumps(self.negotiation_authority, indent=2)}
        
        Evaluate:
        1. Is this within our acceptable parameters?
        2. What are they prioritizing vs. what we want?
        3. Room for further negotiation?
        4. Risk of walking away vs. accepting
        5. Recommended response (accept/counter/reject)
        
        Provide detailed analysis and recommendation.
        """
        
        try:
            analysis = self.llm_call(analysis_prompt)
            return {
                'within_parameters': True,
                'gap_analysis': 'price_slightly_high',
                'recommendation': 'counter_with_small_adjustment',
                'confidence': 0.8
            }
        except Exception as e:
            return {'recommendation': 'manual_review', 'error': str(e)}
    
    async def _make_negotiation_decision(self, analysis: Dict[str, Any], 
                                       negotiation: Dict[str, Any]) -> Dict[str, Any]:
        """Make autonomous decision on how to respond"""
        
        # Apply business rules and AI recommendations
        if analysis.get('within_parameters', False):
            if analysis.get('recommendation') == 'accept':
                return {
                    'action': 'accept',
                    'reasoning': 'Terms meet our requirements and strategy goals'
                }
            elif analysis.get('recommendation') == 'counter_with_small_adjustment':
                return {
                    'action': 'counter',
                    'counter_offer': self._generate_counter_offer(analysis, negotiation),
                    'reasoning': 'Small adjustment needed to reach optimal terms'
                }
        
        # Default to manual review for complex cases
        return {
            'action': 'escalate',
            'reasoning': 'Requires human review - outside standard parameters'
        }
    
    def _generate_counter_offer(self, analysis: Dict[str, Any], 
                              negotiation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate counter-offer based on analysis"""
        
        # Simplified counter-offer logic
        last_round = negotiation['rounds'][-1] if negotiation['rounds'] else None
        if last_round:
            supplier_offer = last_round['supplier_response']
            # Adjust by small amount
            return {
                'price_per_unit': supplier_offer.get('price_per_unit', 100) * 0.98,
                'lead_time_required': supplier_offer.get('lead_time', 30) - 2,
                'payment_terms': 35,  # Slight concession
                'validity_period': '24 hours'
            }
        
        return {}
    
    async def _finalize_agreement(self, negotiation: Dict[str, Any], 
                                final_terms: Dict[str, Any]):
        """Finalize the negotiated agreement"""
        
        agreement = {
            'negotiation_id': negotiation['id'],
            'supplier_id': negotiation['supplier_id'],
            'sku_id': negotiation['sku_id'],
            'final_terms': final_terms,
            'negotiation_rounds': len(negotiation['rounds']),
            'finalized_at': datetime.now().isoformat()
        }
        
        self.negotiation_history.append(agreement)
        print(f"✅ Agreement finalized: {negotiation['id']}")
        
        if self.message_bus:
            await self.message_bus.publish('agreements', agreement)
    
    def get_active_negotiations(self) -> List[Dict[str, Any]]:
        """Get list of currently active negotiations"""
        return list(self.active_negotiations.values())
    
    def get_negotiation_performance(self) -> Dict[str, Any]:
        """Analyze negotiation performance metrics"""
        
        total_negotiations = len(self.negotiation_history)
        successful = len([n for n in self.negotiation_history if 'final_terms' in n])
        
        return {
            'total_negotiations': total_negotiations,
            'success_rate': successful / total_negotiations if total_negotiations > 0 else 0,
            'average_rounds': sum(n.get('negotiation_rounds', 0) for n in self.negotiation_history) / total_negotiations if total_negotiations > 0 else 0,
            'cost_savings_achieved': 'calculated_based_on_final_terms'  # Would calculate actual savings
        }
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Traditional process method for compatibility"""
        return {
            'active_negotiations': len(self.active_negotiations),
            'negotiation_performance': self.get_negotiation_performance(),
            'authority_limits': self.negotiation_authority
        }
