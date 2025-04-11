import pandas as pd

# Read the CSV file
data = pd.read_csv('results/test_results_20250411_143751/all_results.csv')

# Create a copy of the data
corrected_data = data.copy()

# Find ADHD cases where expected and actual diagnoses match but marked as incorrect
adhd_cases = corrected_data[
    (corrected_data['Disorder'] == 'adhd') & 
    (corrected_data['expected_diagnosis'].str.lower() == corrected_data['actual_diagnosis'].str.lower()) &
    (corrected_data['correct'] == False)
]

# Fix the 'correct' column for these cases
for idx in adhd_cases.index:
    corrected_data.at[idx, 'correct'] = True

# Save the corrected data
corrected_data.to_csv('corrected_results.csv', index=False)

# Print summary of changes
print(f"Fixed {len(adhd_cases)} ADHD cases:")
for idx, row in adhd_cases.iterrows():
    print(f"Case ID: {row['case_id']}, Patient: {row['patient_name']}")
    print(f"  Expected: {row['expected_diagnosis']}")
    print(f"  Actual: {row['actual_diagnosis']}")
    print(f"  Changed from incorrect to correct")
    print()

print(f"\nCorrected data saved to 'corrected_results.csv'") 