import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import numpy as np
from typing import List, Dict, Any
from datetime import datetime

class ResultsVisualizer:
    """Class to create visualizations from test results"""
    
    def __init__(self, csv_file, output_dir=None):
        """
        Initialize the visualizer with the results CSV file
        
        Args:
            csv_file (str): Path to the CSV file containing test results
            output_dir (str): Directory to save visualizations (default: charts_TIMESTAMP)
        """
        self.csv_file = csv_file
        
        if output_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_dir = f"charts_{timestamp}"
        else:
            self.output_dir = output_dir
            
        # Create the output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        # Load the data
        self.df = pd.read_csv(csv_file)
        
        # Set the style for all plots
        plt.style.use('seaborn-v0_8-whitegrid')
        
    def load_data(self):
        """Load the data from the CSV file"""
        try:
            self.df = pd.read_csv(self.csv_file)
            # Clean disorder names for better display
            self.df['Disorder'] = self.df['Disorder'].str.replace('_', ' ').str.title()
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
            
    def generate_all_visualizations(self):
        """Generate all visualizations"""
        if not self.load_data():
            return False
            
        print(f"Generating visualizations in {self.output_dir}...")
        
        self.plot_accuracy_bar_chart()
        self.plot_metrics_grouped_bar()
        self.plot_metrics_heatmap()
        self.plot_radar_charts()
        self.generate_summary_statistics()
        
        print(f"All visualizations saved to {self.output_dir}")
        return True
        
    def plot_accuracy_bar_chart(self):
        """Create a bar chart comparing overall accuracy across disorders"""
        plt.figure(figsize=(12, 8))
        
        # Sort by accuracy for better visualization
        sorted_df = self.df.sort_values('Accuracy', ascending=False)
        
        # Create bar chart
        ax = sns.barplot(x='Disorder', y='Accuracy', data=sorted_df, palette='viridis')
        
        # Customize the plot
        plt.title('Accuracy by Disorder Type', fontsize=16)
        plt.xlabel('Disorder', fontsize=14)
        plt.ylabel('Accuracy', fontsize=14)
        plt.xticks(rotation=45, ha='right')
        plt.ylim(0, 1.0)
        
        # Add value labels on top of bars
        for i, v in enumerate(sorted_df['Accuracy']):
            ax.text(i, v + 0.01, f"{v:.2f}", ha='center', fontsize=10)
            
        # Add a horizontal line for average accuracy
        avg_accuracy = sorted_df['Accuracy'].mean()
        plt.axhline(y=avg_accuracy, color='red', linestyle='--', alpha=0.7)
        plt.text(len(sorted_df) - 1, avg_accuracy + 0.02, f"Avg: {avg_accuracy:.2f}", 
                 color='red', ha='right', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'accuracy_comparison.png'), dpi=300)
        plt.close()
        
    def plot_metrics_grouped_bar(self):
        """Create a grouped bar chart comparing all metrics"""
        plt.figure(figsize=(14, 8))
        
        # Sort by accuracy for consistency with other charts
        sorted_df = self.df.sort_values('Accuracy', ascending=False)
        
        # Melt the dataframe to get it in the right format for seaborn
        metrics = ['Accuracy', 'True_Positive_Rate', 'True_Negative_Rate']
        melted_df = pd.melt(sorted_df, id_vars=['Disorder'], value_vars=metrics, 
                           var_name='Metric', value_name='Value')
        
        # Rename metrics for better display
        metric_names = {'Accuracy': 'Accuracy', 
                      'True_Positive_Rate': 'Sensitivity', 
                      'True_Negative_Rate': 'Specificity'}
        melted_df['Metric'] = melted_df['Metric'].map(metric_names)
        
        # Create the grouped bar chart
        ax = sns.barplot(x='Disorder', y='Value', hue='Metric', data=melted_df, palette='viridis')
        
        # Customize the plot
        plt.title('Performance Metrics by Disorder Type', fontsize=16)
        plt.xlabel('Disorder', fontsize=14)
        plt.ylabel('Value', fontsize=14)
        plt.xticks(rotation=45, ha='right')
        plt.ylim(0, 1.0)
        plt.legend(title='Metric')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'metrics_comparison.png'), dpi=300)
        plt.close()
        
    def plot_metrics_heatmap(self):
        """Create a heatmap of performance metrics"""
        plt.figure(figsize=(12, 10))
        
        # Sort by accuracy for consistency
        sorted_df = self.df.sort_values('Accuracy', ascending=False)
        
        # Select and rename columns for the heatmap
        heatmap_df = sorted_df[['Disorder', 'Accuracy', 'True_Positive_Rate', 'True_Negative_Rate',
                              'False_Positive_Rate', 'False_Negative_Rate']]
        
        # Rename columns for better display
        column_names = {
            'True_Positive_Rate': 'Sensitivity',
            'True_Negative_Rate': 'Specificity',
            'False_Positive_Rate': 'False Alarm Rate',
            'False_Negative_Rate': 'Miss Rate'
        }
        heatmap_df = heatmap_df.rename(columns=column_names)
        
        # Set Disorder as index
        heatmap_df = heatmap_df.set_index('Disorder')
        
        # Create the heatmap
        ax = sns.heatmap(heatmap_df, annot=True, cmap='viridis', fmt='.2f',
                        linewidths=.5, cbar_kws={'label': 'Value'})
        
        plt.title('Performance Metrics Heatmap', fontsize=16)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'metrics_heatmap.png'), dpi=300)
        plt.close()
        
    def plot_radar_charts(self):
        """Create radar charts for each disorder"""
        # Create a separate radar chart for each disorder
        for _, row in self.df.iterrows():
            self._create_radar_chart(row)
            
        # Create an aggregate radar chart with average values
        avg_values = self.df[['Accuracy', 'True_Positive_Rate', 'True_Negative_Rate', 
                           'Precision', 'F1_Score']].mean()
        avg_row = pd.Series({
            'Disorder': 'Average',
            'Accuracy': avg_values['Accuracy'],
            'True_Positive_Rate': avg_values['True_Positive_Rate'],
            'True_Negative_Rate': avg_values['True_Negative_Rate'],
            'Precision': avg_values['Precision'],
            'F1_Score': avg_values['F1_Score']
        })
        self._create_radar_chart(avg_row, is_average=True)
        
    def _create_radar_chart(self, row, is_average=False):
        """
        Create a radar chart for a single disorder
        
        Args:
            row (pd.Series): Row containing the metrics for a single disorder
            is_average (bool): Whether this is the average across all disorders
        """
        # Metrics to include in the radar chart
        metrics = ['Accuracy', 'True_Positive_Rate', 'True_Negative_Rate', 'Precision', 'F1_Score']
        
        # Rename metrics for better display
        metric_names = {
            'Accuracy': 'Accuracy',
            'True_Positive_Rate': 'Sensitivity',
            'True_Negative_Rate': 'Specificity',
            'Precision': 'Precision',
            'F1_Score': 'F1 Score'
        }
        
        # Get values
        values = [row[metric] for metric in metrics]
        
        # Number of variables
        N = len(metrics)
        
        # What will be the angle of each axis in the plot
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]  # Close the loop
        
        # Values for the plot
        values += values[:1]  # Close the loop
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        
        # Draw the chart
        ax.plot(angles, values, linewidth=2, linestyle='solid')
        ax.fill(angles, values, alpha=0.25)
        
        # Fix axis to go in the right order and start at 12 o'clock
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        
        # Draw axis lines for each angle and label
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels([metric_names[m] for m in metrics])
        
        # Draw y-axis labels (0.25, 0.5, 0.75, 1.0)
        ax.set_yticks([0.25, 0.5, 0.75, 1.0])
        ax.set_yticklabels(['0.25', '0.5', '0.75', '1.0'])
        ax.set_ylim(0, 1)
        
        # Add title
        disorder_name = row['Disorder']
        if is_average:
            plt.title(f"Average Performance Across All Disorders", fontsize=15, y=1.1)
            filename = 'average_radar.png'
        else:
            plt.title(f"Performance Metrics for {disorder_name}", fontsize=15, y=1.1)
            filename = f"{disorder_name.lower().replace(' ', '_')}_radar.png"
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename), dpi=300)
        plt.close()
        
    def generate_summary_statistics(self):
        """Generate summary statistics and save to a text file"""
        # Calculate averages
        avg_metrics = self.df[['Accuracy', 'True_Positive_Rate', 'True_Negative_Rate', 
                            'Precision', 'F1_Score', 'Total_Cases', 'Total_Correct']].mean()
        
        # Calculate standard deviations
        std_metrics = self.df[['Accuracy', 'True_Positive_Rate', 'True_Negative_Rate', 
                            'Precision', 'F1_Score']].std()
        
        # Calculate min and max values
        min_metrics = self.df[['Accuracy', 'True_Positive_Rate', 'True_Negative_Rate', 
                            'Precision', 'F1_Score']].min()
        max_metrics = self.df[['Accuracy', 'True_Positive_Rate', 'True_Negative_Rate', 
                            'Precision', 'F1_Score']].max()
        
        # Get best and worst performing disorders
        best_idx = self.df['Accuracy'].idxmax()
        worst_idx = self.df['Accuracy'].idxmin()
        
        best_disorder = self.df.loc[best_idx, 'Disorder']
        worst_disorder = self.df.loc[worst_idx, 'Disorder']
        
        # Create a summary text file
        with open(os.path.join(self.output_dir, 'summary_statistics.txt'), 'w') as f:
            f.write("SUMMARY STATISTICS\n")
            f.write("=================\n\n")
            
            f.write("Average Performance Metrics:\n")
            f.write(f"- Accuracy: {avg_metrics['Accuracy']:.4f}\n")
            f.write(f"- Sensitivity (TPR): {avg_metrics['True_Positive_Rate']:.4f}\n")
            f.write(f"- Specificity (TNR): {avg_metrics['True_Negative_Rate']:.4f}\n")
            f.write(f"- Precision: {avg_metrics['Precision']:.4f}\n")
            f.write(f"- F1 Score: {avg_metrics['F1_Score']:.4f}\n\n")
            
            f.write("Standard Deviations:\n")
            f.write(f"- Accuracy: {std_metrics['Accuracy']:.4f}\n")
            f.write(f"- Sensitivity (TPR): {std_metrics['True_Positive_Rate']:.4f}\n")
            f.write(f"- Specificity (TNR): {std_metrics['True_Negative_Rate']:.4f}\n")
            f.write(f"- Precision: {std_metrics['Precision']:.4f}\n")
            f.write(f"- F1 Score: {std_metrics['F1_Score']:.4f}\n\n")
            
            f.write("Min/Max Performance:\n")
            f.write(f"- Min Accuracy: {min_metrics['Accuracy']:.4f}\n")
            f.write(f"- Max Accuracy: {max_metrics['Accuracy']:.4f}\n\n")
            
            f.write(f"Best Performing Disorder: {best_disorder} (Accuracy: {self.df.loc[best_idx, 'Accuracy']:.4f})\n")
            f.write(f"Worst Performing Disorder: {worst_disorder} (Accuracy: {self.df.loc[worst_idx, 'Accuracy']:.4f})\n\n")
            
            f.write(f"Total Test Cases: {int(avg_metrics['Total_Cases'] * len(self.df))}\n")
            f.write(f"Overall Correct Cases: {int(avg_metrics['Total_Correct'] * len(self.df))}\n")
            f.write(f"Average Cases per Disorder: {avg_metrics['Total_Cases']:.1f}\n\n")
            
            f.write("Performance Breakdown by Disorder:\n")
            for _, row in self.df.sort_values('Accuracy', ascending=False).iterrows():
                f.write(f"- {row['Disorder']}: Accuracy={row['Accuracy']:.4f}, ")
                f.write(f"TPR={row['True_Positive_Rate']:.4f}, TNR={row['True_Negative_Rate']:.4f}, ")
                f.write(f"Cases={int(row['Total_Cases'])}, Correct={int(row['Total_Correct'])}\n")
                
        # Create a summary figure
        plt.figure(figsize=(10, 6))
        
        # Plot average metrics with error bars
        metrics = ['Accuracy', 'True_Positive_Rate', 'True_Negative_Rate', 'Precision', 'F1_Score']
        metric_names = ['Accuracy', 'Sensitivity', 'Specificity', 'Precision', 'F1 Score']
        
        avg_values = [avg_metrics[m] for m in metrics]
        std_values = [std_metrics[m] for m in metrics]
        
        plt.bar(metric_names, avg_values, yerr=std_values, capsize=10, color='skyblue', alpha=0.7)
        
        # Customize the plot
        plt.title('Average Performance Metrics Across All Disorders', fontsize=16)
        plt.ylabel('Value', fontsize=14)
        plt.ylim(0, 1.0)
        
        # Add value labels on top of bars
        for i, v in enumerate(avg_values):
            plt.text(i, v + std_values[i] + 0.02, f"{v:.2f}", ha='center', fontsize=10)
            
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'summary_metrics.png'), dpi=300)
        plt.close()


def main():
    """Main function to parse arguments and run the visualizer"""
    parser = argparse.ArgumentParser(description='Generate visualizations from test results')
    parser.add_argument('--csv', required=True, help='Path to the CSV file with test results')
    parser.add_argument('--output', help='Directory to save visualizations')
    args = parser.parse_args()
    
    # Create the visualizer
    visualizer = ResultsVisualizer(args.csv, args.output)
    
    # Generate all visualizations
    success = visualizer.generate_all_visualizations()
    
    if success:
        print("Visualization generation complete!")
    else:
        print("Failed to generate visualizations.")


if __name__ == "__main__":
    main() 