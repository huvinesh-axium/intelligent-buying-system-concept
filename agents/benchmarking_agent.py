import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime, timedelta
from .base_agent import BaseAgent

class BenchmarkingAgent(BaseAgent):
    def __init__(self):
        super().__init__("Benchmarking")
        self.benchmarks = {
            'substitution_accuracy': 0.85,  # Target 85% accuracy
            'brand_switching_accuracy': 0.80,  # Target 80% accuracy
            'cost_reduction': 0.15,  # Target 15% cost reduction
            'lead_time_improvement': 0.20,  # Target 20% lead time improvement
            'stockout_prevention': 0.90  # Target 90% stockout prevention
        }
    
    def evaluate_substitution_accuracy(self, recommendations: List[Dict], 
                                     historical_substitutions: pd.DataFrame) -> Dict[str, float]:
        # Evaluate how accurate our substitution recommendations are
        # compared to historical successful substitutions
        
        if len(recommendations) == 0:
            return {'accuracy': 0.0, 'confidence': 0.0}
        
        correct_predictions = 0
        total_predictions = 0
        
        for rec in recommendations:
            if rec['substitution_options']:
                total_predictions += 1
                sku_id = rec['sku_id']
                
                # Check if our recommended substitutions match historical patterns
                historical_subs = historical_substitutions[
                    historical_substitutions['original_sku'] == sku_id
                ]['substitute_sku'].tolist()
                
                # If any of our recommendations match historical successful substitutions
                if any(sub in historical_subs for sub in rec['substitution_options']):
                    correct_predictions += 1
        
        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0.0
        
        return {
            'accuracy': accuracy,
            'benchmark_target': self.benchmarks['substitution_accuracy'],
            'meets_benchmark': accuracy >= self.benchmarks['substitution_accuracy'],
            'total_predictions': total_predictions,
            'correct_predictions': correct_predictions
        }
    
    def evaluate_supplier_recommendations(self, recommendations: List[Dict], 
                                        supplier_performance: pd.DataFrame) -> Dict[str, Any]:
        # Evaluate quality of supplier recommendations
        scores = []
        
        for rec in recommendations:
            if rec['primary_supplier']:
                supplier_id = rec['primary_supplier']['supplier_id']
                reliability_score = rec['primary_supplier']['reliability_score']
                scores.append(reliability_score)
        
        avg_recommended_score = np.mean(scores) if scores else 0
        
        # Compare to overall supplier population
        overall_avg = supplier_performance['reliability_score'].mean()
        
        return {
            'avg_recommended_supplier_score': avg_recommended_score,
            'overall_supplier_avg': overall_avg,
            'improvement_factor': avg_recommended_score / overall_avg if overall_avg > 0 else 1.0,
            'recommendations_count': len(scores),
            'quality_grade': self._grade_performance(avg_recommended_score)
        }
    
    def evaluate_cost_impact(self, recommendations: List[Dict]) -> Dict[str, Any]:
        # Evaluate potential cost savings and optimization
        total_normal_cost = sum(r['estimated_cost_impact']['normal_order_cost'] for r in recommendations)
        total_expedited_cost = sum(r['estimated_cost_impact']['expedited_cost'] for r in recommendations)
        total_premium = total_expedited_cost - total_normal_cost
        
        # Calculate potential savings through better planning
        potential_savings = total_premium * 0.6  # Assume 60% of premiums could be avoided
        
        return {
            'total_normal_cost': total_normal_cost,
            'total_expedited_cost': total_expedited_cost,
            'cost_premium': total_premium,
            'potential_savings': potential_savings,
            'savings_percentage': (potential_savings / total_expedited_cost * 100) if total_expedited_cost > 0 else 0,
            'meets_cost_benchmark': (potential_savings / total_expedited_cost) >= self.benchmarks['cost_reduction']
        }
    
    def evaluate_lead_time_optimization(self, recommendations: List[Dict]) -> Dict[str, Any]:
        # Evaluate lead time improvements from supplier selection
        lead_times = []
        
        for rec in recommendations:
            if rec['primary_supplier']:
                lead_times.append(rec['primary_supplier']['lead_time'])
        
        if not lead_times:
            return {'optimization_score': 0.0}
        
        avg_lead_time = np.mean(lead_times)
        min_possible_lead_time = min(lead_times)
        
        # Calculate optimization potential
        optimization_score = (max(lead_times) - avg_lead_time) / max(lead_times) if max(lead_times) > 0 else 0
        
        return {
            'avg_recommended_lead_time': avg_lead_time,
            'min_lead_time': min_possible_lead_time,
            'max_lead_time': max(lead_times),
            'optimization_score': optimization_score,
            'meets_benchmark': optimization_score >= self.benchmarks['lead_time_improvement'],
            'total_items_analyzed': len(lead_times)
        }
    
    def _grade_performance(self, score: float) -> str:
        if score >= 90: return "A+"
        elif score >= 85: return "A"
        elif score >= 80: return "B+"
        elif score >= 75: return "B"
        elif score >= 70: return "C+"
        elif score >= 65: return "C"
        else: return "D"
    
    def calculate_system_effectiveness(self, all_metrics: Dict[str, Any]) -> Dict[str, Any]:
        # Overall system effectiveness score
        effectiveness_scores = []
        
        # Weight different metrics
        weights = {
            'supplier_quality': 0.30,
            'cost_optimization': 0.25,
            'lead_time_optimization': 0.20,
            'substitution_accuracy': 0.15,
            'overall_coverage': 0.10
        }
        
        # Calculate weighted effectiveness
        if 'supplier_recommendations' in all_metrics:
            supplier_score = all_metrics['supplier_recommendations']['improvement_factor'] * 100
            effectiveness_scores.append(('supplier_quality', min(supplier_score, 100)))
        
        if 'cost_impact' in all_metrics:
            cost_score = all_metrics['cost_impact']['savings_percentage']
            effectiveness_scores.append(('cost_optimization', cost_score))
        
        if 'lead_time_optimization' in all_metrics:
            lead_time_score = all_metrics['lead_time_optimization']['optimization_score'] * 100
            effectiveness_scores.append(('lead_time_optimization', lead_time_score))
        
        # Calculate overall effectiveness
        total_weighted_score = sum(
            score * weights.get(metric, 0) for metric, score in effectiveness_scores
        )
        
        return {
            'overall_effectiveness_score': total_weighted_score,
            'grade': self._grade_performance(total_weighted_score),
            'component_scores': dict(effectiveness_scores),
            'benchmark_compliance': {
                benchmark: score >= target * 100 
                for benchmark, target in self.benchmarks.items()
                if benchmark in [metric for metric, _ in effectiveness_scores]
            }
        }
    
    def generate_improvement_recommendations(self, metrics: Dict[str, Any]) -> List[Dict[str, str]]:
        recommendations = []
        
        # Check each benchmark and suggest improvements
        if 'substitution_accuracy' in metrics:
            acc = metrics['substitution_accuracy']
            if not acc.get('meets_benchmark', False):
                recommendations.append({
                    'area': 'Substitution Logic',
                    'issue': f"Accuracy {acc['accuracy']:.1%} below target {self.benchmarks['substitution_accuracy']:.1%}",
                    'recommendation': 'Enhance product similarity algorithms and historical pattern analysis'
                })
        
        if 'supplier_recommendations' in metrics:
            supplier_quality = metrics['supplier_recommendations']['avg_recommended_supplier_score']
            if supplier_quality < 80:
                recommendations.append({
                    'area': 'Supplier Selection',
                    'issue': f"Average supplier quality score {supplier_quality:.1f} could be improved",
                    'recommendation': 'Expand supplier database and improve scoring methodology'
                })
        
        if 'cost_impact' in metrics:
            cost_metrics = metrics['cost_impact']
            if not cost_metrics.get('meets_cost_benchmark', False):
                recommendations.append({
                    'area': 'Cost Optimization',
                    'issue': f"Cost savings {cost_metrics['savings_percentage']:.1f}% below target {self.benchmarks['cost_reduction']*100:.1f}%",
                    'recommendation': 'Implement better demand forecasting and supplier negotiation strategies'
                })
        
        return recommendations
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        recommendations = data.get('recommendations', [])
        supplier_performance = data.get('analyzed_performance', pd.DataFrame())
        
        # Create mock historical substitutions for benchmarking
        # In real implementation, this would come from ERP system
        historical_substitutions = pd.DataFrame({
            'original_sku': ['SKU-102', 'SKU-201', 'SKU-301'],
            'substitute_sku': ['SKU-103', 'SKU-202', 'SKU-302'],
            'success_rate': [0.9, 0.85, 0.8]
        })
        
        # Run all evaluations
        substitution_eval = self.evaluate_substitution_accuracy(recommendations, historical_substitutions)
        supplier_eval = self.evaluate_supplier_recommendations(recommendations, supplier_performance)
        cost_eval = self.evaluate_cost_impact(recommendations)
        lead_time_eval = self.evaluate_lead_time_optimization(recommendations)
        
        all_metrics = {
            'substitution_accuracy': substitution_eval,
            'supplier_recommendations': supplier_eval,
            'cost_impact': cost_eval,
            'lead_time_optimization': lead_time_eval
        }
        
        # Calculate overall effectiveness
        effectiveness = self.calculate_system_effectiveness(all_metrics)
        improvement_recs = self.generate_improvement_recommendations(all_metrics)
        
        return {
            'benchmark_results': all_metrics,
            'system_effectiveness': effectiveness,
            'improvement_recommendations': improvement_recs,
            'benchmark_targets': self.benchmarks,
            'evaluation_timestamp': datetime.now().isoformat()
        }
