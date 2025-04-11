import pandas as pd
import numpy as np

# Read the confusion matrix
df = pd.read_csv('results/test_results_20250411_033126/confusion_matrix.csv', index_col=0)

# Initialize metrics list
metrics = []

# Calculate metrics for each diagnosis
for expected_diagnosis in df.columns:
    # Find the matching actual diagnosis row (some diagnoses might have slightly different names)
    matching_actual = [idx for idx in df.index if idx.lower().strip() == expected_diagnosis.lower().strip()]
    actual_diagnosis = matching_actual[0] if matching_actual else None
    
    if actual_diagnosis:
        # True Positives: Correct predictions
        tp = df.loc[actual_diagnosis, expected_diagnosis]
        
        # False Positives: Other diagnoses predicted as this one
        fp = df[expected_diagnosis].sum() - tp
        
        # False Negatives: This diagnosis predicted as something else
        fn = df.loc[actual_diagnosis].sum() - tp
        
        # True Negatives: All other correct predictions
        tn = df.values.sum() - (tp + fp + fn)
        
        # Calculate metrics
        accuracy = (tp + tn) / df.values.sum()
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        metrics.append({
            'Diagnosis': expected_diagnosis,
            'True Positives': int(tp),
            'False Positives': int(fp),
            'False Negatives': int(fn),
            'True Negatives': int(tn),
            'Accuracy': accuracy,
            'Precision': precision,
            'Recall': recall,
            'F1-Score': f1_score
        })

# Create metrics DataFrame
metrics_df = pd.DataFrame(metrics)

# Calculate overall metrics
total_samples = df.values.sum()
total_correct = sum(df.loc[diag, diag] for diag in df.index if diag in df.columns)

# Calculate macro-averaged metrics
overall_accuracy = total_correct / total_samples
overall_precision = metrics_df['Precision'].mean()
overall_recall = metrics_df['Recall'].mean()
overall_f1 = 2 * (overall_precision * overall_recall) / (overall_precision + overall_recall) if (overall_precision + overall_recall) > 0 else 0

# Add overall metrics
overall_metrics = pd.DataFrame([{
    'Diagnosis': 'Overall (Macro Average)',
    'True Positives': int(total_correct),
    'False Positives': int(total_samples - total_correct),
    'False Negatives': int(total_samples - total_correct),
    'True Negatives': 0,  # Not applicable for multiclass
    'Accuracy': overall_accuracy,
    'Precision': overall_precision,
    'Recall': overall_recall,
    'F1-Score': overall_f1
}])

# Combine individual and overall metrics
final_metrics = pd.concat([metrics_df, overall_metrics], ignore_index=True)

# Round floating point numbers to 4 decimal places
float_columns = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
final_metrics[float_columns] = final_metrics[float_columns].round(4)

# Sort by F1-Score in descending order, keeping Overall at the bottom
final_metrics = pd.concat([
    final_metrics[final_metrics['Diagnosis'] != 'Overall (Macro Average)'].sort_values('F1-Score', ascending=False),
    final_metrics[final_metrics['Diagnosis'] == 'Overall (Macro Average)']
])

# Save to CSV
final_metrics.to_csv('results/test_results_20250411_033126/accuracy_metrics.csv', index=False) 