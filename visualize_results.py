import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Any

class ResultsVisualizer:
    """Class for generating visualizations from test results."""
    
    def __init__(self, results_csv: str, output_dir: str):
        """Initialize the visualizer with results data and output directory."""
        self.results_csv = results_csv
        self.output_dir = output_dir
        self.df = pd.read_csv(results_csv)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Try to use seaborn style, fall back to default if not available
        try:
            plt.style.use('seaborn')
        except Exception as e:
            print(f"Warning: Could not use seaborn style: {e}")
            print("Using default matplotlib style instead.")
            plt.style.use('default')
        
    def plot_accuracy_by_disorder(self):
        """Create a bar plot of accuracy by disorder."""
        plt.figure(figsize=(15, 8))
        
        # Calculate accuracy for each disorder
        accuracy_by_disorder = self.df.groupby('Disorder')['correct'].mean().sort_values(ascending=False)
        
        # Create bar plot
        ax = accuracy_by_disorder.plot(kind='bar')
        plt.title('Accuracy by Disorder Type')
        plt.xlabel('Disorder')
        plt.ylabel('Accuracy')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Save plot
        plt.savefig(os.path.join(self.output_dir, 'accuracy_by_disorder.png'))
        plt.close()
        
    def plot_confidence_distribution(self):
        """Create a box plot of confidence scores by disorder."""
        plt.figure(figsize=(15, 8))
        
        # Create box plot
        sns.boxplot(x='Disorder', y='confidence', data=self.df)
        plt.title('Confidence Score Distribution by Disorder')
        plt.xlabel('Disorder')
        plt.ylabel('Confidence Score')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Save plot
        plt.savefig(os.path.join(self.output_dir, 'confidence_distribution.png'))
        plt.close()
        
    def plot_confusion_matrix(self):
        """Create a confusion matrix of expected vs actual diagnoses."""
        plt.figure(figsize=(15, 15))
        
        # Create confusion matrix
        confusion = pd.crosstab(
            self.df['expected_diagnosis'],
            self.df['actual_diagnosis'],
            normalize='index'
        )
        
        # Create heatmap
        sns.heatmap(
            confusion,
            annot=True,
            fmt='.2f',
            cmap='YlOrRd',
            cbar_kws={'label': 'Proportion of Cases'}
        )
        plt.title('Confusion Matrix of Expected vs Actual Diagnoses')
        plt.xlabel('Actual Diagnosis')
        plt.ylabel('Expected Diagnosis')
        plt.tight_layout()
        
        # Save plot
        plt.savefig(os.path.join(self.output_dir, 'confusion_matrix.png'))
        plt.close()
        
    def plot_case_distribution(self):
        """Create a pie chart showing the distribution of test cases."""
        plt.figure(figsize=(12, 8))
        
        # Count cases by disorder
        case_counts = self.df['Disorder'].value_counts()
        
        # Create pie chart
        plt.pie(
            case_counts.values,
            labels=case_counts.index,
            autopct='%1.1f%%',
            startangle=90
        )
        plt.title('Distribution of Test Cases by Disorder')
        plt.axis('equal')
        
        # Save plot
        plt.savefig(os.path.join(self.output_dir, 'case_distribution.png'))
        plt.close()
        
    def plot_accuracy_vs_confidence(self):
        """Create a scatter plot of accuracy vs confidence."""
        plt.figure(figsize=(12, 8))
        
        # Create scatter plot
        sns.scatterplot(
            data=self.df,
            x='confidence',
            y='correct',
            hue='Disorder',
            alpha=0.6
        )
        plt.title('Accuracy vs Confidence Score')
        plt.xlabel('Confidence Score')
        plt.ylabel('Correct (1) / Incorrect (0)')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        # Save plot
        plt.savefig(os.path.join(self.output_dir, 'accuracy_vs_confidence.png'))
        plt.close()
        
    def plot_accuracy_matrix(self):
        """Create an accuracy matrix showing correct vs incorrect diagnoses by disorder."""
        plt.figure(figsize=(15, 10))
        
        # Create a pivot table of correct vs incorrect by disorder
        accuracy_matrix = self.df.pivot_table(
            index='Disorder',
            columns='correct',
            values='case_id',
            aggfunc='count',
            fill_value=0
        )
        
        # Rename columns for clarity
        accuracy_matrix.columns = ['Incorrect', 'Correct']
        
        # Calculate total cases and accuracy percentage
        accuracy_matrix['Total Cases'] = accuracy_matrix['Correct'] + accuracy_matrix['Incorrect']
        accuracy_matrix['Accuracy %'] = (accuracy_matrix['Correct'] / accuracy_matrix['Total Cases'] * 100).round(1)
        
        # Create the plot
        ax = accuracy_matrix[['Correct', 'Incorrect']].plot(
            kind='bar',
            stacked=True,
            color=['#2ecc71', '#e74c3c']
        )
        
        # Add accuracy percentage labels
        for i, (_, row) in enumerate(accuracy_matrix.iterrows()):
            ax.text(i, row['Total Cases'] + 1, f"{row['Accuracy %']}%",
                   ha='center', va='bottom', fontsize=10)
        
        plt.title('Diagnosis Accuracy by Disorder')
        plt.xlabel('Disorder')
        plt.ylabel('Number of Cases')
        plt.xticks(rotation=45, ha='right')
        plt.legend(title='Diagnosis')
        plt.tight_layout()
        
        # Save plot
        plt.savefig(os.path.join(self.output_dir, 'accuracy_matrix.png'))
        plt.close()
        
    def plot_diagnosis_distribution(self):
        """Create a pie chart showing the distribution of actual diagnoses."""
        plt.figure(figsize=(15, 10))
        
        # Count cases by actual diagnosis
        diagnosis_counts = self.df['actual_diagnosis'].value_counts()
        
        # Create pie chart
        plt.pie(
            diagnosis_counts.values,
            labels=diagnosis_counts.index,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 8}
        )
        plt.title('Distribution of Actual Diagnoses')
        plt.axis('equal')
        
        # Save plot
        plt.savefig(os.path.join(self.output_dir, 'diagnosis_distribution.png'))
        plt.close()
        
    def generate_all_visualizations(self) -> bool:
        """Generate all available visualizations."""
        try:
            self.plot_accuracy_matrix()
            self.plot_diagnosis_distribution()
            return True
        except Exception as e:
            print(f"Error generating visualizations: {e}")
            return False 