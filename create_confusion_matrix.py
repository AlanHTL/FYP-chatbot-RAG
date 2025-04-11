import pandas as pd
import numpy as np

# Read the CSV file
df = pd.read_csv('results/test_results_20250411_033126/all_results.csv')

# Create a pivot table to get the confusion matrix
confusion_matrix = pd.crosstab(df['actual_diagnosis'], df['expected_diagnosis'])

# Save to a new CSV file
confusion_matrix.to_csv('results/test_results_20250411_033126/confusion_matrix.csv') 