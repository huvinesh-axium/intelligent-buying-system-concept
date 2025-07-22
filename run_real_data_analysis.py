#!/usr/bin/env python3

import os
import json
import pandas as pd
from datetime import datetime

def analyze_real_data():
    """Analyze real data and provide intelligent buying recommendations."""
    print("🚀 Starting Intelligent Buying System Analysis with Real Data")
    print("=" * 60)
    
    # Load real data
    print("📁 Loading real inventory and supplier data...")
    inventory_df = pd.read_csv('data/inventory.csv')
    suppliers_df = pd.read_csv('data/suppliers.csv')
    purchase_orders_df = pd.read_csv('data/purchase_orders.csv')
    
    print("\n📊 DATA SUMMARY:")
    print(f"   • Inventory items: {len(inventory_df)}")
    print(f"   • Suppliers: {len(suppliers_df)}")
    print(f"   • Historical orders: {len(purchase_orders_df)}")
    
    # Critical inventory analysis
    critical_items = inventory_df[inventory_df['stock_quantity'] <= inventory_df['reorder_level']]
    print(f"\n⚠️  CRITICAL INVENTORY ALERT: {len(critical_items)} items at or below reorder level:")
    
    urgent_orders = []
    for _, item in critical_items.iterrows():
        shortage = item['reorder_level'] - item['stock_quantity']
        if shortage > 0:
            shortage += item['reorder_level']  # Safety stock
        else:
            shortage = item['reorder_level']
        
        print(f"   • {item['sku_id']}: {item['stock_quantity']} units (reorder at {item['reorder_level']}) - Need {shortage} units")
        urgent_orders.append({
            'sku': item['sku_id'],
            'current_stock': item['stock_quantity'],
            'reorder_level': item['reorder_level'],
            'needed_quantity': shortage
        })
    
    # Supplier performance analysis
    print(f"\n🏆 SUPPLIER PERFORMANCE ANALYSIS:")
    supplier_performance = {}
    
    for _, supplier in suppliers_df.iterrows():
        supplier_orders = purchase_orders_df[purchase_orders_df['supplier_id'] == supplier['supplier_id']]
        
        if len(supplier_orders) > 0:
            completed_orders = supplier_orders[supplier_orders['order_status'] == 'Completed']
            on_time_deliveries = 0
            total_completed = len(completed_orders)
            
            for _, order in completed_orders.iterrows():
                if pd.notna(order['actual_delivery_date']) and pd.notna(order['expected_delivery_date']):
                    expected = pd.to_datetime(order['expected_delivery_date'])
                    actual = pd.to_datetime(order['actual_delivery_date'])
                    if actual <= expected:
                        on_time_deliveries += 1
            
            on_time_rate = (on_time_deliveries / total_completed * 100) if total_completed > 0 else 0
            avg_delay = 0
            
            # Calculate average delay
            delays = []
            for _, order in completed_orders.iterrows():
                if pd.notna(order['actual_delivery_date']) and pd.notna(order['expected_delivery_date']):
                    expected = pd.to_datetime(order['expected_delivery_date'])
                    actual = pd.to_datetime(order['actual_delivery_date'])
                    delay_days = (actual - expected).days
                    delays.append(delay_days)
            
            avg_delay = sum(delays) / len(delays) if delays else 0
            
            supplier_performance[supplier['supplier_id']] = {
                'name': supplier['supplier_name'],
                'country': supplier['country'],
                'lead_time': supplier['standard_lead_time_days'],
                'on_time_rate': on_time_rate,
                'total_orders': len(supplier_orders),
                'completed_orders': total_completed,
                'avg_delay_days': avg_delay
            }
            
            print(f"   • {supplier['supplier_name']} ({supplier['country']}): {on_time_rate:.1f}% on-time, {supplier['standard_lead_time_days']} days lead time")
    
    # Smart recommendations
    print(f"\n💡 INTELLIGENT BUYING RECOMMENDATIONS:")
    
    # Find best suppliers
    best_suppliers = sorted(
        supplier_performance.items(), 
        key=lambda x: (x[1]['on_time_rate'], -x[1]['lead_time']), 
        reverse=True
    )[:3]
    
    print(f"   🥇 Top performing suppliers:")
    for i, (sup_id, perf) in enumerate(best_suppliers, 1):
        print(f"      {i}. {perf['name']}: {perf['on_time_rate']:.1f}% on-time, {perf['lead_time']} days lead time")
    
    # Generate purchase recommendations
    budget = 75000
    total_estimated_cost = 0
    recommendations = []
    
    print(f"\n💰 PURCHASE RECOMMENDATIONS (Budget: ${budget:,}):")
    
    for item in urgent_orders:
        # Estimate cost (assuming $10-50 per unit based on SKU)
        if 'SKU-1' in item['sku']:
            unit_cost = 25  # Higher cost items
        elif 'SKU-2' in item['sku']:
            unit_cost = 35  # Premium items
        else:
            unit_cost = 20  # Standard items
        
        item_cost = item['needed_quantity'] * unit_cost
        total_estimated_cost += item_cost
        
        # Recommend best supplier for this item
        best_supplier = best_suppliers[0][1] if best_suppliers else {'name': 'Best Available', 'lead_time': 20}
        
        recommendations.append({
            'sku': item['sku'],
            'quantity': item['needed_quantity'],
            'estimated_cost': item_cost,
            'recommended_supplier': best_supplier['name'],
            'lead_time': best_supplier.get('lead_time', 20)
        })
        
        print(f"   • {item['sku']}: Order {item['needed_quantity']} units from {best_supplier['name']} (~${item_cost:,})")
    
    print(f"\n📈 FINANCIAL SUMMARY:")
    print(f"   • Total estimated cost: ${total_estimated_cost:,}")
    print(f"   • Budget remaining: ${budget - total_estimated_cost:,}")
    print(f"   • Budget utilization: {(total_estimated_cost/budget)*100:.1f}%")
    
    if total_estimated_cost > budget:
        print(f"   ⚠️  WARNING: Estimated cost exceeds budget by ${total_estimated_cost - budget:,}")
        print(f"   💡 SUGGESTION: Prioritize SKU-102 and SKU-201 (zero stock items)")
    
    # Risk assessment
    print(f"\n🎯 RISK ASSESSMENT:")
    high_risk_items = [item for item in urgent_orders if item['current_stock'] == 0]
    medium_risk_items = [item for item in urgent_orders if item['current_stock'] > 0 and item['current_stock'] <= item['reorder_level']]
    
    print(f"   🔴 HIGH RISK (Zero stock): {len(high_risk_items)} items - {', '.join([item['sku'] for item in high_risk_items])}")
    print(f"   🟡 MEDIUM RISK (Below reorder): {len(medium_risk_items)} items - {', '.join([item['sku'] for item in medium_risk_items])}")
    
    # Timeline analysis
    print(f"\n⏰ DELIVERY TIMELINE:")
    for rec in recommendations[:3]:  # Show top 3
        delivery_date = pd.Timestamp.now() + pd.Timedelta(days=rec['lead_time'])
        print(f"   • {rec['sku']}: Expected delivery {delivery_date.strftime('%Y-%m-%d')} ({rec['lead_time']} days)")
    
    # Save analysis results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = f"buying_analysis_{timestamp}.json"
    
    analysis_results = {
        'timestamp': datetime.now().isoformat(),
        'critical_items_count': len(urgent_orders),
        'total_estimated_cost': total_estimated_cost,
        'budget': budget,
        'budget_utilization_pct': (total_estimated_cost/budget)*100,
        'high_risk_items': len(high_risk_items),
        'recommendations': recommendations,
        'supplier_performance': supplier_performance,
        'top_suppliers': [{'id': sup_id, **perf} for sup_id, perf in best_suppliers]
    }
    
    with open(results_file, 'w') as f:
        json.dump(analysis_results, f, indent=2)
    
    print(f"\n💾 Analysis saved to: {results_file}")
    
    return analysis_results

if __name__ == "__main__":
    analyze_real_data()
