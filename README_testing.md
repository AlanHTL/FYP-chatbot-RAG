# Mental Disorder Screening Chatbot Testing Framework

This framework tests the accuracy of the mental disorder screening chatbot using simulated patients powered by GPT-3.5 Turbo.

## Features

- Tests chatbot accuracy against predefined test cases
- Uses GPT-3.5 Turbo to simulate natural patient responses
- Supports parallel testing for faster evaluation
- Calculates accuracy metrics (overall accuracy, true positive rate, true negative rate)
- Provides detailed test results for each case

## How It Works

1. The framework loads test cases from a JSON file
2. For each test case, GPT-3.5 Turbo simulates a patient with the specified characteristics
3. The simulated patient interacts with the screening chatbot API
4. The framework extracts and evaluates the chatbot's diagnosis
5. Results are compiled and accuracy metrics are calculated

## Usage

1. Make sure the screening chatbot API is running (using the `run_scripts.py` script)
2. Run the testing script:

```bash
python chatbot_tester.py
```

By default, the script will test all cases in the `major_neurocognitive_disorder_test.json` file.

## Test Case Structure

Test cases are stored in JSON files with the following structure:

```json
{
  "test_cases": [
    {
      "case_id": 1,
      "patient_profile": {
        "name": "Patient Name",
        "age": 72,
        "gender": "Gender",
        "occupation": "Occupation"
      },
      "symptoms_and_experiences": {
        "main_complaints": ["Symptom 1", "Symptom 2"],
        "duration": "Duration",
        "severity": "Severity",
        "impact_on_life": "Impact",
        "specific_examples": ["Example 1", "Example 2"]
      },
      "emotional_state": {
        "current_mood": "Mood",
        "thoughts": ["Thought 1", "Thought 2"],
        "feelings": ["Feeling 1", "Feeling 2"]
      },
      "behavioral_patterns": {
        "daily_activities": ["Activity 1", "Activity 2"],
        "changes_in_routine": ["Change 1", "Change 2"],
        "coping_mechanisms": ["Mechanism 1", "Mechanism 2"]
      },
      "expected_diagnosis": {
        "has_disorder": true,
        "confidence_level": "high",
        "matching_criteria": ["Criterion 1", "Criterion 2"]
      }
    }
  ]
}
```

## Creating Test Cases for Other Disorders

To test other disorders:

1. Create a JSON file with test cases for that disorder
2. Follow the same structure as the example test cases
3. Update the file path in `chatbot_tester.py`

## Interpreting Results

The testing framework calculates:

- **Overall Accuracy**: Percentage of correctly diagnosed cases
- **True Positive Rate**: Percentage of disorder cases correctly identified
- **True Negative Rate**: Percentage of normal cases correctly identified as normal

A test case is considered correctly diagnosed if:
- For disorder cases: The chatbot identifies the correct disorder
- For normal cases: The chatbot returns "Normal" in the result 