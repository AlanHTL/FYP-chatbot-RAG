import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.gridspec import GridSpec

# Set the style
plt.style.use('seaborn')
sns.set_palette("husl")

# Read the corrected CSV file
data = pd.read_csv('corrected_results.csv')

# Calculate metrics
overall_accuracy = data['correct'].mean() * 100
disorder_accuracy = data.groupby('Disorder')['correct'].mean() * 100
disorder_accuracy = disorder_accuracy.sort_values(ascending=False)
total_correct = data['correct'].sum()
total_incorrect = len(data) - total_correct

# Create a figure with multiple subplots
fig = plt.figure(figsize=(20, 15))
gs = GridSpec(2, 2, figure=fig)

# 1. Overall Accuracy and Distribution
ax1 = fig.add_subplot(gs[0, 0])
accuracy_data = pd.DataFrame({
    'Category': ['Correct', 'Incorrect'],
    'Count': [total_correct, total_incorrect]
})
colors = ['#4CAF50', '#F44336']
ax1.pie(accuracy_data['Count'], labels=accuracy_data['Category'], 
        autopct='%1.1f%%', colors=colors, startangle=90)
ax1.set_title('Overall Diagnosis Distribution', fontsize=16, pad=20)
ax1.text(0, -1.2, f'Overall Accuracy: {overall_accuracy:.1f}%', 
         ha='center', fontsize=14, fontweight='bold')

# 2. Accuracy by Disorder (Horizontal Bar Chart)
ax2 = fig.add_subplot(gs[0, 1])
colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(disorder_accuracy)))
bars = ax2.barh(disorder_accuracy.index, disorder_accuracy.values, color=colors)
ax2.set_title('Accuracy by Disorder', fontsize=16, pad=20)
ax2.set_xlabel('Accuracy (%)', fontsize=14)
ax2.set_xlim(0, 105)
ax2.axvline(x=overall_accuracy, color='blue', linestyle='--', 
            label=f'Overall Average: {overall_accuracy:.1f}%')
for i, v in enumerate(disorder_accuracy):
    ax2.text(v + 1, i, f"{v:.1f}%", va='center', fontweight='bold')
ax2.legend(loc='lower right')

# 3. Correct vs Incorrect by Disorder (Stacked Bar Chart)
ax3 = fig.add_subplot(gs[1, 0])
disorder_counts = data.groupby(['Disorder', 'correct']).size().unstack(fill_value=0)
disorder_counts = disorder_counts.sort_values(True, ascending=False)
disorder_counts.plot(kind='bar', stacked=True, ax=ax3, 
                    color=['#F44336', '#4CAF50'])
ax3.set_title('Correct vs Incorrect Diagnoses by Disorder', fontsize=16, pad=20)
ax3.set_xlabel('Disorder', fontsize=14)
ax3.set_ylabel('Count', fontsize=14)
ax3.legend(['Incorrect', 'Correct'])
plt.xticks(rotation=45, ha='right')

# 4. Confidence Distribution
ax4 = fig.add_subplot(gs[1, 1])
sns.histplot(data=data, x='confidence', hue='correct', 
             bins=10, kde=True, ax=ax4)
ax4.set_title('Confidence Distribution by Correctness', fontsize=16, pad=20)
ax4.set_xlabel('Confidence Score', fontsize=14)
ax4.set_ylabel('Count', fontsize=14)
ax4.legend(['Incorrect', 'Correct'])

# Adjust layout and save
plt.tight_layout()
plt.subplots_adjust(top=0.9, hspace=0.3, wspace=0.3)
plt.savefig('comprehensive_analysis.png', dpi=300, bbox_inches='tight')
print('Comprehensive analysis visualization saved as comprehensive_analysis.png')

# Create a separate confusion matrix visualization
plt.figure(figsize=(15, 12))
confusion = pd.crosstab(data['expected_diagnosis'], data['actual_diagnosis'])
sns.heatmap(confusion, annot=True, fmt='g', cmap='Blues', 
            linewidths=0.5, square=True)
plt.title('Confusion Matrix: Expected vs Actual Diagnoses', fontsize=16, pad=20)
plt.xlabel('Actual Diagnosis', fontsize=14)
plt.ylabel('Expected Diagnosis', fontsize=14)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig('confusion_matrix.png', dpi=300, bbox_inches='tight')
print('Confusion matrix saved as confusion_matrix.png')

# Print summary statistics
print("\nSummary Statistics:")
print(f"Overall Accuracy: {overall_accuracy:.2f}%")
print(f"Total Cases: {len(data)}")
print(f"Correct Diagnoses: {total_correct}")
print(f"Incorrect Diagnoses: {total_incorrect}")
print("\nAccuracy by Disorder:")
print(disorder_accuracy) 