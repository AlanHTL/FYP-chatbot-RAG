import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# Read the corrected CSV file
data = pd.read_csv('corrected_results.csv')

# Convert diagnoses to lowercase for consistent comparison
data['expected_diagnosis_lower'] = data['expected_diagnosis'].str.lower()
data['actual_diagnosis_lower'] = data['actual_diagnosis'].str.lower()

# Get classification report
report = classification_report(
    data['expected_diagnosis_lower'],
    data['actual_diagnosis_lower'],
    output_dict=True,
    zero_division=0
)

# Convert the report to a DataFrame
metrics_df = pd.DataFrame(report).transpose()
metrics_df = metrics_df.round(4)

# Remove the 'support' column from display but keep it for later
support = metrics_df['support']
metrics_df = metrics_df.drop('support', axis=1)

# Print the results
print("\nClassification Metrics (Case-Insensitive):")
print("=====================================")
print("\nOverall Metrics:")
print(f"Accuracy: {metrics_df.loc['accuracy', 'precision']:.4f}")
print(f"Macro Avg Precision: {metrics_df.loc['macro avg', 'precision']:.4f}")
print(f"Macro Avg Recall: {metrics_df.loc['macro avg', 'recall']:.4f}")
print(f"Macro Avg F1-score: {metrics_df.loc['macro avg', 'f1-score']:.4f}")
print(f"Weighted Avg Precision: {metrics_df.loc['weighted avg', 'precision']:.4f}")
print(f"Weighted Avg Recall: {metrics_df.loc['weighted avg', 'recall']:.4f}")
print(f"Weighted Avg F1-score: {metrics_df.loc['weighted avg', 'f1-score']:.4f}")

print("\nDetailed Metrics by Class:")
# Filter out the average rows for the detailed view
detailed_metrics = metrics_df[~metrics_df.index.isin(['accuracy', 'macro avg', 'weighted avg'])]
print(detailed_metrics)

# Save detailed metrics to CSV
metrics_df.to_csv('detailed_metrics.csv')
print("\nDetailed metrics saved to 'detailed_metrics.csv'")

# Create visualizations
plt.figure(figsize=(15, 8))

# Plot precision, recall, and f1-score for each class
classes = [c for c in detailed_metrics.index]
x = np.arange(len(classes))
width = 0.25

plt.bar(x - width, detailed_metrics['precision'], width, label='Precision')
plt.bar(x, detailed_metrics['recall'], width, label='Recall')
plt.bar(x + width, detailed_metrics['f1-score'], width, label='F1 Score')

plt.xlabel('Diagnosis Class')
plt.ylabel('Score')
plt.title('Precision, Recall, and F1 Score by Diagnosis Class')
plt.xticks(x, classes, rotation=45, ha='right')
plt.legend()
plt.tight_layout()
plt.savefig('metrics_by_class.png', dpi=300, bbox_inches='tight')
print("\nMetrics visualization saved as 'metrics_by_class.png'")

# Create confusion matrix heatmap
plt.figure(figsize=(15, 12))
cm = confusion_matrix(data['expected_diagnosis_lower'], data['actual_diagnosis_lower'])
unique_labels = sorted(set(data['expected_diagnosis_lower'].unique()) | set(data['actual_diagnosis_lower'].unique()))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=unique_labels,
            yticklabels=unique_labels)
plt.title('Confusion Matrix (Case-Insensitive)')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('confusion_matrix_heatmap.png', dpi=300, bbox_inches='tight')
print("Confusion matrix heatmap saved as 'confusion_matrix_heatmap.png'") 