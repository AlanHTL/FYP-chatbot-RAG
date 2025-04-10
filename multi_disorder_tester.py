import os
import json
import time
import subprocess
import concurrent.futures
import pandas as pd
import glob
import csv
import argparse
import re
import signal
from typing import List, Dict, Any, Tuple
import socket

# Define constants
DEFAULT_BASE_PORT = 8081
MAX_SERVERS = 5  # Maximum number of API servers to run in parallel
MAX_WORKERS_PER_SERVER = 3  # Maximum test workers per server

class DisorderTestManager:
    """Manager for testing multiple disorder types in parallel."""

    def __init__(self, 
                 test_files_dir: str = ".", 
                 base_port: int = DEFAULT_BASE_PORT,
                 max_servers: int = MAX_SERVERS,
                 results_dir: str = "results",
                 test_subset: List[str] = None,
                 test_configs: List[Dict[str, Any]] = None,
                 num_servers: int = None,
                 verbose: bool = False):
        """
        Initialize the test manager.
        
        Args:
            test_files_dir: Directory containing the test JSON files
            base_port: Starting port number for API servers
            max_servers: Maximum number of API servers to run in parallel
            results_dir: Directory to save test results
            test_subset: List of disorder names to test (if None, test all)
            test_configs: List of test configurations for each disorder
            num_servers: Number of API servers to run (overrides max_servers if provided)
            verbose: Whether to print detailed progress information
        """
        self.test_files_dir = test_files_dir
        self.base_port = base_port
        self.max_servers = num_servers if num_servers is not None else max_servers
        self.results_dir = results_dir
        self.test_subset = test_subset
        self.api_processes = {}  # Maps port to subprocess
        self.verbose = verbose
        self.test_configs = test_configs or []
        
        # Ensure results directory exists
        os.makedirs(results_dir, exist_ok=True)
        
        # Log configuration if verbose
        if self.verbose:
            print(f"DisorderTestManager initialized with:")
            print(f"  - max_servers: {self.max_servers}")
            print(f"  - base_port: {self.base_port}")
            print(f"  - results_dir: {self.results_dir}")
            print(f"  - test_configs: {len(self.test_configs)} configurations")

    def find_test_files(self) -> List[Tuple[str, str]]:
        """
        Find all disorder test files in the test directory.
        
        Returns:
            List of tuples (disorder_name, file_path)
        """
        test_files = []
        
        # If test_configs is provided, use those instead of searching for files
        if self.test_configs:
            for config in self.test_configs:
                disorder_name = config.get("name", "unknown")
                test_file = config.get("test_file")
                if test_file and os.path.exists(test_file):
                    test_files.append((disorder_name, test_file))
                else:
                    print(f"Warning: Test file for {disorder_name} not found: {test_file}")
            return test_files
        
        # Otherwise, find all JSON files with pattern *_test.json
        for file_path in glob.glob(os.path.join(self.test_files_dir, "*_test.json")):
            file_name = os.path.basename(file_path)
            # Extract disorder name from filename
            match = re.match(r"(.+)_test\.json", file_name)
            if match:
                disorder_name = match.group(1)
                
                # If test_subset is provided, only include disorders in the subset
                if not self.test_subset or disorder_name in self.test_subset:
                    test_files.append((disorder_name, file_path))
        
        if self.verbose:
            print(f"Found {len(test_files)} disorder test files")
        return test_files

    def is_port_available(self, port: int) -> bool:
        """Check if a port is available for use."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0

    def start_api_server(self, port: int) -> subprocess.Popen:
        """
        Start the API server on the specified port.
        
        Args:
            port: Port to run the server on
            
        Returns:
            Process handle for the API server
        """
        if not self.is_port_available(port):
            raise ValueError(f"Port {port} is already in use")
        
        # Set environment variables for the API server
        env = os.environ.copy()
        env["API_PORT"] = str(port)
        
        print(f"Starting API server on port {port}...")
        api_process = subprocess.Popen(
            ["python", "api.py"], 
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for the server to start
        time.sleep(5)
        
        # Check if the server started successfully
        if api_process.poll() is not None:
            print("Error: API server failed to start")
            stdout, stderr = api_process.communicate()
            print(f"Server output: {stdout}")
            print(f"Server error: {stderr}")
            raise RuntimeError(f"Failed to start API server on port {port}")
        
        print(f"API server started successfully on port {port}")
        return api_process

    def stop_api_server(self, port: int):
        """Stop the API server running on the specified port."""
        if port not in self.api_processes:
            print(f"No API server running on port {port}")
            return
        
        api_process = self.api_processes[port]
        print(f"Stopping API server on port {port}...")
        
        # Send termination signal
        if os.name == 'nt':  # Windows
            api_process.terminate()
        else:  # Unix/Linux
            os.kill(api_process.pid, signal.SIGTERM)
        
        # Wait for the process to terminate
        try:
            api_process.wait(timeout=10)
            print(f"API server on port {port} stopped successfully")
        except subprocess.TimeoutExpired:
            print(f"API server on port {port} did not stop gracefully, forcing termination...")
            api_process.kill()
            api_process.wait()
        
        del self.api_processes[port]

    def run_test(self, disorder_name: str, test_file_path: str, port: int, 
                 save_responses: bool = False) -> Dict[str, Any]:
        """
        Run tests for a specific disorder type using the specified API server port.
        
        Args:
            disorder_name: Name of the disorder being tested
            test_file_path: Path to the test JSON file
            port: Port of the API server to use
            save_responses: Whether to save detailed chatbot responses
            
        Returns:
            Dictionary containing test results
        """
        if self.verbose:
            print(f"Testing {disorder_name} using API server on port {port}...")
        
        # Create result filename
        result_file = os.path.join(self.results_dir, f"{disorder_name}_results.json")
        
        # Build command arguments
        cmd = [
            "python", "chatbot_tester.py", 
            "--file", test_file_path, 
            "--save", result_file,
            "--parallel", str(MAX_WORKERS_PER_SERVER)
        ]
        
        # Add save-responses flag if requested
        if save_responses:
            cmd.append("--save-responses")
        
        # Set environment variable for the API URL
        env = os.environ.copy()
        env["CHATBOT_API_URL"] = f"http://127.0.0.1:{port}/chat"
        
        if self.verbose:
            print(f"Running command: {' '.join(cmd)}")
            print(f"Using API URL: {env['CHATBOT_API_URL']}")
        
        try:
            process = subprocess.run(
                cmd, 
                env=env,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if self.verbose:
                print(f"Test completed for {disorder_name}")
            
            # Load and return the results
            if os.path.exists(result_file):
                with open(result_file, 'r') as f:
                    results = json.load(f)
                
                # Extract the metrics from the results
                accuracy_metrics = results.get("accuracy_metrics", {})
                
                # Create a standardized result dictionary
                return {
                    "Disorder": disorder_name,
                    "Accuracy": accuracy_metrics.get("overall_accuracy", 0),
                    "True_Positive_Rate": accuracy_metrics.get("true_positive_rate", 0),
                    "True_Negative_Rate": accuracy_metrics.get("true_negative_rate", 0),
                    "False_Positive_Rate": accuracy_metrics.get("false_positive_rate", 0),
                    "False_Negative_Rate": accuracy_metrics.get("false_negative_rate", 0),
                    "Precision": accuracy_metrics.get("precision", 0),
                    "F1_Score": accuracy_metrics.get("f1_score", 0),
                    "Total_Cases": results.get("total_cases", 0),
                    "Total_Correct": results.get("total_correct", 0),
                    "results_file": result_file,
                }
            else:
                print(f"Warning: Results file not found for {disorder_name}")
                return {
                    "Disorder": disorder_name,
                    "Accuracy": 0,
                    "True_Positive_Rate": 0,
                    "True_Negative_Rate": 0,
                    "False_Positive_Rate": 0,
                    "False_Negative_Rate": 0,
                    "Precision": 0,
                    "F1_Score": 0,
                    "Total_Cases": 0,
                    "Total_Correct": 0,
                    "results_file": result_file,
                    "error": "Results file not found"
                }
                
        except subprocess.CalledProcessError as e:
            print(f"Error testing {disorder_name}: {e}")
            print(f"stdout: {e.stdout}")
            print(f"stderr: {e.stderr}")
            return {
                "Disorder": disorder_name,
                "Accuracy": 0,
                "True_Positive_Rate": 0,
                "True_Negative_Rate": 0,
                "False_Positive_Rate": 0,
                "False_Negative_Rate": 0,
                "Precision": 0,
                "F1_Score": 0,
                "Total_Cases": 0,
                "Total_Correct": 0,
                "results_file": result_file,
                "error": str(e)
            }

    def run_all_tests(self) -> List[Dict[str, Any]]:
        """
        Run tests for all disorder types in parallel.
        
        Returns:
            List of result dictionaries for each disorder
        """
        # Find all test files
        test_files = self.find_test_files()
        if not test_files:
            print("No test files found")
            return []
        
        # Results container
        all_results = []
        
        # Create a pool of API servers
        server_ports = []
        try:
            # Start API servers
            for i in range(min(self.max_servers, len(test_files))):
                port = self.base_port + i
                api_process = self.start_api_server(port)
                self.api_processes[port] = api_process
                server_ports.append(port)
            
            # Create work queue
            work_queue = []
            for disorder_name, test_file_path in test_files:
                # Check if we have a config for this disorder
                save_responses = False
                if self.test_configs:
                    for config in self.test_configs:
                        if config.get("name") == disorder_name:
                            save_responses = config.get("save_responses", False)
                            break
                
                work_queue.append((disorder_name, test_file_path, save_responses))
                
            port_index = 0
            
            # Process work queue with round-robin port assignment
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(server_ports)) as executor:
                futures = {}
                
                # Submit initial batch of tests
                while work_queue and len(futures) < len(server_ports):
                    disorder_name, test_file_path, save_responses = work_queue.pop(0)
                    port = server_ports[port_index]
                    port_index = (port_index + 1) % len(server_ports)
                    
                    future = executor.submit(self.run_test, disorder_name, test_file_path, port, save_responses)
                    futures[future] = (disorder_name, port)
                
                # Process remaining tests as others complete
                while futures:
                    completed, _ = concurrent.futures.wait(
                        futures, 
                        return_when=concurrent.futures.FIRST_COMPLETED
                    )
                    
                    for future in completed:
                        disorder_name, port = futures.pop(future)
                        try:
                            result = future.result()
                            all_results.append(result)
                            if self.verbose:
                                print(f"Completed test for {disorder_name}")
                        except Exception as e:
                            print(f"Error in test for {disorder_name}: {e}")
                            all_results.append({
                                "Disorder": disorder_name,
                                "Accuracy": 0,
                                "True_Positive_Rate": 0,
                                "True_Negative_Rate": 0,
                                "False_Positive_Rate": 0,
                                "False_Negative_Rate": 0,
                                "Precision": 0,
                                "F1_Score": 0,
                                "Total_Cases": 0,
                                "Total_Correct": 0,
                                "results_file": "",
                                "error": str(e)
                            })
                        
                        # Submit next test if available
                        if work_queue:
                            next_disorder_name, next_test_file_path, next_save_responses = work_queue.pop(0)
                            next_future = executor.submit(self.run_test, next_disorder_name, next_test_file_path, port, next_save_responses)
                            futures[next_future] = (next_disorder_name, port)
        
        finally:
            # Stop all API servers
            for port in list(self.api_processes.keys()):
                self.stop_api_server(port)
        
        return all_results

    def generate_csv_report(self, results: List[Dict[str, Any]], output_file: str = "disorder_accuracy.csv"):
        """
        Generate a CSV report of test results for all disorders.
        
        Args:
            results: List of result dictionaries for each disorder
            output_file: Path to the output CSV file
        """
        if not results:
            print("No results to generate report from")
            return
        
        # Sort results by disorder name
        results.sort(key=lambda x: x["Disorder"])
        
        # Prepare data for CSV
        csv_data = []
        for result in results:
            disorder_name = result["Disorder"]
            accuracy = result.get("Accuracy", 0)
            
            row = {
                "Disorder": disorder_name,
                "Accuracy": f"{accuracy:.2%}",
                "True_Positive_Rate": f"{result.get('True_Positive_Rate', 0):.2%}",
                "True_Negative_Rate": f"{result.get('True_Negative_Rate', 0):.2%}",
                "False_Positive_Rate": f"{result.get('False_Positive_Rate', 0):.2%}",
                "False_Negative_Rate": f"{result.get('False_Negative_Rate', 0):.2%}",
                "Precision": f"{result.get('Precision', 0):.2%}",
                "F1_Score": f"{result.get('F1_Score', 0):.2%}",
                "Total_Cases": result.get("Total_Cases", 0),
                "Total_Correct": result.get("Total_Correct", 0),
                "Error": result.get("error", "")
            }
            csv_data.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(csv_data)
        
        # Format percentages
        for col in ["Accuracy", "True_Positive_Rate", "True_Negative_Rate", "False_Positive_Rate", "False_Negative_Rate", "Precision", "F1_Score"]:
            df[col] = df[col].apply(lambda x: f"{x:.2%}")
        
        # Write to CSV
        df.to_csv(output_file, index=False)
        print(f"CSV report generated: {output_file}")


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run tests for multiple mental disorder types")
    parser.add_argument("--dir", type=str, default=".",
                        help="Directory containing test JSON files")
    parser.add_argument("--base-port", type=int, default=DEFAULT_BASE_PORT,
                        help=f"Base port number for API servers (default: {DEFAULT_BASE_PORT})")
    parser.add_argument("--max-servers", type=int, default=MAX_SERVERS,
                        help=f"Maximum number of API servers to run in parallel (default: {MAX_SERVERS})")
    parser.add_argument("--results-dir", type=str, default="results",
                        help="Directory to save test results (default: results/)")
    parser.add_argument("--csv", type=str, default="disorder_accuracy.csv",
                        help="Path to output CSV file (default: disorder_accuracy.csv)")
    parser.add_argument("--disorders", type=str, nargs="+",
                        help="Specific disorders to test (default: test all)")
    
    args = parser.parse_args()
    
    # Create and run the test manager
    manager = DisorderTestManager(
        test_files_dir=args.dir,
        base_port=args.base_port,
        max_servers=args.max_servers,
        results_dir=args.results_dir,
        test_subset=args.disorders
    )
    
    # Run the tests
    results = manager.run_all_tests()
    
    # Generate CSV report
    manager.generate_csv_report(results, args.csv) 