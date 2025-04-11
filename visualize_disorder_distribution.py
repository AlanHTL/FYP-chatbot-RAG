import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Read the original results file
df = pd.read_csv('results/test_results_20250411_033126/all_results.csv')

# Count occurrences of each disorder
disorder_counts = df['expected_diagnosis'].value_counts()

# Create a bar plot
plt.figure(figsize=(15, 8))
sns.set_style("whitegrid")
ax = sns.barplot(x=disorder_counts.index, y=disorder_counts.values)

# Customize the plot
plt.title('Distribution of Disorders in Test Dataset', fontsize=16, pad=20)
plt.xlabel('Disorder Type', fontsize=12)
plt.ylabel('Number of Cases', fontsize=12)
plt.xticks(rotation=45, ha='right', fontsize=10)
plt.yticks(fontsize=10)

# Add value labels on top of each bar
for i, v in enumerate(disorder_counts.values):
    ax.text(i, v + 0.5, str(v), ha='center', fontsize=10)

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Save the plot
plt.savefig('results/test_results_20250411_033126/disorder_distribution.png', dpi=300, bbox_inches='tight')
plt.close() 