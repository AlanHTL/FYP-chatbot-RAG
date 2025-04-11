#!/usr/bin/env python
import argparse
import json
import os
import time
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys
from typing import Optional

# Add the parent directory to system path to import the required modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from multi_disorder_tester import DisorderTestManager
from visualize_results import ResultsVisualizer

def run_tests(results_dir: Optional[str] = None) -> Optional[str]:
    """Run all tests and save results to CSV files."""
    if results_dir is None:
        # Create timestamped results directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = os.path.join("results", f"test_results_{timestamp}")
    
    # Ensure results directory exists
    os.makedirs(results_dir, exist_ok=True)
    
    # Initialize test manager
    test_manager = DisorderTestManager(
        test_configs=[
            {
                "name": "delirium",
                "test_file": "Test json/delirium_test.json",
                "save_responses": True
            },
            {
                "name": "major depressive disorder",
                "test_file": "Test json/major_depressive_disorder_test.json",
                "save_responses": True
            },
            {
                "name": "schizophrenia",
                "test_file": "Test json/schizophrenia_test.json",
                "save_responses": True
            },
            {
                "name": "ptsd",
                "test_file": "Test json/posttraumatic_stress_disorder_test.json",
                "save_responses": True
            },
            {
                "name": "pdd",
                "test_file": "Test json/persistent_depressive_disorder_test.json",
                "save_responses": True
            },
            {
                "name": "panic",
                "test_file": "Test json/panic_disorder_test.json",
                "save_responses": True
            },
            {
                "name": "odd",
                "test_file": "Test json/oppositional_defiant_disorder_test.json",
                "save_responses": True
            },
            {
                "name": "ocd",
                "test_file": "Test json/obsessive_compulsive_disorder_test.json",
                "save_responses": True
            },
            {
                "name": "mild_ncd",
                "test_file": "Test json/mild_neurocognitive_disorder_test.json",
                "save_responses": True
            },
            {
                "name": "manic",
                "test_file": "Test json/manic_episode_test.json",
                "save_responses": True
            },
            {
                "name": "major_ncd",
                "test_file": "Test json/major_neurocognitive_disorder_test.json",
                "save_responses": True
            },
            {
                "name": "gad",
                "test_file": "Test json/generalized_anxiety_disorder_test.json",
                "save_responses": True
            },
            {
                "name": "adhd",
                "test_file": "Test json/attention_deficit_hyperactivity_disorder_test.json",
                "save_responses": True
            },
            {
                "name": "asd",
                "test_file": "Test json/autism_spectrum_disorder_test.json",
                "save_responses": True
            },
            {
                "name": "id",
                "test_file": "Test json/intellectual_disabilities_test.json",
                "save_responses": True
            },
            {
                "name": "cd",
                "test_file": "Test json/conduct_disorder_test.json",
                "save_responses": True
            },
            {
                "name": "td",
                "test_file": "Test json/tourettes_disorder_test.json",
                "save_responses": True
            }
        ],
        results_dir=results_dir,
        verbose=True
    )
    
    # Run tests
    results = test_manager.run_all_tests()
    
    if not results:
        print("Warning: No test results were generated!")
        return None
    
    # Save results to CSV
    csv_file = os.path.join(results_dir, "all_results.csv")
    try:
        df = pd.DataFrame(results)
        df.to_csv(csv_file, index=False)
        print(f"Results saved to {csv_file}")
        return csv_file
    except Exception as e:
        print(f"Error saving results to CSV: {e}")
        return None

def run_reports(disorders, num_servers=1, result_dir=None, save_responses=False, 
               verbose=False, skip_visualization=False):
    """
    Run tests and generate a full reporting package including visualizations.
    
    Args:
        disorders (dict): Dictionary mapping disorder names to their test file paths
        num_servers (int): Number of parallel test servers to use
        result_dir (str): Directory to save results (default: results_TIMESTAMP)
        save_responses (bool): Whether to save detailed chatbot responses
        verbose (bool): Whether to print detailed progress information
        skip_visualization (bool): Whether to skip generating visualizations
        
    Returns:
        tuple: (results_csv, charts_dir) paths to results CSV and charts directory
    """
    # Run all tests and get the CSV file path
    results_csv = run_tests(
        results_dir=result_dir
    )
    
    charts_dir = None
    if not skip_visualization and results_csv:
        # Generate visualizations from the results
        results_dir = os.path.dirname(results_csv)
        charts_dir = os.path.join(results_dir, "charts")
        
        # Create the visualizer
        visualizer = ResultsVisualizer(results_csv, charts_dir)
        visualizer.generate_all_visualizations()
    
    return results_csv, charts_dir

def main():
    """Main function to parse arguments and run tests"""
    parser = argparse.ArgumentParser(
        description="Run tests for all mental disorders and generate reports"
    )
    
    parser.add_argument(
        "--servers", 
        type=int, 
        default=3,  # Changed default to 3 servers
        help="Number of parallel test servers to use"
    )
    
    parser.add_argument(
        "--output", 
        type=str, 
        default=None,
        help="Directory to save test results"
    )
    
    parser.add_argument(
        "--save-responses", 
        action="store_true",
        help="Save detailed chatbot responses"
    )
    
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Print detailed progress information"
    )
    
    parser.add_argument(
        "--no-visualization", 
        action="store_true",
        help="Skip generating visualizations"
    )
    
    args = parser.parse_args()
    
    # Create a dictionary of all test files in the Test json directory
    test_dir = "Test json"
    disorders = {}
    for file in os.listdir(test_dir):
        if file.endswith("_test.json"):
            disorder_name = file.replace("_test.json", "")
            disorders[disorder_name] = os.path.join(test_dir, file)
    
    if not disorders:
        print("No disorders found to test. Exiting.")
        return 1
    
    # Run tests and generate reports
    results_csv, charts_dir = run_reports(
        disorders=disorders,
        num_servers=args.servers,
        result_dir=args.output,
        save_responses=args.save_responses,
        verbose=args.verbose,
        skip_visualization=args.no_visualization
    )
    
    if results_csv:
        print("\nTest run completed successfully!")
        print(f"Results CSV: {results_csv}")
        if charts_dir:
            print(f"Charts directory: {charts_dir}")
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main()) 