"""
Agent runner for executing test cases and collecting evaluation data.

Provides infrastructure for:
- Running agent on test datasets
- Collecting responses and traces
- Handling errors gracefully
- Parallel execution support
"""
import asyncio
import time
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed


class AgentRunner:
    """
    Runner for executing the AI agent against test datasets.
    
    Supports both synchronous and asynchronous execution,
    with built-in error handling and performance tracking.
    """
    
    def __init__(self, agent_executor, max_workers: int = 4):
        """
        Initialize the agent runner.
        
        Args:
            agent_executor: Instance of AgentExecutor to run
            max_workers: Maximum number of parallel workers
        """
        self.agent_executor = agent_executor
        self.max_workers = max_workers
        self.results = []
    
    def run_single(
        self,
        test_case: Dict[str, Any],
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Run agent on a single test case.
        
        Args:
            test_case: Test case dictionary with 'input' and 'expected' keys
            verbose: Whether to print progress information
            
        Returns:
            Result dictionary with prediction, expected, metrics, and timing
        """
        case_id = test_case.get("id", "unknown")
        
        if verbose:
            print(f"Running test case: {case_id}")
        
        start_time = time.time()
        error = None
        prediction = None
        
        try:
            # Extract input data
            pdf_path = test_case["input"]["pdf_path"]
            user_data = test_case["input"].get("user", {})
            
            # Run agent
            prediction = self.agent_executor.process(pdf_path, user_data)
            
        except Exception as e:
            error = str(e)
            if verbose:
                print(f"  Error: {error}")
        
        execution_time = time.time() - start_time
        
        result = {
            "id": case_id,
            "prediction": prediction,
            "expected": test_case.get("expected", {}),
            "execution_time_ms": int(execution_time * 1000),
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if verbose and not error:
            print(f"  Completed in {result['execution_time_ms']}ms")
        
        return result
    
    def run_batch(
        self,
        test_cases: List[Dict[str, Any]],
        parallel: bool = True,
        verbose: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Run agent on a batch of test cases.
        
        Args:
            test_cases: List of test case dictionaries
            parallel: Whether to run in parallel
            verbose: Whether to print progress
            
        Returns:
            List of result dictionaries
        """
        if verbose:
            print(f"\n{'='*60}")
            print(f"Running {len(test_cases)} test cases...")
            print(f"{'='*60}\n")
        
        results = []
        
        if parallel and len(test_cases) > 1:
            # Parallel execution
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {
                    executor.submit(self.run_single, tc, verbose): tc
                    for tc in test_cases
                }
                
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        test_case = futures[future]
                        results.append({
                            "id": test_case.get("id", "unknown"),
                            "error": str(e),
                            "prediction": None,
                            "expected": test_case.get("expected", {})
                        })
        else:
            # Sequential execution
            for test_case in test_cases:
                result = self.run_single(test_case, verbose)
                results.append(result)
        
        self.results.extend(results)
        
        if verbose:
            success_count = sum(1 for r in results if not r.get("error"))
            print(f"\n{'='*60}")
            print(f"Completed: {success_count}/{len(results)} successful")
            print(f"{'='*60}\n")
        
        return results
    
    def save_results(
        self,
        output_path: str,
        results: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Save evaluation results to a JSON file.
        
        Args:
            output_path: Path to save results
            results: Optional results list (uses self.results if not provided)
        """
        results_to_save = results or self.results
        
        output_data = {
            "run_timestamp": datetime.utcnow().isoformat(),
            "total_cases": len(results_to_save),
            "successful_cases": sum(1 for r in results_to_save if not r.get("error")),
            "results": results_to_save
        }
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Results saved to: {output_path}")
    
    def load_results(self, input_path: str) -> List[Dict[str, Any]]:
        """
        Load previously saved results from a JSON file.
        
        Args:
            input_path: Path to results file
            
        Returns:
            List of result dictionaries
        """
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return data.get("results", [])
    
    @staticmethod
    def filter_results(
        results: List[Dict[str, Any]],
        filter_fn: Callable[[Dict[str, Any]], bool]
    ) -> List[Dict[str, Any]]:
        """
        Filter results based on a predicate function.
        
        Args:
            results: List of result dictionaries
            filter_fn: Function that returns True for results to keep
            
        Returns:
            Filtered list of results
        """
        return [r for r in results if filter_fn(r)]
    
    @staticmethod
    def get_success_rate(results: List[Dict[str, Any]]) -> float:
        """
        Calculate success rate from results.
        
        Args:
            results: List of result dictionaries
            
        Returns:
            Success rate between 0.0 and 1.0
        """
        if not results:
            return 0.0
        
        success_count = sum(1 for r in results if not r.get("error"))
        return success_count / len(results)
    
    @staticmethod
    def get_average_execution_time(results: List[Dict[str, Any]]) -> float:
        """
        Calculate average execution time from results.
        
        Args:
            results: List of result dictionaries
            
        Returns:
            Average execution time in milliseconds
        """
        if not results:
            return 0.0
        
        times = [r.get("execution_time_ms", 0) for r in results if not r.get("error")]
        return sum(times) / len(times) if times else 0.0
