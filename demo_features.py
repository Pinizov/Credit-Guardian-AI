"""
Example script demonstrating observability and evaluation features.

This script shows how to:
1. Use tracing with the AI agent
2. Run evaluation on a test case
3. Calculate metrics
4. Generate reports
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from ai_agent.tracing import initialize_tracing, trace_span, add_trace_event
from evaluation.dataset import EvaluationDataset
from evaluation.metrics import EvaluationMetrics


def demo_tracing():
    """Demonstrate tracing capabilities."""
    print("\n" + "=" * 60)
    print("DEMO: Tracing with OpenTelemetry")
    print("=" * 60 + "\n")
    
    # Initialize tracing with console export
    initialize_tracing(
        service_name="credit-guardian-demo",
        console_export=True
    )
    
    print("✓ Tracing initialized\n")
    
    # Example 1: Basic span
    print("Example 1: Basic trace span")
    with trace_span("demo_operation", attributes={"demo": "basic"}):
        add_trace_event("processing_start")
        # Simulate some work
        import time
        time.sleep(0.5)
        add_trace_event("processing_complete")
    
    print("✓ Trace span completed\n")
    
    # Example 2: Nested spans
    print("Example 2: Nested trace spans")
    with trace_span("parent_operation", attributes={"level": "parent"}):
        add_trace_event("parent_start")
        
        with trace_span("child_operation_1", attributes={"level": "child"}):
            add_trace_event("child1_processing")
            time.sleep(0.2)
        
        with trace_span("child_operation_2", attributes={"level": "child"}):
            add_trace_event("child2_processing")
            time.sleep(0.3)
        
        add_trace_event("parent_complete")
    
    print("✓ Nested spans completed\n")
    
    print("Note: Traces are exported to console. For production, configure OTLP endpoint.")


def demo_evaluation():
    """Demonstrate evaluation framework."""
    print("\n" + "=" * 60)
    print("DEMO: Evaluation Framework")
    print("=" * 60 + "\n")
    
    # Create sample dataset
    print("Creating sample dataset...")
    dataset = EvaluationDataset()
    sample_cases = dataset.create_sample_dataset()
    print(f"✓ Created {len(sample_cases)} sample test cases\n")
    
    # Display test case structure
    print("Sample test case structure:")
    if sample_cases:
        test_case = sample_cases[0]
        print(f"  ID: {test_case['id']}")
        print(f"  Description: {test_case['description']}")
        print(f"  Input PDF: {test_case['input']['pdf_path']}")
        print(f"  Expected violations: {len(test_case['expected']['violations'])}")
    
    print()


def demo_metrics():
    """Demonstrate metrics calculation."""
    print("\n" + "=" * 60)
    print("DEMO: Evaluation Metrics")
    print("=" * 60 + "\n")
    
    # Example data
    predicted = {
        "contract_number": "K-2024-001234",
        "creditor": "Test Bank",
        "principal": 5000.0,
        "stated_apr": 35.5
    }
    
    expected = {
        "contract_number": "K-2024-001234",
        "creditor": "Test Bank",
        "principal": 5000.0,
        "stated_apr": 35.5
    }
    
    # Calculate accuracy
    accuracy = EvaluationMetrics.calculate_accuracy(predicted, expected)
    print(f"Contract Analysis Accuracy: {accuracy:.2%}")
    
    # Violation detection metrics
    predicted_violations = [
        "Неразкрита информация за действителния ГПР",
        "Скрита такса за управление на сметка"
    ]
    
    expected_violations = [
        "Неразкрита информация за действителния ГПР",
        "Скрита такса за управление на сметка",
        "Неравноправна клауза за едностранно изменение"
    ]
    
    recall = EvaluationMetrics.calculate_violation_recall(
        predicted_violations, expected_violations
    )
    precision = EvaluationMetrics.calculate_violation_precision(
        predicted_violations, expected_violations
    )
    f1 = EvaluationMetrics.calculate_f1_score(precision, recall)
    
    print(f"Violation Detection Recall: {recall:.2%}")
    print(f"Violation Detection Precision: {precision:.2%}")
    print(f"Violation Detection F1 Score: {f1:.2%}")
    
    # GPR accuracy
    gpr_accuracy = EvaluationMetrics.calculate_gpr_accuracy(35.5, 35.8, tolerance=0.5)
    print(f"GPR Accuracy: {gpr_accuracy:.2%}")
    
    # Aggregate results
    print("\n" + "-" * 60)
    print("Aggregated Results Example")
    print("-" * 60)
    
    sample_results = [
        {"accuracy": 0.95, "recall": 0.90, "precision": 0.85, "f1": 0.87},
        {"accuracy": 0.88, "recall": 0.85, "precision": 0.90, "f1": 0.87},
        {"accuracy": 0.92, "recall": 0.88, "precision": 0.87, "f1": 0.87}
    ]
    
    aggregated = EvaluationMetrics.aggregate_results(sample_results)
    
    print("\nMetric Summary:")
    for metric_name, stats in aggregated.items():
        print(f"\n{metric_name.upper()}:")
        print(f"  Mean:   {stats['mean']:.3f}")
        print(f"  Median: {stats['median']:.3f}")
        print(f"  Min:    {stats['min']:.3f}")
        print(f"  Max:    {stats['max']:.3f}")


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("CREDIT GUARDIAN - OBSERVABILITY & EVALUATION DEMO")
    print("=" * 60)
    
    try:
        # Run demos
        demo_tracing()
        demo_evaluation()
        demo_metrics()
        
        print("\n" + "=" * 60)
        print("DEMO COMPLETE")
        print("=" * 60)
        
        print("\nNext steps:")
        print("1. Set PERPLEXITY_API_KEY or run Ollama locally")
        print("2. Create test PDF files in tests/fixtures/")
        print("3. Run full evaluation: python run_evaluation.py --verbose")
        print("4. Set up trace export: $env:OTEL_EXPORTER_OTLP_ENDPOINT='http://localhost:4317'")
        print("5. Read full documentation: README_OBSERVABILITY.md\n")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
