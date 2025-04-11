import pandas as pd

# Read the CSV file
data = pd.read_csv('results/test_results_20250411_143751/all_results.csv')

# Create a calculated 'should_be_correct' column based on exact match
data['should_be_correct'] = data['expected_diagnosis'].str.lower() == data['actual_diagnosis'].str.lower()

# Find discrepancies between 'correct' column and actual comparison
discrepancies = data[data['correct'] != data['should_be_correct']]

print(f"Total records: {len(data)}")
print(f"Records with discrepancies: {len(discrepancies)}")

if len(discrepancies) > 0:
    print("\nDiscrepancies found:")
    print("=====================")
    for idx, row in discrepancies.iterrows():
        print(f"Row {idx+1} (case_id: {row['case_id']}, patient: {row['patient_name']})")
        print(f"  Expected diagnosis: {row['expected_diagnosis']}")
        print(f"  Actual diagnosis: {row['actual_diagnosis']}")
        print(f"  Marked as correct: {row['correct']}")
        print(f"  Should be marked as: {row['should_be_correct']}")
        print()
        
    # Count discrepancies by disorder
    print("\nDiscrepancies by disorder:")
    print(discrepancies['Disorder'].value_counts())
    
    # Save discrepancies to a CSV for further analysis
    discrepancies.to_csv('discrepancies.csv', index=False)
    print("\nDiscrepancies saved to 'discrepancies.csv'")
else:
    print("No discrepancies found. All 'correct' values match the comparison of expected vs actual diagnoses.") 