#!/usr/bin/env python
import argparse
import json
import os
import time
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys

# Add the parent directory to system path to import the required modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from multi_disorder_tester import DisorderTestManager
from visualize_results import ResultsVisualizer


def load_disorder_list(disorder_file="disorder_test_files.json"):
    """
    Load the list of disorders and their test files from JSON.
    
    Args:
        disorder_file (str): Path to the JSON file with disorder test files
        
    Returns:
        dict: Dictionary mapping disorder names to their test file paths
    """
    try:
        with open(disorder_file, 'r') as f:
            disorder_data = json.load(f)
        
        # Check if the expected data structure is present
        if not isinstance(disorder_data, dict):
            print(f"Error: {disorder_file} does not contain a valid disorder dictionary")
            return {}
            
        return disorder_data
    except Exception as e:
        print(f"Error loading disorder list from {disorder_file}: {e}")
        return {}


def run_tests(disorders, num_servers=1, result_dir=None, save_responses=False, verbose=False):
    """
    Run tests for all specified disorders using parallel servers.
    
    Args:
        disorders (dict): Dictionary mapping disorder names to their test file paths
        num_servers (int): Number of parallel test servers to use
        result_dir (str): Directory to save results (default: results_TIMESTAMP)
        save_responses (bool): Whether to save detailed chatbot responses
        verbose (bool): Whether to print detailed progress information
        
    Returns:
        str: Path to the generated results CSV file
    """
    # Create timestamp for result directory if not specified
    if result_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_dir = f"results_{timestamp}"
    
    # Create results directory if it doesn't exist
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
        
    print(f"Starting test run with {num_servers} servers for {len(disorders)} disorders")
    print(f"Results will be saved to: {result_dir}")
    
    # Create test configurations for all disorders
    test_configs = []
    for disorder_name, test_file in disorders.items():
        # Skip disorders with missing test files
        if not os.path.exists(test_file):
            print(f"Warning: Test file {test_file} for {disorder_name} not found. Skipping.")
            continue
            
        # Create a configuration for each disorder
        test_configs.append({
            "name": disorder_name,
            "test_file": test_file,
            "result_dir": result_dir,
            "save_responses": save_responses
        })
        
    # Start the tests
    start_time = time.time()
    
    # Initialize the multi-disorder tester
    tester = DisorderTestManager(
        test_configs=test_configs,
        num_servers=num_servers,
        verbose=verbose
    )
    
    # Run all tests
    results = tester.run_all_tests()
    
    # Calculate the total time taken
    elapsed_time = time.time() - start_time
    
    # Create a pandas DataFrame with the results
    results_df = pd.DataFrame(results)
    
    # Add elapsed time information
    print(f"Tests completed in {elapsed_time:.2f} seconds")
    print(f"Average time per disorder: {elapsed_time / len(disorders):.2f} seconds")
    
    # Save the results to a CSV file
    results_csv = os.path.join(result_dir, "test_results.csv")
    results_df.to_csv(results_csv, index=False)
    print(f"Results saved to {results_csv}")
    
    return results_csv


def generate_visualizations(results_csv, output_dir=None):
    """
    Generate visualizations from the test results.
    
    Args:
        results_csv (str): Path to the CSV file with test results
        output_dir (str): Directory to save visualizations (default is within results dir)
        
    Returns:
        bool: True if visualizations were generated successfully
    """
    if output_dir is None:
        # Use a charts subdirectory within the results directory
        results_dir = os.path.dirname(results_csv)
        output_dir = os.path.join(results_dir, "charts")
    
    print(f"Generating visualizations in: {output_dir}")
    
    # Create the visualizer
    visualizer = ResultsVisualizer(results_csv, output_dir)
    
    # Generate all visualizations
    success = visualizer.generate_all_visualizations()
    
    if success:
        print(f"Visualizations saved to {output_dir}")
        return True
    else:
        print("Failed to generate visualizations")
        return False


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
        disorders=disorders,
        num_servers=num_servers,
        result_dir=result_dir,
        save_responses=save_responses,
        verbose=verbose
    )
    
    charts_dir = None
    if not skip_visualization and results_csv:
        # Generate visualizations from the results
        results_dir = os.path.dirname(results_csv)
        charts_dir = os.path.join(results_dir, "charts")
        
        generate_visualizations(results_csv, charts_dir)
    
    return results_csv, charts_dir


def main():
    """Main function to parse arguments and run tests"""
    parser = argparse.ArgumentParser(
        description="Run tests for all mental disorders and generate reports"
    )
    
    parser.add_argument(
        "--disorders", 
        type=str, 
        default="disorder_test_files.json",
        help="Path to JSON file with disorder test files"
    )
    
    parser.add_argument(
        "--servers", 
        type=int, 
        default=1,
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
    
    # Load the disorder list
    disorders = load_disorder_list(args.disorders)
    
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
        print(f"Results available at: {results_csv}")
        
        if charts_dir and not args.no_visualization:
            print(f"Visualizations available at: {charts_dir}")
        
        return 0
    else:
        print("\nTest run failed to complete.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 