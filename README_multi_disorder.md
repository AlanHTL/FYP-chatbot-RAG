# Mental Disorder Screening Chatbot - Multi-Disorder Testing Framework

This testing framework evaluates the accuracy of the mental disorder screening chatbot across multiple disorder types, running tests in parallel for improved efficiency.

## Features

- Tests all disorder types from JSON test files
- Runs multiple API server instances in parallel
- Distributes test workload across servers
- Generates consolidated CSV report of accuracy metrics
- Allows testing specific disorders or all available ones
- Stores detailed results for each disorder

## Prerequisites

- Python 3.6+
- All required packages installed (`pandas`, `requests`, etc.)
- The chatbot API server (`api.py`)
- Individual test files for each disorder type (named `[disorder_name]_test.json`)

## Usage

### Basic Usage

To test all disorder types with default settings:

```bash
python multi_disorder_tester.py
```

This will:
1. Find all `*_test.json` files in the current directory
2. Start up to 5 API servers on different ports
3. Run tests for each disorder in parallel
4. Generate a CSV report of the results

### Advanced Options

```bash
python multi_disorder_tester.py \
  --dir /path/to/test/files \
  --base-port 8090 \
  --max-servers 3 \
  --results-dir my_results \
  --csv disorder_metrics.csv \
  --disorders major_depressive_disorder generalized_anxiety_disorder
```

### Command Line Arguments

- `--dir`: Directory containing test JSON files (default: current directory)
- `--base-port`: Starting port number for API servers (default: 8081)
- `--max-servers`: Maximum number of API servers to run in parallel (default: 5)
- `--results-dir`: Directory to save test results (default: results/)
- `--csv`: Path to output CSV file (default: disorder_accuracy.csv)
- `--disorders`: Specific disorders to test (by default, tests all)

## Output

### CSV Report

The CSV report includes the following columns:
- **Disorder**: Name of the disorder
- **Overall Accuracy**: Percentage of correctly diagnosed cases
- **True Positive Rate**: Percentage of disorder cases correctly identified
- **True Negative Rate**: Percentage of normal cases correctly identified as normal
- **Error**: Any error encountered during testing

### Individual Results

Individual test results are saved as JSON files in the results directory.

## How It Works

1. **Discovery**: The framework finds all test files in the specified directory
2. **Server Pool**: Multiple API servers are started on different ports
3. **Testing**: Tests are distributed across servers for parallel execution
4. **Monitoring**: As tests complete, new ones are assigned to the available servers
5. **Reporting**: Results are collected and formatted into a CSV report

## Testing Flow

```
┌────────────────┐      ┌────────────────┐      ┌────────────────┐
│ API Server 1   │      │ API Server 2   │      │ API Server 3   │
│ (Port 8081)    │      │ (Port 8082)    │      │ (Port 8083)    │
└───────┬────────┘      └───────┬────────┘      └───────┬────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌────────────────┐      ┌────────────────┐      ┌────────────────┐
│ Test Worker 1  │      │ Test Worker 2  │      │ Test Worker 3  │
│ (Disorder A)   │      │ (Disorder B)   │      │ (Disorder C)   │
└───────┬────────┘      └───────┬────────┘      └───────┬────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌────────────────┐      ┌────────────────┐      ┌────────────────┐
│ Results A      │      │ Results B      │      │ Results C      │
└───────┬────────┘      └───────┬────────┘      └───────┬────────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                               ▼
                     ┌────────────────────┐
                     │ Consolidated CSV   │
                     └────────────────────┘
```

## Adding New Disorder Tests

To test a new disorder type:

1. Create a test JSON file named `[disorder_name]_test.json` with the appropriate test cases
2. Put the file in the test directory
3. Run the multi-disorder tester

The framework will automatically detect and test the new disorder. 