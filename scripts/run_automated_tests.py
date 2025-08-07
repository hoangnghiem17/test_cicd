#!/usr/bin/env python3
"""
Automated testing script for CD-Test pipeline.
Compares application output against reference data and generates binary results.
"""

import json
import sys
import os
from pathlib import Path

# Add the project root to Python path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import fetch_greeting


def load_test_data():
    """Load test input data from JSON file."""
    test_data_path = Path(__file__).parent.parent / "test_data" / "input_data.json"
    with open(test_data_path, 'r') as f:
        return json.load(f)


def load_reference_data():
    """Load reference expected results from JSON file."""
    reference_data_path = Path(__file__).parent.parent / "test_data" / "reference_data.json"
    with open(reference_data_path, 'r') as f:
        return json.load(f)


def run_tests():
    """
    Run automated tests comparing current app output with reference data.
    Returns list of binary results (1 for pass, 0 for fail) and overall success status.
    """
    print("Loading test data...")
    test_data = load_test_data()
    reference_data = load_reference_data()
    
    # Create results dictionary for easier matching
    reference_dict = {item['id']: item for item in reference_data}
    
    results = []
    detailed_results = []
    
    print(f"Running {len(test_data)} automated tests...")
    
    for test_case in test_data:
        test_id = test_case['id']
        endpoint = test_case['endpoint']
        description = test_case['description']
        
        # Get reference data for this test case
        if test_id not in reference_dict:
            print(f"ERROR: No reference data found for test ID {test_id}")
            results.append(0)
            continue
            
        reference = reference_dict[test_id]
        expected_result = reference['expected_result']
        
        print(f"Test {test_id}: {description}")
        print(f"  Testing endpoint: {endpoint}")
        
        try:
            # Run the application with test data
            actual_result = fetch_greeting(endpoint)
            
            # Compare with reference
            test_passed = (actual_result == expected_result)
            binary_result = 1 if test_passed else 0
            
            results.append(binary_result)
            detailed_results.append({
                'id': test_id,
                'description': description,
                'endpoint': endpoint,
                'expected': expected_result,
                'actual': actual_result,
                'passed': test_passed,
                'binary_result': binary_result
            })
            
            status = "PASS" if test_passed else "FAIL"
            print(f"  Expected: {expected_result}")
            print(f"  Actual:   {actual_result}")
            print(f"  Result:   {status} ({binary_result})")
            
        except Exception as e:
            print(f"  ERROR: Exception during test execution: {e}")
            results.append(0)
            detailed_results.append({
                'id': test_id,
                'description': description,
                'endpoint': endpoint,
                'expected': expected_result,
                'actual': f"ERROR: {str(e)}",
                'passed': False,
                'binary_result': 0
            })
        
        print()
    
    return results, detailed_results


def save_results(binary_results, detailed_results):
    """Save test results to output files."""
    output_dir = Path(__file__).parent.parent / "test_results"
    output_dir.mkdir(exist_ok=True)
    
    # Save binary results (main requirement)
    binary_results_path = output_dir / "binary_results.txt"
    with open(binary_results_path, 'w') as f:
        for result in binary_results:
            f.write(f"{result}\n")
    
    # Save detailed results for debugging
    detailed_results_path = output_dir / "detailed_results.json"
    with open(detailed_results_path, 'w') as f:
        json.dump(detailed_results, f, indent=2)
    
    print(f"Binary results saved to: {binary_results_path}")
    print(f"Detailed results saved to: {detailed_results_path}")
    
    return binary_results_path


def main():
    """Main function for automated testing."""
    print("=" * 60)
    print("AUTOMATED TESTING - CD-Test Pipeline")
    print("=" * 60)
    
    try:
        # Run tests
        binary_results, detailed_results = run_tests()
        
        # Save results
        results_file = save_results(binary_results, detailed_results)
        
        # Calculate summary
        total_tests = len(binary_results)
        passed_tests = sum(binary_results)
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total tests:    {total_tests}")
        print(f"Passed:         {passed_tests}")
        print(f"Failed:         {failed_tests}")
        print(f"Success rate:   {success_rate:.1f}%")
        print(f"Binary results: {binary_results}")
        
        # Exit with appropriate code
        if failed_tests == 0:
            print("\n✅ ALL TESTS PASSED - Pipeline can proceed")
            sys.exit(0)
        else:
            print(f"\n❌ {failed_tests} TESTS FAILED - Pipeline should be blocked")
            sys.exit(1)
            
    except Exception as e:
        print(f"FATAL ERROR during automated testing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 