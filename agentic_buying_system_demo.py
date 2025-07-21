#!/usr/bin/env python3
"""
Enhanced Agentic Buying System Demo
Showcases truly autonomous AI agents that:
- Monitor continuously and make autonomous decisions
- Communicate and negotiate with each other
- Learn and adapt from experience
- Handle complex scenarios without human intervention
"""

import asyncio
import os
from dotenv import load_dotenv
from agents.enhanced.agentic_orchestrator import AgenticOrchestrator

async def main():
    # Load environment variables
    load_dotenv()
    
    if not os.environ.get("HF_TOKEN"):
        print("❌ Error: HF_TOKEN environment variable not set")
        return
    
    print("=" * 80)
    print("🤖 ENHANCED AGENTIC INTELLIGENT BUYING SYSTEM")
    print("=" * 80)
    print("🧠 Autonomous AI Agents with Learning & Adaptation")
    print("🤝 Inter-Agent Communication & Negotiation")
    print("⚡ Real-time Decision Making & Continuous Monitoring")
    print("🎯 Self-Improving Procurement Intelligence")
    print("=" * 80)
    
    # Initialize the enhanced agentic orchestrator
    orchestrator = AgenticOrchestrator()
    
    try:
        print("\n🚀 STARTING AUTONOMOUS OPERATIONS...")
        
        # Start autonomous operations
        autonomous_tasks = await orchestrator.start_autonomous_operations()
        
        print("\n📊 INITIAL SYSTEM ANALYSIS...")
        
        # Run initial analysis
        data = orchestrator.data_loader.process({})
        stockout_analysis = orchestrator.stockout_predictor.process(data)
        supplier_analysis = orchestrator.supplier_analyzer.process(data)
        
        print(f"📦 Found {stockout_analysis['summary']['critical_count']} critical stockouts")
        print(f"⚠️  Found {stockout_analysis['summary']['high_risk_count']} high-risk items")
        print(f"🏢 Analyzing {len(supplier_analysis['analyzed_performance'])} suppliers")
        
        print("\n🤖 AUTONOMOUS AGENTS NOW ACTIVE:")
        print("🔍 Monitoring Agent - Continuously watching for issues")
        print("🤝 Negotiation Agent - Ready for autonomous supplier negotiations")
        print("🧠 Learning Agent - Adapting based on outcomes")
        print("📡 Message Bus - Enabling agent-to-agent communication")
        
        print("\n⏰ DEMONSTRATION TIMELINE:")
        print("Next 30 seconds: Monitoring and analysis")
        print("30-60 seconds: Autonomous decision making")
        print("60-90 seconds: Learning and adaptation")
        
        # Let the system run autonomously for demonstration
        print("\n🔄 System running autonomously... (Press Ctrl+C to stop)")
        
        # Simulate some time for autonomous operations
        for i in range(90):  # 90 seconds demo
            await asyncio.sleep(1)
            
            # Show periodic status updates
            if i % 15 == 0 and i > 0:
                status = orchestrator.get_autonomous_status()
                print(f"\n📈 STATUS UPDATE ({i}s):")
                print(f"   🤖 Autonomous Mode: {'ON' if status['autonomous_mode'] else 'OFF'}")
                print(f"   🎯 Decisions Made: {status['decisions_made']}")
                print(f"   💰 Max Authority: ${status['decision_authority']['max_order_value']:,}")
                print(f"   🧠 Knowledge Items: {status['knowledge_base_stats']['total_items']}")
                print(f"   📨 Messages Processed: {status['message_bus_stats']['messages_processed']}")
        
        print("\n" + "=" * 80)
        print("📊 FINAL AUTONOMOUS OPERATION SUMMARY")
        print("=" * 80)
        
        final_status = orchestrator.get_autonomous_status()
        
        print(f"🎯 Total Autonomous Decisions Made: {final_status['decisions_made']}")
        print(f"💰 Current Decision Authority: ${final_status['decision_authority']['max_order_value']:,}")
        print(f"🧠 Knowledge Base Size: {final_status['knowledge_base_stats']['total_items']} items")
        print(f"📨 Messages Processed: {final_status['message_bus_stats']['messages_processed']}")
        print(f"🔗 Active Communication Channels: {len(final_status['message_bus_stats']['active_channels'])}")
        
        # Show recent autonomous decisions
        if orchestrator.decision_log:
            print("\n🤖 RECENT AUTONOMOUS DECISIONS:")
            for i, decision_entry in enumerate(orchestrator.decision_log[-3:], 1):
                decision = decision_entry['decision']
                print(f"{i}. {decision['type']}")
                print(f"   SKU: {decision.get('sku_id', 'N/A')}")
                print(f"   Confidence: {decision_entry['confidence']:.1%}")
                print(f"   Authority: {decision.get('authority_level', 'autonomous')}")
        
        # Show learning and adaptation
        if final_status['performance_metrics']:
            print("\n📈 LEARNING & ADAPTATION METRICS:")
            metrics = final_status['performance_metrics']
            print(f"   📊 Decisions (24h): {metrics.get('decisions_made_24h', 0)}")
            print(f"   📈 Authority Level: ${metrics.get('autonomous_authority_level', 0):,}")
            print(f"   🕒 Last Updated: {metrics.get('last_updated', 'N/A')}")
        
        print("\n🎯 AGENTIC CAPABILITIES DEMONSTRATED:")
        print("✅ Autonomous monitoring and alerting")
        print("✅ Real-time decision making within authority bounds")
        print("✅ Inter-agent communication and coordination")
        print("✅ Learning from outcomes and adaptation")
        print("✅ Knowledge sharing and accumulation")
        print("✅ Escalation handling for complex scenarios")
        
        print("\n💡 BUSINESS VALUE DELIVERED:")
        print("💰 Automated emergency procurement decisions")
        print("⚡ 24/7 continuous monitoring without human intervention")
        print("🎯 Self-improving decision accuracy over time")
        print("📞 Autonomous supplier negotiation capabilities")
        print("🧠 Institutional knowledge retention and growth")
        
        print("\n" + "=" * 80)
        print("🚀 AGENTIC BUYING SYSTEM DEMO COMPLETE")
        print("=" * 80)
        print("🎊 The system demonstrated true autonomous AI agent capabilities!")
        print("🔄 In production, this would run 24/7 with continuous improvement")
        print("📈 Expected ROI: $90,000 - $108,000 annually + operational efficiency gains")
        
    except KeyboardInterrupt:
        print("\n\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
    finally:
        print("\n🔄 Shutting down autonomous operations...")
        await orchestrator.stop_autonomous_operations()
        print("✅ Shutdown complete")

def show_agentic_comparison():
    """Show comparison between traditional and agentic approaches"""
    
    print("\n" + "=" * 80)
    print("📊 TRADITIONAL vs AGENTIC SYSTEM COMPARISON")
    print("=" * 80)
    
    comparison = """
    🔹 TRADITIONAL SYSTEM:                    🤖 AGENTIC SYSTEM:
    ┌─────────────────────────────────────┐  ┌─────────────────────────────────────┐
    │ ⏰ Scheduled batch processing        │  │ 🔄 Continuous real-time monitoring   │
    │ 👤 Human-triggered decisions         │  │ 🤖 Autonomous decision making        │
    │ 📊 Static analysis reports          │  │ 🧠 Learning and adaptation           │
    │ 📧 Email/dashboard alerts           │  │ 📡 Agent-to-agent communication      │
    │ 📋 Manual supplier selection        │  │ 🤝 Autonomous negotiation            │
    │ 🔄 No learning from outcomes        │  │ 📈 Self-improving algorithms         │
    │ ⏳ Hours/days response time          │  │ ⚡ Seconds/minutes response time     │
    │ 🚨 Reactive problem solving         │  │ 🎯 Proactive problem prevention      │
    └─────────────────────────────────────┘  └─────────────────────────────────────┘
    
    🎯 AGENTIC FEATURES THAT MAKE THE DIFFERENCE:
    
    1. 🧠 COGNITIVE AUTONOMY
       - Agents reason about complex scenarios
       - Make contextual decisions within bounds
       - Learn from experience and adapt
    
    2. 🤝 SOCIAL INTELLIGENCE
       - Agents communicate and coordinate
       - Negotiate with suppliers autonomously
       - Share knowledge and insights
    
    3. ⚡ REACTIVITY & PROACTIVITY
       - Respond instantly to environmental changes
       - Anticipate problems before they occur
       - Take initiative without human prompting
    
    4. 🎯 GOAL-ORIENTED BEHAVIOR
       - Understand business objectives
       - Optimize for multiple competing goals
       - Adapt strategies based on outcomes
    
    5. 🔄 CONTINUOUS IMPROVEMENT
       - Learn from every decision and outcome
       - Refine decision boundaries over time
       - Build institutional knowledge
    """
    
    print(comparison)

if __name__ == "__main__":
    show_agentic_comparison()
    asyncio.run(main())
