#!/usr/bin/env python
"""
Test Frontend Components
Проверява дали frontend компонентите са правилно структурирани
"""

import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
FRONTEND_ROOT = PROJECT_ROOT / "frontend"

def check_file_exists(file_path, description):
    """Check if file exists"""
    if file_path.exists():
        print(f"[OK] {description}: {file_path.name}")
        return True
    else:
        print(f"[FAIL] {description}: NOT FOUND ({file_path.name})")
        return False

def check_component_file(component_name):
    """Check if component file exists"""
    component_path = FRONTEND_ROOT / "src" / "components" / f"{component_name}.jsx"
    return check_file_exists(component_path, f"Component {component_name}")

def main():
    """Test frontend structure"""
    print("=" * 70)
    print("FRONTEND COMPONENTS TEST")
    print("=" * 70)
    
    results = []
    
    # Check main files
    print("\nMain Files:")
    results.append(check_file_exists(FRONTEND_ROOT / "package.json", "package.json"))
    results.append(check_file_exists(FRONTEND_ROOT / "src" / "App.jsx", "App.jsx"))
    results.append(check_file_exists(FRONTEND_ROOT / "src" / "main.jsx", "main.jsx"))
    results.append(check_file_exists(FRONTEND_ROOT / "vite.config.js", "vite.config.js"))
    results.append(check_file_exists(FRONTEND_ROOT / "tailwind.config.js", "tailwind.config.js"))
    
    # Check components
    print("\nComponents:")
    components = [
        "LandingPage",
        "SubscriptionForm",
        "TrustIndicators",
        "Header",
        "Footer",
        "Dashboard",
        "CreditorSearch",
        "CreditorList",
        "GPRCalculator",
        "ContractAnalyzer",
    ]
    
    for component in components:
        results.append(check_component_file(component))
    
    # Check UI components
    print("\nUI Components:")
    ui_components = [
        "Button",
        "Input",
        "Card",
        "Alert",
        "Badge",
        "Spinner",
    ]
    
    for component in ui_components:
        ui_path = FRONTEND_ROOT / "src" / "components" / "ui" / f"{component}.jsx"
        results.append(check_file_exists(ui_path, f"UI Component {component}"))
    
    # Check API client
    print("\nAPI Files:")
    api_path = FRONTEND_ROOT / "src" / "api" / "client.js"
    results.append(check_file_exists(api_path, "API Client"))
    
    # Check package.json for dependencies
    print("\nChecking package.json:")
    try:
        with open(FRONTEND_ROOT / "package.json", 'r') as f:
            package = json.load(f)
            deps = package.get('dependencies', {})
            dev_deps = package.get('devDependencies', {})
            
            required_deps = ['react', 'react-dom', 'axios', 'react-router-dom']
            required_dev_deps = ['vite', 'tailwindcss', '@vitejs/plugin-react']
            
            print("  Dependencies:")
            for dep in required_deps:
                if dep in deps:
                    print(f"    [OK] {dep}: {deps[dep]}")
                else:
                    print(f"    [FAIL] {dep}: MISSING")
                    results.append(False)
            
            print("  Dev Dependencies:")
            for dep in required_dev_deps:
                if dep in dev_deps:
                    print(f"    [OK] {dep}: {dev_deps[dep]}")
                else:
                    print(f"    [FAIL] {dep}: MISSING")
                    results.append(False)
    except Exception as e:
        print(f"  ❌ Error reading package.json: {e}")
        results.append(False)
    
    # Summary
    print("\n" + "=" * 70)
    print("FRONTEND TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for r in results if r)
    total = len(results)
    
    print(f"Total Checks: {total}")
    print(f"[OK] Passed: {passed}")
    print(f"[FAIL] Failed: {total - passed}")
    print("=" * 70)
    
    if passed == total:
        print("[SUCCESS] ALL FRONTEND CHECKS PASSED!")
        return 0
    else:
        print(f"[FAIL] {total - passed} CHECK(S) FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())

