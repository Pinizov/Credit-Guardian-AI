"""
Tests for evaluation framework.
"""
import pytest
from evaluation.metrics import EvaluationMetrics
from evaluation.dataset import EvaluationDataset


class TestEvaluationMetrics:
    """Test evaluation metrics calculations."""
    
    def test_calculate_accuracy_exact_match(self):
        """Test accuracy calculation with exact match."""
        predicted = {
            "contract_number": "K-2024-001",
            "creditor": "Test Bank",
            "principal": 5000.0,
            "stated_apr": 12.5
        }
        expected = {
            "contract_number": "K-2024-001",
            "creditor": "Test Bank",
            "principal": 5000.0,
            "stated_apr": 12.5
        }
        
        accuracy = EvaluationMetrics.calculate_accuracy(predicted, expected)
        assert accuracy == 1.0
    
    def test_calculate_accuracy_partial_match(self):
        """Test accuracy calculation with partial match."""
        predicted = {
            "contract_number": "K-2024-001",
            "creditor": "Test Bank",
            "principal": 5000.0,
            "stated_apr": 15.0  # Different from expected
        }
        expected = {
            "contract_number": "K-2024-001",
            "creditor": "Test Bank",
            "principal": 5000.0,
            "stated_apr": 12.5
        }
        
        accuracy = EvaluationMetrics.calculate_accuracy(predicted, expected)
        assert 0.5 < accuracy < 1.0  # 3 out of 4 fields match
    
    def test_violation_recall_perfect(self):
        """Test violation recall with all violations found."""
        predicted = ["Violation A", "Violation B", "Violation C"]
        expected = ["Violation A", "Violation B", "Violation C"]
        
        recall = EvaluationMetrics.calculate_violation_recall(predicted, expected)
        assert recall == 1.0
    
    def test_violation_recall_missing_some(self):
        """Test violation recall with some violations missed."""
        predicted = ["Violation A", "Violation B"]
        expected = ["Violation A", "Violation B", "Violation C"]
        
        recall = EvaluationMetrics.calculate_violation_recall(predicted, expected)
        assert 0.6 < recall < 0.7  # 2 out of 3 found
    
    def test_violation_precision_perfect(self):
        """Test violation precision with all correct predictions."""
        predicted = ["Violation A", "Violation B"]
        expected = ["Violation A", "Violation B", "Violation C"]
        
        precision = EvaluationMetrics.calculate_violation_precision(predicted, expected)
        assert precision == 1.0  # All predicted are correct
    
    def test_violation_precision_with_false_positives(self):
        """Test violation precision with false positives."""
        predicted = ["Violation A", "Violation B", "False Violation"]
        expected = ["Violation A", "Violation B"]
        
        precision = EvaluationMetrics.calculate_violation_precision(predicted, expected)
        assert 0.6 < precision < 0.7  # 2 out of 3 predicted are correct
    
    def test_f1_score(self):
        """Test F1 score calculation."""
        precision = 0.8
        recall = 0.6
        
        f1 = EvaluationMetrics.calculate_f1_score(precision, recall)
        expected_f1 = 2 * (0.8 * 0.6) / (0.8 + 0.6)
        assert abs(f1 - expected_f1) < 0.001
    
    def test_gpr_accuracy_exact(self):
        """Test GPR accuracy with exact match."""
        accuracy = EvaluationMetrics.calculate_gpr_accuracy(12.5, 12.5)
        assert accuracy == 1.0
    
    def test_gpr_accuracy_within_tolerance(self):
        """Test GPR accuracy within tolerance."""
        accuracy = EvaluationMetrics.calculate_gpr_accuracy(12.5, 12.8, tolerance=0.5)
        assert accuracy == 1.0
    
    def test_gpr_accuracy_outside_tolerance(self):
        """Test GPR accuracy outside tolerance."""
        accuracy = EvaluationMetrics.calculate_gpr_accuracy(12.5, 15.0, tolerance=0.5)
        assert accuracy == 0.0
    
    def test_complaint_quality(self):
        """Test complaint quality evaluation."""
        complaint = "Жалба до КЗП относно потребителски договор с нарушения"
        required_elements = ["жалба", "КЗП", "договор", "нарушение"]
        
        quality = EvaluationMetrics.calculate_complaint_quality(complaint, required_elements)
        assert quality > 0.5  # Should find most elements
    
    def test_aggregate_results(self):
        """Test aggregation of evaluation results."""
        results = [
            {"accuracy": 0.8, "recall": 0.9},
            {"accuracy": 0.9, "recall": 0.8},
            {"accuracy": 0.7, "recall": 0.85}
        ]
        
        aggregated = EvaluationMetrics.aggregate_results(results)
        
        assert "accuracy" in aggregated
        assert "recall" in aggregated
        assert aggregated["accuracy"]["mean"] == pytest.approx(0.8, abs=0.01)
        assert aggregated["accuracy"]["count"] == 3


class TestEvaluationDataset:
    """Test evaluation dataset management."""
    
    def test_add_test_case(self):
        """Test adding a test case to dataset."""
        dataset = EvaluationDataset()
        
        dataset.add_test_case(
            test_id="test_001",
            pdf_path="path/to/test.pdf",
            user_data={"name": "Test User", "address": "Test Address"},
            expected_analysis={"creditor": "Test Bank"},
            expected_violations=["Violation 1"],
            description="Test case 1"
        )
        
        assert len(dataset.test_cases) == 1
        assert dataset.test_cases[0]["id"] == "test_001"
    
    def test_create_sample_dataset(self):
        """Test sample dataset creation."""
        dataset = EvaluationDataset()
        sample_cases = dataset.create_sample_dataset()
        
        assert len(sample_cases) > 0
        assert all("id" in case for case in sample_cases)
        assert all("input" in case for case in sample_cases)
        assert all("expected" in case for case in sample_cases)
    
    def test_validate_dataset_valid(self):
        """Test dataset validation with valid data."""
        dataset = EvaluationDataset()
        dataset.create_sample_dataset()
        
        validation = dataset.validate_dataset()
        
        assert validation["valid_cases"] > 0
        assert validation["invalid_cases"] == 0
        assert len(validation["errors"]) == 0
    
    def test_validate_dataset_invalid(self):
        """Test dataset validation with invalid data."""
        dataset = EvaluationDataset()
        dataset.test_cases = [
            {"id": "test_001"},  # Missing input and expected
            {"id": "test_002", "input": {}}  # Missing expected
        ]
        
        validation = dataset.validate_dataset()
        
        assert validation["invalid_cases"] > 0
        assert len(validation["errors"]) > 0
    
    def test_get_test_cases_no_filter(self):
        """Test getting all test cases."""
        dataset = EvaluationDataset()
        dataset.create_sample_dataset()
        
        cases = dataset.get_test_cases()
        
        assert len(cases) == len(dataset.test_cases)
    
    def test_get_test_cases_with_filter(self):
        """Test getting filtered test cases."""
        dataset = EvaluationDataset()
        dataset.create_sample_dataset()
        
        all_ids = [case["id"] for case in dataset.test_cases]
        filter_ids = [all_ids[0]] if all_ids else []
        
        cases = dataset.get_test_cases(filter_ids=filter_ids)
        
        assert len(cases) <= len(dataset.test_cases)
        if filter_ids:
            assert all(case["id"] in filter_ids for case in cases)
