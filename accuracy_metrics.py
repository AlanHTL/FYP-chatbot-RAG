import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report

# Read the CSV file
data = pd.read_csv('results/test_results_20250411_143751/all_results.csv')

# Calculate overall accuracy
overall_accuracy = data['correct'].mean() * 100

# Calculate accuracy per disorder
disorder_accuracy = data.groupby('Disorder')['correct'].mean() * 100
disorder_accuracy = disorder_accuracy.sort_values(ascending=False)

# Create figure with subplots
fig = plt.figure(figsize=(18, 12))
fig.suptitle('Diagnosis Accuracy Metrics', fontsize=20, fontweight='bold', y=0.98)

# Plot 1: Overall Accuracy
ax1 = plt.subplot2grid((2, 2), (0, 0))
ax1.bar(['Overall Accuracy'], [overall_accuracy], color='royalblue')
ax1.set_ylim(0, 100)
ax1.set_ylabel('Accuracy (%)', fontsize=12)
ax1.set_title('Overall Accuracy', fontsize=16)
ax1.text(0, overall_accuracy + 1, f'{overall_accuracy:.1f}%', ha='center', fontweight='bold')
ax1.grid(axis='y', linestyle='--', alpha=0.7)

# Plot 2: Accuracy by Disorder
ax2 = plt.subplot2grid((2, 2), (0, 1), rowspan=2)
colors = plt.cm.viridis(np.linspace(0, 0.9, len(disorder_accuracy)))
bars = ax2.barh(disorder_accuracy.index, disorder_accuracy.values, color=colors)
ax2.set_xlabel('Accuracy (%)', fontsize=12)
ax2.set_title('Accuracy by Disorder', fontsize=16)
ax2.set_xlim(0, 100)
ax2.grid(axis='x', linestyle='--', alpha=0.7)
for i, (idx, val) in enumerate(disorder_accuracy.items()):
    ax2.text(val + 1, i, f'{val:.1f}%', va='center')

# Plot 3: Count of Correct vs Incorrect by Disorder
ax3 = plt.subplot2grid((2, 2), (1, 0))
disorder_counts = data.groupby(['Disorder', 'correct']).size().unstack(fill_value=0)
if False not in disorder_counts.columns:
    disorder_counts[False] = 0
if True not in disorder_counts.columns:
    disorder_counts[True] = 0
disorder_counts = disorder_counts.sort_values(True, ascending=False)
disorder_counts.plot(kind='bar', stacked=True, ax=ax3, color=['#ff9999', '#66b3ff'])
ax3.set_title('Correct vs Incorrect Diagnoses by Disorder', fontsize=16)
ax3.set_xlabel('Disorder', fontsize=12)
ax3.set_ylabel('Count', fontsize=12)
ax3.legend(['Incorrect', 'Correct'])
plt.xticks(rotation=90)

plt.tight_layout()
plt.subplots_adjust(top=0.9, hspace=0.3, wspace=0.3)
plt.savefig('accuracy_metrics.png', dpi=300)
print('Accuracy metrics visualization saved as accuracy_metrics.png')

# Generate detailed classification metrics
print('\nOverall Accuracy: {:.2f}%'.format(overall_accuracy))
print('\nAccuracy by Disorder:')
print(disorder_accuracy)

# Create confusion matrix for each disorder
print("\nGenerating confusion matrices and classification reports for each disorder...")
for disorder in data['Disorder'].unique():
    print(f"\n--- {disorder} ---")
    disorder_data = data[data['Disorder'] == disorder]
    
    # Get all unique diagnoses for this disorder
    all_diagnoses = set(disorder_data['expected_diagnosis'].tolist() + disorder_data['actual_diagnosis'].tolist())
    
    # Print counts for expected vs actual
    print("Expected diagnosis count:", disorder_data['expected_diagnosis'].value_counts())
    print("Actual diagnosis count:", disorder_data['actual_diagnosis'].value_counts())
    
    # Print accuracy
    accuracy = disorder_data['correct'].mean() * 100
    print(f"Accuracy: {accuracy:.2f}%")
    
    # Create a cross-tabulation (simple confusion matrix)
    print("\nCross-tabulation (expected vs actual):")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    confusion = pd.crosstab(disorder_data['expected_diagnosis'], 
                            disorder_data['actual_diagnosis'], 
                            rownames=['Expected'], 
                            colnames=['Actual'])
    print(confusion) 