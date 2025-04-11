import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Read the corrected CSV file
data = pd.read_csv('corrected_results.csv')

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
plt.title('Diagnosis Accuracy by Disorder (Corrected)', fontsize=18, fontweight='bold')
plt.xlabel('Accuracy (%)', fontsize=14)
plt.xlim(0, 105)  # Give room for the labels
plt.legend(loc='lower right')
plt.tight_layout()

# Save the visualization
plt.savefig('corrected_disorder_accuracy.png', dpi=300)
print('Corrected accuracy visualization saved as corrected_disorder_accuracy.png')

# Print detailed accuracy by disorder
print("\nAccuracy by Disorder (after correction):")
print(disorder_accuracy) 