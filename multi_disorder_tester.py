import os
import json
import time
import subprocess
import concurrent.futures
import pandas as pd
from typing import List, Dict, Any
import socket
import signal
from dotenv import load_dotenv
load_dotenv()
class DisorderTestManager:
    """Manager for testing multiple disorder types in parallel."""

    def __init__(self, 
                 test_configs: List[Dict[str, Any]],
                 num_servers: int = int(os.getenv("Number_of_Servers", 3)),
                 base_port: int = 8081,
                 results_dir: str = "results",
                 verbose: bool = False):
        """
        Initialize the test manager.
        
        Args:
            test_configs: List of test configurations for each disorder
            num_servers: Number of API servers to run in parallel
            base_port: Starting port number for API servers
            results_dir: Directory to save test results
            verbose: Whether to print detailed progress information
        """
        self.test_configs = test_configs
        self.num_servers = num_servers
        self.base_port = base_port
        self.results_dir = results_dir
        self.verbose = verbose
        self.api_processes = {}  # Maps port to subprocess
        
        # Ensure results directory exists
        os.makedirs(results_dir, exist_ok=True)
        
        if self.verbose:
            print(f"DisorderTestManager initialized with {len(test_configs)} test configurations")
            print(f"Using {num_servers} parallel servers starting from port {base_port}")

    def is_port_available(self, port: int) -> bool:
        """Check if a port is available for use."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0

    def start_api_server(self, port: int) -> subprocess.Popen:
        """Start an API server on the specified port."""
        if not self.is_port_available(port):
            raise ValueError(f"Port {port} is already in use")
        
        # Set environment variables for the API server
        env = os.environ.copy()
        env["API_PORT"] = str(port)
        
        if self.verbose:
            print(f"Starting API server on port {port}...")
        
        # Start the server process
        api_process = subprocess.Popen(
            ["python", "api.py"],
            env=env,
            stdout=subprocess.PIPE if not self.verbose else None,
            stderr=subprocess.PIPE if not self.verbose else None
        )
        
        # Wait for server to start
        time.sleep(5)
        
        # Check if server started successfully
        if api_process.poll() is not None:
            raise RuntimeError(f"Failed to start API server on port {port}")
        
        if self.verbose:
            print(f"API server started on port {port}")
        
        return api_process

    def stop_api_server(self, port: int):
        """Stop the API server on the specified port."""
        if port not in self.api_processes:
            return
        
        process = self.api_processes[port]
        if self.verbose:
            print(f"Stopping API server on port {port}...")
        
        try:
            if os.name == 'nt':  # Windows
                process.terminate()
            else:  # Unix
                os.kill(process.pid, signal.SIGTERM)
            
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        
        del self.api_processes[port]

    def run_test_case(self, config: Dict[str, Any], port: int) -> Dict[str, Any]:
        """Run tests for a specific disorder using the specified port."""
        disorder_name = config["name"]
        test_file = config["test_file"]
        save_responses = config.get("save_responses", False)
        
        if self.verbose:
            print(f"Testing {disorder_name} using port {port}...")
        
        # Create result filename
        result_file = os.path.join(self.results_dir, f"{disorder_name}_results.json")
        csv_file = os.path.join(self.results_dir, "all_results.csv")
        
        # Set up command
        cmd = [
            "python", "chatbot_tester.py",
            "--file", test_file,
            "--save", result_file
        ]
        
        if save_responses:
            cmd.append("--save-responses")
        
        # Set API URL environment variable
        env = os.environ.copy()
        env["CHATBOT_API_URL"] = f"http://127.0.0.1:{port}/chat"
        
        try:
            # Run the test
            process = subprocess.run(
                cmd,
                env=env,
                check=True,
                capture_output=True,
                text=True
            )
            
            if self.verbose:
                print(f"Test completed for {disorder_name}")
                print(process.stdout)
            
            # Load and return results
            if os.path.exists(result_file):
                with open(result_file, 'r') as f:
                    results = json.load(f)
                
                # Add disorder name to each result
                for result in results.get("results", []):
                    result["Disorder"] = disorder_name
                
                # Update CSV file with new results
                try:
                    if os.path.exists(csv_file):
                        # Read existing CSV
                        df_existing = pd.read_csv(csv_file)
                        # Convert new results to DataFrame
                        df_new = pd.DataFrame(results.get("results", []))
                        # Combine and remove duplicates
                        df_combined = pd.concat([df_existing, df_new]).drop_duplicates(subset=['case_id', 'Disorder'], keep='last')
                        # Save back to CSV
                        df_combined.to_csv(csv_file, index=False)
                    else:
                        # Create new CSV if it doesn't exist
                        pd.DataFrame(results.get("results", [])).to_csv(csv_file, index=False)
                except Exception as e:
                    print(f"Error updating CSV file: {e}")
                
                return results
            else:
                print(f"Warning: No results file found for {disorder_name}")
                return {"results": []}
                
        except subprocess.CalledProcessError as e:
            print(f"Error testing {disorder_name}: {e}")
            print(f"Output: {e.output}")
            print(f"Error: {e.stderr}")
            return {"results": []}
        except Exception as e:
            print(f"Unexpected error testing {disorder_name}: {e}")
            return {"results": []}

    def run_all_tests(self) -> List[Dict[str, Any]]:
        """Run all tests using multiple servers in parallel."""
        all_results = []
        
        # Initialize CSV file if it doesn't exist
        csv_file = os.path.join(self.results_dir, "all_results.csv")
        if not os.path.exists(csv_file):
            pd.DataFrame(columns=['case_id', 'Disorder', 'expected_diagnosis', 'actual_diagnosis', 'correct', 'confidence']).to_csv(csv_file, index=False)
        
        try:
            # Start API servers
            for i in range(self.num_servers):
                port = self.base_port + i
                self.api_processes[port] = self.start_api_server(port)
            
            # Create a pool of worker threads
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_servers) as executor:
                # Distribute test cases across servers
                futures = []
                for i, config in enumerate(self.test_configs):
                    port = self.base_port + (i % self.num_servers)
                    futures.append(executor.submit(self.run_test_case, config, port))
                
                # Collect results as they complete
                for future in concurrent.futures.as_completed(futures):
                    try:
                        result = future.result()
                        if result and "results" in result:
                            all_results.extend(result["results"])
                    except Exception as e:
                        print(f"Error collecting test results: {e}")
        
        finally:
            # Stop all API servers
            for port in list(self.api_processes.keys()):
                self.stop_api_server(port)
        
        return all_results 