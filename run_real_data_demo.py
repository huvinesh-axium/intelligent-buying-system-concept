#!/usr/bin/env python3

import os
import dspy
from dspy import Module, ChainOfThought, Predict
import json
import pandas as pd
from datetime import datetime

# Set up OpenAI API key (you'll need to replace this)
# os.environ['OPENAI_API_KEY'] = 'your-openai-api-key-here'

def load_real_data():
    """Load and process real data from CSV files."""
    # Load real data
    inventory_df = pd.read_csv('data/inventory.csv')
    suppliers_df = pd.read_csv('data/suppliers.csv')
    purchase_orders_df = pd.read_csv('data/purchase_orders.csv')
    
    # Transform data for DSPy system
    inventory_data = []
    for _, item in inventory_df.iterrows():
        # Calculate usage from purchase orders
        item_orders = purchase_orders_df[purchase_orders_df['sku_id'] == item['sku_id']]
        avg_order_size = item_orders['quantity_ordered'].mean() if len(item_orders) > 0 else 100
        
        # Get supplier lead time
        recent_orders = item_orders.tail(1)
        if len(recent_orders) > 0:
            supplier_id = recent_orders.iloc[0]['supplier_id']
            supplier_info = suppliers_df[suppliers_df['supplier_id'] == supplier_id]
            lead_time = supplier_info['standard_lead_time_days'].iloc[0] if len(supplier_info) > 0 else 21
        else:
            lead_time = 21
        
        inventory_data.append({
            'sku': item['sku_id'],
            'stock': item['stock_quantity'],
            'usage': f'Average {int(avg_order_size/4)} units per week based on historical orders',
            'lead_time': f'{lead_time} days',
            'reorder_level': item['reorder_level']
        })
    
    # Process supplier performance
    supplier_performance = {}
    for _, supplier in suppliers_df.iterrows():
        supplier_orders = purchase_orders_df[purchase_orders_df['supplier_id'] == supplier['supplier_id']]
        
        if len(supplier_orders) > 0:
            completed_orders = supplier_orders[supplier_orders['order_status'] == 'Completed']
            on_time_count = 0
            total_completed = len(completed_orders)
            
            for _, order in completed_orders.iterrows():
                if pd.notna(order['actual_delivery_date']) and pd.notna(order['expected_delivery_date']):
                    expected = pd.to_datetime(order['expected_delivery_date'])
                    actual = pd.to_datetime(order['actual_delivery_date'])
                    if actual <= expected:
                        on_time_count += 1
            
            on_time_rate = (on_time_count / total_completed * 100) if total_completed > 0 else 0
            
            supplier_performance[supplier['supplier_id']] = {
                'name': supplier['supplier_name'],
                'country': supplier['country'],
                'lead_time': supplier['standard_lead_time_days'],
                'on_time_rate': f'{on_time_rate:.1f}%',
                'total_orders': len(supplier_orders),
                'completed_orders': total_completed
            }
    
    return {
        'inventory': inventory_data,
        'suppliers': {
            'history': f'Supplier performance data: {json.dumps(supplier_performance, indent=2)}',
            'info': f'Available suppliers: {len(suppliers_df)} with avg lead time {suppliers_df["standard_lead_time_days"].mean():.1f} days'
        },
        'budget': 75000,
        'negotiation_required': True,
        'selected_supplier': 'Best performing supplier based on delivery history',
        'market_conditions': 'Supply chain recovering, lead times stabilizing'
    }

# Configure DSPy with mock LM for demo
class MockLM:
    def __init__(self):
        self.model = "mock-gpt-4o-mini"
        
    def __call__(self, prompt, **kwargs):
        return [{"choices": [{"message": {"content": "Mock response for demo"}}]}]
        
    def generate(self, prompt, **kwargs):
        # Return mock responses based on the signature type
        if "reliability_score" in prompt.lower():
            return ["85", "Late delivery risk, quality concerns"]
        elif "stockout_probability" in prompt.lower():
            return ["High - 85%", "3-5 days"]
        elif "recommended_order" in prompt.lower():
            return ["Order 200 units SKU-102 and 150 units SKU-201 from SUP-02 and SUP-06", 
                   "Critical stockout items need immediate attention. SUP-02 and SUP-06 have best on-time performance."]
        return ["Mock response"]

# DSPy Signatures
class SupplierEvaluation(dspy.Signature):
    """Evaluate supplier reliability based on historical performance."""
    order_history = dspy.InputField(desc="Past orders from supplier")
    supplier_info = dspy.InputField(desc="Supplier details")
    reliability_score = dspy.OutputField(desc="Score 0-100")
    risk_factors = dspy.OutputField(desc="Key risks identified")

class StockoutPrediction(dspy.Signature):
    """Predict stockout risk for inventory items."""
    current_stock = dspy.InputField()
    consumption_pattern = dspy.InputField()
    lead_time = dspy.InputField()
    stockout_probability = dspy.OutputField()
    days_until_stockout = dspy.OutputField()

class PurchaseRecommendation(dspy.Signature):
    """Generate optimal purchase recommendations."""
    stockout_risk = dspy.InputField()
    supplier_scores = dspy.InputField()
    budget_constraints = dspy.InputField()
    recommended_order = dspy.OutputField()
    justification = dspy.OutputField()

# DSPy Agents
class DSPySupplierAgent(Module):
    def __init__(self):
        super().__init__()
        self.evaluate = ChainOfThought(SupplierEvaluation)
        
    def forward(self, supplier_data):
        return self.evaluate(
            order_history=supplier_data['history'],
            supplier_info=supplier_data['info']
        )

class DSPyStockoutAgent(Module):
    def __init__(self):
        super().__init__()
        self.predict = Predict(StockoutPrediction)
        
    def forward(self, inventory_data):
        predictions = []
        critical_items = []
        
        for sku in inventory_data:
            pred = self.predict(
                current_stock=str(sku['stock']),
                consumption_pattern=str(sku['usage']),
                lead_time=str(sku['lead_time'])
            )
            predictions.append({
                'sku': sku['sku'],
                'stock': sku['stock'],
                'reorder_level': sku['reorder_level'],
                'prediction': pred
            })
            
            # Identify critical items
            if sku['stock'] <= sku['reorder_level']:
                critical_items.append(sku['sku'])
        
        return {
            'predictions': predictions,
            'critical_items': critical_items,
            'summary': f"Found {len(critical_items)} critical items needing immediate attention"
        }

class DSPyRecommendationAgent(Module):
    def __init__(self):
        super().__init__()
        self.recommend = ChainOfThought(PurchaseRecommendation)
        
    def forward(self, context):
        return self.recommend(**context)

class DSPyBuyingSystemOrchestrator(Module):
    def __init__(self):
        super().__init__()
        self.supplier_agent = DSPySupplierAgent()
        self.stockout_agent = DSPyStockoutAgent()
        self.recommendation_agent = DSPyRecommendationAgent()
        
    def forward(self, system_state):
        print("🔍 Analyzing suppliers...")
        supplier_scores = self.supplier_agent(system_state['suppliers'])
        
        print("📊 Predicting stockout risks...")
        stockout_risks = self.stockout_agent(system_state['inventory'])
        
        print("💡 Generating purchase recommendations...")
        
        # Aggregate insights
        context = {
            'stockout_risk': str(stockout_risks),
            'supplier_scores': str(supplier_scores),
            'budget_constraints': str(system_state['budget'])
        }
        
        # Generate recommendations
        recommendations = self.recommendation_agent(context)
        
        return {
            'supplier_analysis': supplier_scores,
            'stockout_analysis': stockout_risks,
            'recommendations': recommendations
        }

def run_demo_with_real_data():
    """Run the DSPy buying system demo with real data."""
    print("🚀 Starting DSPy Intelligent Buying System Demo with Real Data")
    print("=" * 60)
    
    # Configure DSPy with mock LM for demo purposes
    lm = dspy.LM(model="gpt-4o", base_url="https://api.openai.com/v1", api_key=os.environ["OPENAI_API_KEY"])
    dspy.settings.configure(lm=lm)
    
    # Load real data
    print("📁 Loading real inventory and supplier data...")
    system_state = load_real_data()
    
    # Show critical inventory status
    critical_items = []
    for item in system_state['inventory']:
        if item['stock'] <= item['reorder_level']:
            critical_items.append(item)
    
    print(f"\n⚠️  CRITICAL INVENTORY ALERT: {len(critical_items)} items at or below reorder level:")
    for item in critical_items:
        print(f"   • {item['sku']}: {item['stock']} units (reorder at {item['reorder_level']})")
    
    # Initialize and run the system
    print(f"\n🤖 Initializing multi-agent system...")
    orchestrator = DSPyBuyingSystemOrchestrator()
    
    print("🔄 Running intelligent buying system analysis...")
    try:
        result = orchestrator(system_state)
        
        print("\n" + "="*60)
        print("📋 INTELLIGENT BUYING SYSTEM RESULTS")
        print("="*60)
        
        print(f"\n🏆 SUPPLIER ANALYSIS:")
        print(f"   Reliability Score: {result['supplier_analysis'].reliability_score}")
        print(f"   Risk Factors: {result['supplier_analysis'].risk_factors}")
        
        print(f"\n📈 STOCKOUT ANALYSIS:")
        print(f"   {result['stockout_analysis']['summary']}")
        print(f"   Critical SKUs: {', '.join(result['stockout_analysis']['critical_items'])}")
        
        print(f"\n💰 PURCHASE RECOMMENDATIONS:")
        print(f"   Order: {result['recommendations'].recommended_order}")
        print(f"   Justification: {result['recommendations'].justification}")
        print(f"   Budget Available: ${system_state['budget']:,}")
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f"real_data_analysis_{timestamp}.json"
        
        output_data = {
            'timestamp': datetime.now().isoformat(),
            'critical_items_count': len(critical_items),
            'critical_items': [item['sku'] for item in critical_items],
            'supplier_reliability': result['supplier_analysis'].reliability_score,
            'recommendations': result['recommendations'].recommended_order,
            'justification': result['recommendations'].justification,
            'budget': system_state['budget']
        }
        
        with open(results_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\n💾 Results saved to: {results_file}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error running system: {e}")
        return None

if __name__ == "__main__":
    run_demo_with_real_data()
