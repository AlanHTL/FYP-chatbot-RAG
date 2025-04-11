import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Read the CSV file
data = pd.read_csv('results/test_results_20250411_143751/all_results.csv')

# Create a confusion matrix
confusion = pd.crosstab(
    data['expected_diagnosis'], 
    data['actual_diagnosis'],
    rownames=['Expected'], 
    colnames=['Actual']
)

# Fill NaN values with 0
confusion = confusion.fillna(0)

# Convert to percentages across rows (what percentage of each expected diagnosis was classified as what)
confusion_pct = confusion.div(confusion.sum(axis=1), axis=0) * 100

# Create a figure with two subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 14))

# Plot 1: Absolute counts confusion matrix
sns.heatmap(confusion, annot=True, fmt='g', cmap='Blues', ax=ax1, linewidths=0.5)
ax1.set_title('Confusion Matrix: Expected vs Actual Diagnoses (Counts)', fontsize=16)
ax1.set_ylabel('Expected Diagnosis', fontsize=12)
ax1.set_xlabel('Actual Diagnosis', fontsize=12)

# Rotate the labels and set font size
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha='right', fontsize=10)
ax1.set_yticklabels(ax1.get_yticklabels(), rotation=0, fontsize=10)

# Plot 2: Percentage confusion matrix
sns.heatmap(confusion_pct, annot=True, fmt='.1f', cmap='RdYlGn', ax=ax2, linewidths=0.5)
ax2.set_title('Confusion Matrix: Expected vs Actual Diagnoses (Row %)', fontsize=16)
ax2.set_ylabel('Expected Diagnosis', fontsize=12)
ax2.set_xlabel('Actual Diagnosis', fontsize=12)

# Rotate the labels and set font size
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha='right', fontsize=10)
ax2.set_yticklabels(ax2.get_yticklabels(), rotation=0, fontsize=10)

plt.tight_layout()
plt.savefig('confusion_matrix.png', dpi=300)
print('Confusion matrix visualizations saved as confusion_matrix.png')

# Calculate and print some overall metrics
print("\nOverall accuracy metrics:")
print(f"Total number of cases: {len(data)}")
print(f"Total correct diagnoses: {data['correct'].sum()}")
print(f"Total incorrect diagnoses: {len(data) - data['correct'].sum()}")
print(f"Overall accuracy rate: {data['correct'].mean() * 100:.2f}%")

# Print highest and lowest accuracy disorders
disorder_accuracy = data.groupby('Disorder')['correct'].mean() * 100
print("\nTop 5 highest accuracy disorders:")
print(disorder_accuracy.sort_values(ascending=False).head(5))
print("\nBottom 5 lowest accuracy disorders:")
print(disorder_accuracy.sort_values(ascending=True).head(5)) 