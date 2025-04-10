#!/usr/bin/env python3
import argparse
import json
import os
from datetime import datetime
import sys
from multi_disorder_tester import DisorderTestManager
from visualize_results import ResultsVisualizer

def load_disorder_list(json_file):
    """Load the list of disorder test files from JSON."""
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
            return data
    except Exception as e:
        print(f"Error loading disorder list: {e}")
        return {}

def get_disorder_names(json_file):
    """Get a list of disorder names from the disorder dictionary."""
    disorders = load_disorder_list(json_file)
    return list(disorders.keys())

def main():
    # Get list of available disorders for the help text
    available_disorders = get_disorder_names("disorder_test_files.json")
    disorder_list_str = ", ".join(available_disorders)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run tests for specific mental disorders")
    parser.add_argument("disorders", nargs="+", 
                       help=f"Disorders to test. Available: {disorder_list_str[:100]}... (and others)")
    parser.add_argument("--servers", type=int, default=1,
                       help="Number of servers to use (default: 1)")
    parser.add_argument("--port", type=int, default=8081,
                       help="Base port for API servers (default: 8081)")
    parser.add_argument("--visualize", action="store_true",
                       help="Generate visualizations after testing")
    parser.add_argument("--save-responses", action="store_true",
                       help="Save detailed chatbot responses")
    parser.add_argument("--verbose", action="store_true",
                       help="Print detailed progress information")
    
    args = parser.parse_args()
    
    # Create timestamp for this test run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = f"quick_test_{timestamp}"
    results_csv = os.path.join(results_dir, "test_results.csv")
    
    print(f"Starting test for disorders: {', '.join(args.disorders)}")
    print(f"Results will be saved to: {results_dir}")
    
    # Load all available disorders
    all_disorders = load_disorder_list("disorder_test_files.json")
    
    # Filter to only include the requested disorders
    selected_disorders = {}
    for name in args.disorders:
        matched = False
        # Try to match by substring
        for disorder_name, file_path in all_disorders.items():
            if name.lower() in disorder_name.lower():
                selected_disorders[disorder_name] = file_path
                matched = True
        
        if not matched:
            print(f"Warning: No match found for '{name}'")
    
    if not selected_disorders:
        print("No matching disorders found. Exiting.")
        return 1
    
    print(f"Will test the following disorders: {', '.join(selected_disorders.keys())}")
    
    # Create test configurations
    test_configs = []
    for disorder_name, test_file in selected_disorders.items():
        test_configs.append({
            "name": disorder_name,
            "test_file": test_file,
            "save_responses": args.save_responses
        })
    
    # Create and run the test manager
    manager = DisorderTestManager(
        test_configs=test_configs,
        num_servers=args.servers,
        base_port=args.port,
        results_dir=results_dir,
        verbose=args.verbose
    )
    
    # Run the tests
    results = manager.run_all_tests()
    
    # Generate CSV report
    manager.generate_csv_report(results, results_csv)
    
    # Generate visualizations if requested
    if args.visualize:
        print("Generating visualizations...")
        charts_dir = os.path.join(results_dir, "charts")
        visualizer = ResultsVisualizer(results_csv, charts_dir)
        visualizer.generate_all_visualizations()
        print(f"Visualizations saved to {charts_dir}")
    
    print("\n=== TESTING SUMMARY ===")
    print(f"Tested {len(results)} disorder types")
    print(f"Results saved to: {results_dir}")
    print(f"CSV report: {results_csv}")
    if args.visualize:
        print(f"Visualizations: {os.path.join(results_dir, 'charts')}")
    print("=======================")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 