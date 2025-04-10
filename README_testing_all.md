# Mental Disorder Screening Chatbot - Comprehensive Testing Framework

This framework provides tools to test the mental health screening chatbot across multiple disorders, collect results, and generate visual reports.

## Files Overview

- `run_all_tests.py`: Tests all disorders listed in the JSON file
- `test_specific_disorders.py`: Tests a specific subset of disorders
- `update_check_diagnosis.py`: Updates the diagnosis checker to work with all disorder types
- `multi_disorder_tester.py`: Core testing framework that runs multiple API servers in parallel
- `visualize_results.py`: Generates visualizations from test results
- `disorder_test_files.json`: Contains the list of disorder test files

## Setup

Before running any tests, you need to update the diagnosis checker to properly handle all disorder types:

```bash
python update_check_diagnosis.py
```

This will modify the `chatbot_tester.py` file to extract disorder names from test filenames and perform proper diagnosis matching.

## Testing All Disorders

To run tests for all disorders listed in `disorder_test_files.json`:

```bash
python run_all_tests.py
```

Options:
- `--max-servers`: Number of API servers to run in parallel (default: 3)
- `--results-dir`: Base directory for results (default: results_TIMESTAMP)
- `--disorder-list`: JSON file containing list of test files (default: disorder_test_files.json)
- `--base-port`: Starting port for API servers (default: 8081)
- `--specific-disorders`: List of specific disorders to test
- `--skip-visualization`: Skip generating visualizations

## Testing Specific Disorders

For quicker testing of specific disorders:

```bash
python test_specific_disorders.py "major depressive" "generalized anxiety"
```

Options:
- `--servers`: Number of API servers to use (default: 1)
- `--port`: Base port for API servers (default: 8081)
- `--visualize`: Generate visualizations after testing

## Test Results

Each test run generates:

1. A CSV file with accuracy metrics for each disorder
2. Individual JSON result files in the results directory
3. Visualization charts (if not skipped)

## Visualizations

The framework generates the following visualizations:

- Bar chart comparing overall accuracy across disorders
- Grouped bar chart comparing all metrics (accuracy, TPR, TNR)
- Heatmap of performance metrics
- Radar charts for each disorder
- Summary statistics with averages

To generate visualizations from existing results:

```bash
python visualize_results.py --csv path/to/disorder_accuracy.csv --output charts_dir
```

## Example Workflow

1. Update the diagnosis checker:
   ```bash
   python update_check_diagnosis.py
   ```

2. Test a couple of disorders to verify setup:
   ```bash
   python test_specific_disorders.py "major depressive" --visualize
   ```

3. Run full test suite overnight:
   ```bash
   python run_all_tests.py --max-servers 5
   ```

4. Review the results in the generated CSV file and visualizations

## Performance Considerations

- Each API server uses significant resources
- Recommended max-servers setting depends on system capabilities:
  - 4GB RAM: 1-2 servers
  - 8GB RAM: 2-3 servers
  - 16GB+ RAM: 3-5 servers

## Troubleshooting

- If an API server fails to start, check if the port is already in use
- If tests fail with timeouts, reduce the number of parallel servers
- If the diagnosis accuracy seems low, verify the disorder name extraction in `update_check_diagnosis.py` 