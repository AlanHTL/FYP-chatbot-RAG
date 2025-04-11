import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the CSV file
data = pd.read_csv('results/test_results_20250411_143751/all_results.csv')

# Count occurrences of each expected diagnosis
disorder_counts = data['expected_diagnosis'].value_counts().sort_values(ascending=False)

# Create the plot
plt.figure(figsize=(14, 10))
colors = plt.cm.viridis(np.linspace(0, 0.9, len(disorder_counts)))
ax = disorder_counts.plot(kind='bar', color=colors)
plt.title('Number of Cases by Expected Diagnosis', fontsize=18, fontweight='bold')
plt.xlabel('Disorder', fontsize=14)
plt.ylabel('Number of Cases', fontsize=14)
plt.xticks(rotation=45, ha='right', fontsize=12)
plt.yticks(fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Add count labels on top of each bar
for i, v in enumerate(disorder_counts):
    ax.text(i, v + 0.3, str(v), ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig('expected_diagnosis_counts.png', dpi=300)
print('Enhanced graph saved as expected_diagnosis_counts.png')
print(disorder_counts) 