# Fixing Test Result Bias Issue

This guide explains how to fix the issue where test results were being influenced by filenames rather than actual chatbot responses.

## The Problem

The current testing system has a flaw:
- Test results are matching filenames rather than actual chatbot responses
- For example, tests in `panic_disorder_test.json` are being matched against the string "panic disorder"
- This creates biased results that don't accurately reflect the chatbot's performance

## Solution

We've created three scripts to resolve this issue:

1. `update_test_files.py` - Adds explicit disorder names to test cases
2. `update_check_diagnosis.py` - Improves the diagnosis checking logic
3. `disable_filename_extraction.py` - Completely disables filename-based matching

## Step-by-Step Fix

### 1. Update test files with explicit disorder names

Run:
```bash
python update_test_files.py
```

This will:
- Find all test files in your project
- Add an explicit `disorder_name` field to each test case
- Back up the original files before modifying them
- Show statistics about the number of cases updated

### 2. Update the diagnosis checking logic

Run:
```bash
python update_check_diagnosis.py
```

This will:
- Update the `_check_diagnosis` method in `chatbot_tester.py`
- Add better logic for checking against explicit disorder names
- Fix issues with result parsing
- Back up the original file before modifying it

### 3. Disable filename extraction (recommended)

Run:
```bash
python disable_filename_extraction.py
```

This will:
- Completely disable the filename-based diagnosis matching
- Ensure tests only pass if they match against explicit disorder names
- Add warnings for test cases missing disorder names

## Verifying the Fix

After applying these fixes, run a test to verify the changes:

```bash
python test_specific_disorders.py "panic disorder"
```

Check the results to ensure:
- Tests are matching against actual chatbot responses
- Normal cases are correctly identified
- Disorder cases are correctly identified based on matching the disorder name in the response

## Understanding Test Case Structure

After the update, your test cases should look like:

```json
{
  "id": "case_001",
  "conversation": [...],
  "expected_diagnosis": {
    "has_disorder": true,
    "disorder_name": "panic disorder"  // Explicitly specified
  }
}
```

## Recommended Workflow

1. First, update your test files to add explicit disorder names
2. Then, update the diagnosis checking logic
3. Finally, disable filename extraction completely
4. Re-run your tests to get accurate results 