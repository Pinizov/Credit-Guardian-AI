"""
Evaluation metrics for assessing AI agent performance.

Includes metrics for:
- Contract analysis accuracy
- Violation detection completeness
- Complaint generation quality
- Overall agent effectiveness
"""
from typing import Dict, Any, List
from difflib import SequenceMatcher


class EvaluationMetrics:
    """Comprehensive metrics for evaluating the Credit Guardian AI agent."""
    
    @staticmethod
    def calculate_accuracy(predicted: Dict[str, Any], expected: Dict[str, Any]) -> float:
        """
        Calculate overall accuracy by comparing predicted vs expected outputs.
        
        Args:
            predicted: Agent's output
            expected: Ground truth expected output
            
        Returns:
            Accuracy score between 0.0 and 1.0
        """
        if not predicted or not expected:
            return 0.0
        
        # Key fields to compare
        key_fields = ["contract_number", "creditor", "principal", "stated_apr"]
        
        matches = 0
        total_fields = 0
        
        for field in key_fields:
            if field in expected:
                total_fields += 1
                pred_value = str(predicted.get(field, "")).lower()
                exp_value = str(expected.get(field, "")).lower()
                
                # Exact match or close match
                if pred_value == exp_value:
                    matches += 1
                elif SequenceMatcher(None, pred_value, exp_value).ratio() > 0.8:
                    matches += 0.5  # Partial credit for close matches
        
        return matches / total_fields if total_fields > 0 else 0.0
    
    @staticmethod
    def calculate_violation_recall(
        predicted_violations: List[str], 
        expected_violations: List[str]
    ) -> float:
        """
        Calculate recall for violation detection.
        
        Recall = True Positives / (True Positives + False Negatives)
        Measures how many actual violations were found.
        
        Args:
            predicted_violations: List of violations found by agent
            expected_violations: List of known violations in ground truth
            
        Returns:
            Recall score between 0.0 and 1.0
        """
        if not expected_violations:
            return 1.0 if not predicted_violations else 0.0
        
        # Normalize violation text for comparison
        predicted_set = {v.lower().strip() for v in predicted_violations}
        expected_set = {v.lower().strip() for v in expected_violations}
        
        # Find true positives using fuzzy matching
        true_positives = 0
        for exp_violation in expected_set:
            for pred_violation in predicted_set:
                similarity = SequenceMatcher(None, exp_violation, pred_violation).ratio()
                if similarity > 0.7:  # 70% similarity threshold
                    true_positives += 1
                    break
        
        recall = true_positives / len(expected_set)
        return recall
    
    @staticmethod
    def calculate_violation_precision(
        predicted_violations: List[str],
        expected_violations: List[str]
    ) -> float:
        """
        Calculate precision for violation detection.
        
        Precision = True Positives / (True Positives + False Positives)
        Measures how many predicted violations are correct.
        
        Args:
            predicted_violations: List of violations found by agent
            expected_violations: List of known violations in ground truth
            
        Returns:
            Precision score between 0.0 and 1.0
        """
        if not predicted_violations:
            return 1.0 if not expected_violations else 0.0
        
        predicted_set = {v.lower().strip() for v in predicted_violations}
        expected_set = {v.lower().strip() for v in expected_violations}
        
        # Find true positives
        true_positives = 0
        for pred_violation in predicted_set:
            for exp_violation in expected_set:
                similarity = SequenceMatcher(None, pred_violation, exp_violation).ratio()
                if similarity > 0.7:
                    true_positives += 1
                    break
        
        precision = true_positives / len(predicted_set)
        return precision
    
    @staticmethod
    def calculate_f1_score(precision: float, recall: float) -> float:
        """
        Calculate F1 score (harmonic mean of precision and recall).
        
        Args:
            precision: Precision score
            recall: Recall score
            
        Returns:
            F1 score between 0.0 and 1.0
        """
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)
    
    @staticmethod
    def calculate_complaint_quality(complaint: str, required_elements: List[str]) -> float:
        """
        Evaluate quality of generated complaint.
        
        Checks for presence of required legal elements like:
        - User information
        - Violation descriptions
        - Legal references
        - Formal structure
        
        Args:
            complaint: Generated complaint text
            required_elements: List of required elements/keywords
            
        Returns:
            Quality score between 0.0 and 1.0
        """
        if not complaint or not required_elements:
            return 0.0
        
        complaint_lower = complaint.lower()
        elements_found = 0
        
        for element in required_elements:
            if element.lower() in complaint_lower:
                elements_found += 1
        
        # Also check for minimum length and structure
        length_score = min(len(complaint) / 500, 1.0)  # Expect at least 500 chars
        element_score = elements_found / len(required_elements)
        
        return (length_score * 0.3) + (element_score * 0.7)
    
    @staticmethod
    def calculate_gpr_accuracy(predicted_gpr: float, actual_gpr: float, tolerance: float = 0.5) -> float:
        """
        Calculate accuracy of GPR (APR) calculation.
        
        Args:
            predicted_gpr: Predicted APR/GPR value
            actual_gpr: Actual APR/GPR value from ground truth
            tolerance: Acceptable percentage point difference
            
        Returns:
            Accuracy score between 0.0 and 1.0
        """
        if actual_gpr == 0:
            return 1.0 if predicted_gpr == 0 else 0.0
        
        difference = abs(predicted_gpr - actual_gpr)
        
        if difference <= tolerance:
            return 1.0
        elif difference <= tolerance * 2:
            return 0.5
        else:
            return 0.0
    
    @staticmethod
    def aggregate_results(results: List[Dict[str, float]]) -> Dict[str, Any]:
        """
        Aggregate evaluation results across multiple test cases.
        
        Args:
            results: List of evaluation result dictionaries
            
        Returns:
            Aggregated statistics including mean, median, min, max
        """
        if not results:
            return {}
        
        aggregated = {}
        
        # Get all metric names from first result
        metric_names = results[0].keys()
        
        for metric in metric_names:
            values = [r.get(metric, 0.0) for r in results if metric in r]
            
            if values:
                aggregated[metric] = {
                    "mean": sum(values) / len(values),
                    "median": sorted(values)[len(values) // 2],
                    "min": min(values),
                    "max": max(values),
                    "count": len(values)
                }
        
        return aggregated
    
    @staticmethod
    def generate_report(results: List[Dict[str, Any]], output_path: str = None) -> str:
        """
        Generate a comprehensive evaluation report.
        
        Args:
            results: List of evaluation results
            output_path: Optional path to save report
            
        Returns:
            Report text
        """
        aggregated = EvaluationMetrics.aggregate_results(results)
        
        report_lines = [
            "=" * 60,
            "CREDIT GUARDIAN AI AGENT - EVALUATION REPORT",
            "=" * 60,
            f"\nTotal Test Cases: {len(results)}",
            "\n" + "-" * 60,
            "METRIC SUMMARY",
            "-" * 60,
        ]
        
        for metric_name, stats in aggregated.items():
            report_lines.append(f"\n{metric_name.upper()}:")
            report_lines.append(f"  Mean:   {stats['mean']:.3f}")
            report_lines.append(f"  Median: {stats['median']:.3f}")
            report_lines.append(f"  Min:    {stats['min']:.3f}")
            report_lines.append(f"  Max:    {stats['max']:.3f}")
        
        report_lines.append("\n" + "=" * 60)
        
        report = "\n".join(report_lines)
        
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report)
        
        return report
