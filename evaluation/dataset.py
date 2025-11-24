"""
Test dataset management for evaluation.

Provides utilities for:
- Loading test datasets
- Creating synthetic test cases
- Managing ground truth data
"""
import json
from typing import Dict, Any, List
from pathlib import Path


class EvaluationDataset:
    """
    Dataset manager for evaluation test cases.
    """
    
    def __init__(self, dataset_path: str = None):
        """
        Initialize dataset manager.
        
        Args:
            dataset_path: Optional path to existing dataset JSON file
        """
        self.dataset_path = dataset_path
        self.test_cases = []
        
        if dataset_path and Path(dataset_path).exists():
            self.load_dataset(dataset_path)
    
    def load_dataset(self, path: str) -> List[Dict[str, Any]]:
        """
        Load test dataset from JSON file.
        
        Args:
            path: Path to dataset JSON file
            
        Returns:
            List of test cases
        """
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self.test_cases = data.get("test_cases", [])
        return self.test_cases
    
    def save_dataset(self, path: str) -> None:
        """
        Save test dataset to JSON file.
        
        Args:
            path: Path to save dataset
        """
        data = {
            "version": "1.0",
            "description": "Credit Guardian AI Agent Evaluation Dataset",
            "test_cases": self.test_cases
        }
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Dataset saved to: {path}")
    
    def add_test_case(
        self,
        test_id: str,
        pdf_path: str,
        user_data: Dict[str, str],
        expected_analysis: Dict[str, Any],
        expected_violations: List[str],
        description: str = ""
    ) -> None:
        """
        Add a test case to the dataset.
        
        Args:
            test_id: Unique identifier for test case
            pdf_path: Path to test PDF file
            user_data: User information dictionary
            expected_analysis: Expected contract analysis output
            expected_violations: List of expected violations
            description: Optional description of test case
        """
        test_case = {
            "id": test_id,
            "description": description,
            "input": {
                "pdf_path": pdf_path,
                "user": user_data
            },
            "expected": {
                "analysis": expected_analysis,
                "violations": expected_violations
            }
        }
        
        self.test_cases.append(test_case)
    
    def get_test_cases(self, filter_ids: List[str] = None) -> List[Dict[str, Any]]:
        """
        Get test cases, optionally filtered by IDs.
        
        Args:
            filter_ids: Optional list of test case IDs to include
            
        Returns:
            List of test cases
        """
        if not filter_ids:
            return self.test_cases
        
        return [tc for tc in self.test_cases if tc.get("id") in filter_ids]
    
    def create_sample_dataset(self) -> List[Dict[str, Any]]:
        """
        Create a sample dataset with synthetic test cases.
        
        Returns:
            List of sample test cases
        """
        sample_cases = [
            {
                "id": "test_case_001",
                "description": "Standard consumer loan with hidden fees",
                "input": {
                    "pdf_path": "tests/fixtures/sample_contract_001.pdf",
                    "user": {
                        "name": "Иван Петров",
                        "address": "гр. София, ул. Витоша 123"
                    }
                },
                "expected": {
                    "analysis": {
                        "contract_number": "K-2024-001234",
                        "creditor": "Бързи Кредити ЕООД",
                        "principal": 5000.0,
                        "stated_apr": 35.5,
                        "fees": [
                            {"name": "Такса управление", "amount": 50.0, "frequency": "месечна"},
                            {"name": "Такса оценка", "amount": 150.0, "frequency": "еднократна"}
                        ],
                        "violations": [
                            "Неразкрита информация за действителния ГПР",
                            "Скрита такса за управление на сметка",
                            "Неравноправна клауза за едностранно изменение"
                        ]
                    },
                    "violations": [
                        "Неразкрита информация за действителния ГПР",
                        "Скрита такса за управление на сметка",
                        "Неравноправна клауза за едностранно изменение"
                    ],
                    "gpr": 45.8,
                    "complaint_elements": [
                        "жалба",
                        "КЗП",
                        "потребител",
                        "договор",
                        "нарушение"
                    ]
                }
            },
            {
                "id": "test_case_002",
                "description": "Payday loan with excessive APR",
                "input": {
                    "pdf_path": "tests/fixtures/sample_contract_002.pdf",
                    "user": {
                        "name": "Мария Георгиева",
                        "address": "гр. Пловдив, бул. Цар Борис III №45"
                    }
                },
                "expected": {
                    "analysis": {
                        "contract_number": "PL-2024-05678",
                        "creditor": "Експрес Финанс АД",
                        "principal": 1000.0,
                        "stated_apr": 120.0,
                        "fees": [
                            {"name": "Административна такса", "amount": 100.0, "frequency": "еднократна"}
                        ],
                        "violations": [
                            "ГПР над законовия лихвен таван",
                            "Недостатъчна информация за правото на предсрочно погасяване",
                            "Липсва ясна информация за начина на изчисление на ГПР"
                        ]
                    },
                    "violations": [
                        "ГПР над законовия лихвен таван",
                        "Недостатъчна информация за правото на предсрочно погасяване",
                        "Липсва ясна информация за начина на изчисление на ГПР"
                    ],
                    "gpr": 145.0,
                    "complaint_elements": [
                        "жалба",
                        "КЗП",
                        "лихвен таван",
                        "договор",
                        "нарушение"
                    ]
                }
            },
            {
                "id": "test_case_003",
                "description": "Clean contract with no violations",
                "input": {
                    "pdf_path": "tests/fixtures/sample_contract_003.pdf",
                    "user": {
                        "name": "Георги Димитров",
                        "address": "гр. Варна, кв. Младост 15"
                    }
                },
                "expected": {
                    "analysis": {
                        "contract_number": "CL-2024-09876",
                        "creditor": "Надеждна Банка АД",
                        "principal": 10000.0,
                        "stated_apr": 12.5,
                        "fees": [
                            {"name": "Застрахователна премия", "amount": 50.0, "frequency": "месечна"}
                        ],
                        "violations": []
                    },
                    "violations": [],
                    "gpr": 13.2,
                    "complaint_elements": []
                }
            }
        ]
        
        self.test_cases = sample_cases
        return sample_cases
    
    def validate_dataset(self) -> Dict[str, Any]:
        """
        Validate dataset structure and completeness.
        
        Returns:
            Validation report dictionary
        """
        report = {
            "total_cases": len(self.test_cases),
            "valid_cases": 0,
            "invalid_cases": 0,
            "errors": []
        }
        
        required_keys = ["id", "input", "expected"]
        
        for i, test_case in enumerate(self.test_cases):
            case_id = test_case.get("id", f"case_{i}")
            
            # Check required keys
            missing_keys = [k for k in required_keys if k not in test_case]
            if missing_keys:
                report["invalid_cases"] += 1
                report["errors"].append({
                    "case_id": case_id,
                    "error": f"Missing required keys: {missing_keys}"
                })
                continue
            
            # Check input structure
            if "pdf_path" not in test_case["input"]:
                report["invalid_cases"] += 1
                report["errors"].append({
                    "case_id": case_id,
                    "error": "Missing pdf_path in input"
                })
                continue
            
            report["valid_cases"] += 1
        
        return report
