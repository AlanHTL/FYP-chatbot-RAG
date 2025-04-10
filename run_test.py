import subprocess
import time
import sys
import os
import signal
import argparse

def start_api_server():
    """Start the API server in a separate process"""
    print("Starting API server...")
    api_process = subprocess.Popen(["python", "api.py"], 
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True)
    
    # Wait for the server to start
    time.sleep(5)
    
    # Check if the server started successfully
    if api_process.poll() is not None:
        print("Error: API server failed to start")
        stdout, stderr = api_process.communicate()
        print(f"Server output: {stdout}")
        print(f"Server error: {stderr}")
        sys.exit(1)
    
    print("API server started successfully")
    return api_process

def run_tests(args_list):
    """Run the tests with the provided arguments"""
    print(f"Running tests with arguments: {args_list}")
    test_cmd = ["python", "chatbot_tester.py"] + args_list
    
    try:
        subprocess.run(test_cmd, check=True)
        print("Tests completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error running tests: {e}")
        return False
    
    return True

def stop_api_server(api_process):
    """Stop the API server"""
    print("Stopping API server...")
    
    # Send SIGTERM signal to terminate the process
    if os.name == 'nt':  # Windows
        api_process.terminate()
    else:  # Unix/Linux
        os.kill(api_process.pid, signal.SIGTERM)
    
    # Wait for the process to terminate
    try:
        api_process.wait(timeout=10)
        print("API server stopped successfully")
    except subprocess.TimeoutExpired:
        print("API server did not stop gracefully, forcing termination...")
        api_process.kill()
        api_process.wait()

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Run chatbot tests with API server")
    parser.add_argument("--file", type=str, default="major_neurocognitive_disorder_test.json",
                        help="Path to the test case JSON file")
    parser.add_argument("--cases", type=int, nargs="+", 
                        help="Specific case IDs to test (e.g. --cases 1 2 15)")
    parser.add_argument("--save", type=str, default="test_results.json",
                        help="Save results to the specified JSON file")
    parser.add_argument("--parallel", type=int, default=3,
                        help="Number of parallel tests to run (default: 3)")
    
    args = parser.parse_args()
    
    # Prepare arguments for the test script
    test_args = []
    if args.file:
        test_args.extend(["--file", args.file])
    if args.cases:
        test_args.append("--cases")
        test_args.extend([str(case) for case in args.cases])
    if args.save:
        test_args.extend(["--save", args.save])
    if args.parallel:
        test_args.extend(["--parallel", str(args.parallel)])
    
    # Start API server
    api_process = start_api_server()
    
    try:
        # Run tests
        success = run_tests(test_args)
        
        # Print summary
        if success:
            print("\nTest run completed successfully")
            print(f"Results saved to: {args.save}")
        else:
            print("\nTest run completed with errors")
    finally:
        # Stop API server
        stop_api_server(api_process) 