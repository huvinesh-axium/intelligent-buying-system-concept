#!/usr/bin/env python3
"""
Intelligent Buying System - Multi-Agent Procurement Optimization
Elush Retail Use Case Implementation

This system enhances buying decision-making by leveraging AI agents to:
- Recommend optimal suppliers based on historical performance
- Predict and prevent stockouts
- Suggest substitute products when needed
- Optimize order batching and procurement costs

Expected Annual ROI: $90,000 - $108,000
"""

import os
from dotenv import load_dotenv
from agents.orchestrator_agent import OrchestratorAgent

def main():
    # Load environment variables
    load_dotenv()
    
    # Verify HF token is available
    if not os.environ.get("HF_TOKEN"):
        print("❌ Error: HF_TOKEN environment variable not set")
        print("Please set your Hugging Face token in the .env file")
        return
    
    print("=" * 60)
    print("🏢 ELUSH RETAIL - INTELLIGENT BUYING SYSTEM")
    print("=" * 60)
    print("AI-Powered Procurement Decision Support")
    print("Expected Annual ROI: $90,000 - $108,000")
    print("=" * 60)
    
    try:
        # Initialize the orchestrator
        orchestrator = OrchestratorAgent()
        
        # Run the full analysis
        results = orchestrator.run_full_analysis()
        
        # Display executive summary
        print("\n" + "=" * 60)
        print("📈 EXECUTIVE DASHBOARD")
        print("=" * 60)
        
        dashboard = results['dashboard']
        metrics = dashboard['summary_metrics']
        
        print(f"📊 Total Suppliers: {metrics['total_suppliers']}")
        print(f"⭐ Tier 1 Suppliers: {metrics['tier_1_suppliers']}")
        print(f"📦 Inventory Items: {metrics['total_inventory_items']}")
        print(f"🚨 Critical Stockouts: {metrics['critical_stockouts']}")
        print(f"⚠️  High Risk Items: {metrics['high_risk_items']}")
        print(f"💡 Active Recommendations: {metrics['active_recommendations']}")
        print(f"💰 Estimated Cost Impact: ${metrics['estimated_cost_impact']:,.2f}")
        print(f"💵 Potential Savings: ${metrics['potential_savings']:,.2f}")
        
        # Display key alerts
        print("\n🚨 KEY ALERTS:")
        for alert in dashboard['key_alerts']:
            icon = "🔴" if alert['type'] == 'CRITICAL' else "🟡" if alert['type'] == 'WARNING' else "🔵"
            print(f"{icon} {alert['title']}: {alert['message']}")
            print(f"   Action: {alert['action_required']}")
        
        # Display top recommendations
        print("\n💡 TOP PROCUREMENT RECOMMENDATIONS:")
        for i, rec in enumerate(dashboard['top_recommendations'], 1):
            print(f"{i}. SKU {rec['sku_id']} - {rec['risk_level']} Risk")
            if rec['primary_supplier']:
                print(f"   Recommended Supplier: {rec['primary_supplier']['supplier_name']}")
                print(f"   Reliability Score: {rec['primary_supplier']['reliability_score']}/100")
            print(f"   Quantity: {rec['recommended_quantity']} units")
            print(f"   Urgency Score: {rec['urgency_score']}/100")
        
        # Display ROI projection
        print("\n📈 ROI PROJECTION:")
        roi = dashboard['roi_projection']
        print(f"💰 Projected Annual Savings: ${roi['projected_annual_savings']['total_projected']:,}")
        print(f"🏗️  Implementation Cost: ${roi['implementation_cost']:,}")
        print(f"⏱️  Payback Period: {roi['payback_period_months']:.1f} months")
        print(f"📊 ROI Percentage: {roi['roi_percentage']:.1f}%")
        
        # Display next actions
        print("\n🎯 NEXT ACTIONS:")
        for action in dashboard['next_actions']:
            print(f"Priority {action['priority']}: {action['action']}")
            print(f"   {action['details']}")
            print(f"   Timeline: {action['timeline']} | Responsible: {action['responsible']}")
        
        # Save detailed results
        filename = orchestrator.save_results(results)
        
        print("\n" + "=" * 60)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 60)
        print(f"📁 Detailed results saved to: {filename}")
        print("🚀 System ready for procurement automation!")
        
        return results
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        print("Please check your data files and environment setup")
        raise

if __name__ == "__main__":
    main()
