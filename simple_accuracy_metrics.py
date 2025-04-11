import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Read the CSV file
data = pd.read_csv('results/test_results_20250411_143751/all_results.csv')

# Calculate overall accuracy
overall_accuracy = data['correct'].mean() * 100
print(f"Overall Accuracy: {overall_accuracy:.2f}%")

# Calculate accuracy per disorder
disorder_accuracy = data.groupby('Disorder')['correct'].mean() * 100
disorder_accuracy = disorder_accuracy.sort_values(ascending=False)

# Calculate total correct/incorrect counts
total_correct = data['correct'].sum()
total_incorrect = len(data) - total_correct
print(f"Total Correct: {total_correct}, Total Incorrect: {total_incorrect}")

# Create a cleaner horizontal bar chart for accuracies
plt.figure(figsize=(12, 10))
sns.set_style('whitegrid')
colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(disorder_accuracy)))

# Plot horizontal bars
ax = sns.barplot(x=disorder_accuracy.values, y=disorder_accuracy.index, palette=colors, orient='h')

# Add percentage labels
for i, v in enumerate(disorder_accuracy):
    ax.text(v + 1, i, f"{v:.1f}%", va='center', fontweight='bold')

# Add a vertical line for the overall average
plt.axvline(x=overall_accuracy, color='blue', linestyle='--', label=f'Overall Average: {overall_accuracy:.1f}%')

# Formatting
plt.title('Diagnosis Accuracy by Disorder', fontsize=18, fontweight='bold')
plt.xlabel('Accuracy (%)', fontsize=14)
plt.xlim(0, 105)  # Give room for the labels
plt.legend(loc='lower right')
plt.tight_layout()

# Save the visualization
plt.savefig('disorder_accuracy.png', dpi=300)
print('Simple accuracy visualization saved as disorder_accuracy.png')

# Get more detailed information about disorders with lowest accuracy
print("\nDetailed analysis of disorders with low accuracy:")
for disorder in disorder_accuracy.index[-5:]:  # Get the 5 lowest accuracy disorders
    print(f"\n--- {disorder} ---")
    disorder_data = data[data['Disorder'] == disorder]
    
    # Count the number of cases where expected and actual diagnoses match
    matching = (disorder_data['expected_diagnosis'] == disorder_data['actual_diagnosis']).sum()
    total = len(disorder_data)
    print(f"Matches: {matching}/{total} ({matching/total*100:.1f}%)")
    
    # Most common actual diagnoses for this expected disorder
    print("\nActual diagnoses when expected was", disorder_data['expected_diagnosis'].iloc[0])
    print(disorder_data['actual_diagnosis'].value_counts()) 