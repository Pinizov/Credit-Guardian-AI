"""
Main evaluation script for Credit Guardian AI Agent.

Usage:
    python run_evaluation.py --dataset evaluation/test_dataset.json --output evaluation/results.json

This script:
1. Loads test dataset
2. Runs agent on each test case
3. Calculates evaluation metrics
4. Generates comprehensive report
"""
import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ai_agent.agent_executor import AgentExecutor
from evaluation.dataset import EvaluationDataset
from evaluation.runner import AgentRunner
from evaluation.metrics import EvaluationMetrics


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run evaluation for Credit Guardian AI Agent"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="evaluation/test_dataset.json",
        help="Path to test dataset JSON file"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="evaluation/results.json",
        help="Path to save evaluation results"
    )
    parser.add_argument(
        "--report",
        type=str,
        default="evaluation/report.txt",
        help="Path to save evaluation report"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run test cases in parallel"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of parallel workers (if --parallel is set)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print verbose output"
    )
    parser.add_argument(
        "--create-sample",
        action="store_true",
        help="Create a sample dataset instead of running evaluation"
    )
    
    return parser.parse_args()


def create_sample_dataset(dataset_path: str):
    """Create and save a sample evaluation dataset."""
    print("Creating sample dataset...")
    
    dataset = EvaluationDataset()
    dataset.create_sample_dataset()
    dataset.save_dataset(dataset_path)
    
    print(f"\n✓ Sample dataset created with {len(dataset.test_cases)} test cases")
    print(f"  Edit the file to add your own test cases: {dataset_path}")


def run_evaluation(args):
    """Run the full evaluation pipeline."""
    print("\n" + "=" * 60)
    print("CREDIT GUARDIAN AI AGENT - EVALUATION")
    print("=" * 60 + "\n")
    
    # Load dataset
    print(f"Loading dataset from: {args.dataset}")
    dataset = EvaluationDataset(args.dataset)
    
    if not dataset.test_cases:
        print("❌ No test cases found in dataset")
        print("   Run with --create-sample to create a sample dataset")
        return
    
    # Validate dataset
    validation = dataset.validate_dataset()
    print(f"\nDataset validation:")
    print(f"  Total cases:   {validation['total_cases']}")
    print(f"  Valid cases:   {validation['valid_cases']}")
    print(f"  Invalid cases: {validation['invalid_cases']}")
    
    if validation['errors']:
        print("\n⚠️  Validation errors found:")
        for error in validation['errors'][:5]:  # Show first 5 errors
            print(f"    - {error['case_id']}: {error['error']}")
    
    if validation['invalid_cases'] > 0:
        print("\n❌ Please fix dataset validation errors before continuing")
        return
    
    # Initialize agent and runner
    print("\nInitializing agent executor...")
    agent_executor = AgentExecutor()
    runner = AgentRunner(agent_executor, max_workers=args.workers)
    
    # Run test cases
    print(f"\nRunning {len(dataset.test_cases)} test cases...")
    results = runner.run_batch(
        dataset.test_cases,
        parallel=args.parallel,
        verbose=args.verbose
    )
    
    # Calculate metrics for each result
    print("\nCalculating metrics...")
    evaluated_results = []
    
    for result in results:
        if result.get("error"):
            if args.verbose:
                print(f"  Skipping {result['id']} due to error: {result['error']}")
            continue
        
        prediction = result["prediction"]
        expected = result["expected"]
        
        # Extract data for metrics
        pred_analysis = prediction.get("analysis", {})
        exp_analysis = expected.get("analysis", {})
        
        pred_violations = pred_analysis.get("violations", [])
        exp_violations = expected.get("violations", [])
        
        # Calculate all metrics
        metrics = {
            "accuracy": EvaluationMetrics.calculate_accuracy(pred_analysis, exp_analysis),
            "violation_recall": EvaluationMetrics.calculate_violation_recall(
                pred_violations, exp_violations
            ),
            "violation_precision": EvaluationMetrics.calculate_violation_precision(
                pred_violations, exp_violations
            ),
        }
        
        # Calculate F1 score
        metrics["violation_f1"] = EvaluationMetrics.calculate_f1_score(
            metrics["violation_precision"],
            metrics["violation_recall"]
        )
        
        # Calculate GPR accuracy if available
        if "gpr" in expected:
            pred_gpr = pred_analysis.get("stated_apr", 0)
            exp_gpr = expected.get("gpr", 0)
            metrics["gpr_accuracy"] = EvaluationMetrics.calculate_gpr_accuracy(
                pred_gpr, exp_gpr
            )
        
        # Calculate complaint quality if available
        if "complaint_elements" in expected:
            complaint = prediction.get("complaint", "")
            required_elements = expected.get("complaint_elements", [])
            metrics["complaint_quality"] = EvaluationMetrics.calculate_complaint_quality(
                complaint, required_elements
            )
        
        result["metrics"] = metrics
        evaluated_results.append(result)
        
        if args.verbose:
            print(f"  {result['id']}: accuracy={metrics['accuracy']:.3f}, "
                  f"f1={metrics['violation_f1']:.3f}")
    
    # Save results
    print(f"\nSaving results to: {args.output}")
    runner.save_results(args.output, evaluated_results)
    
    # Generate and save report
    print(f"Generating report...")
    metric_results = [r["metrics"] for r in evaluated_results]
    report = EvaluationMetrics.generate_report(metric_results, args.report)
    
    print("\n" + report)
    
    # Print summary statistics
    success_rate = runner.get_success_rate(results)
    avg_time = runner.get_average_execution_time(results)
    
    print("\nEXECUTION SUMMARY:")
    print(f"  Success rate:       {success_rate * 100:.1f}%")
    print(f"  Avg execution time: {avg_time:.0f}ms")
    print(f"  Report saved to:    {args.report}")
    
    print("\n" + "=" * 60)


def main():
    """Main entry point."""
    args = parse_args()
    
    try:
        if args.create_sample:
            create_sample_dataset(args.dataset)
        else:
            run_evaluation(args)
    except KeyboardInterrupt:
        print("\n\n⚠️  Evaluation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
