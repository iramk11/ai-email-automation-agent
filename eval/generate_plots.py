#!/usr/bin/env python3
"""
Generate plots for evaluation results.
"""
import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path
import seaborn as sns

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11

def load_results(filepath):
    """Load evaluation results."""
    with open(filepath, 'r') as f:
        return json.load(f)

def plot_metric_distribution(results, output_dir):
    """Plot distribution of key metrics across emails."""
    data = results['results']
    
    # Extract metrics
    artifact_f1 = [r['metrics']['artifact_hit_rate']['f1'] for r in data]
    intent_f1 = [r['metrics'].get('intent_hit_rate', {}).get('f1', 0) for r in data]
    rouge_l = [r['metrics']['rouge_scores']['rougeL'] for r in data]
    expert_overall = [r['metrics']['expert_scores']['expert_overall'] for r in data]
    llm_judge = [r['metrics']['llm_judge_scores'].get('average_score', 0) 
                 for r in data if 'error' not in r['metrics']['llm_judge_scores']]
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Metric Distributions Across 20 Emails', fontsize=16, fontweight='bold')
    
    # Artifact F1
    axes[0, 0].hist(artifact_f1, bins=10, color='#3498db', alpha=0.7, edgecolor='black')
    axes[0, 0].axvline(np.mean(artifact_f1), color='red', linestyle='--', linewidth=2, label=f'Mean: {np.mean(artifact_f1):.3f}')
    axes[0, 0].set_title('Artifact Hit Rate (F1)', fontweight='bold')
    axes[0, 0].set_xlabel('F1 Score')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Intent F1
    axes[0, 1].hist(intent_f1, bins=10, color='#2ecc71', alpha=0.7, edgecolor='black')
    axes[0, 1].axvline(np.mean(intent_f1), color='red', linestyle='--', linewidth=2, label=f'Mean: {np.mean(intent_f1):.3f}')
    axes[0, 1].set_title('Intent Hit Rate (F1)', fontweight='bold')
    axes[0, 1].set_xlabel('F1 Score')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # ROUGE-L
    axes[0, 2].hist(rouge_l, bins=10, color='#e74c3c', alpha=0.7, edgecolor='black')
    axes[0, 2].axvline(np.mean(rouge_l), color='red', linestyle='--', linewidth=2, label=f'Mean: {np.mean(rouge_l):.3f}')
    axes[0, 2].set_title('ROUGE-L Score', fontweight='bold')
    axes[0, 2].set_xlabel('ROUGE-L Score')
    axes[0, 2].set_ylabel('Frequency')
    axes[0, 2].legend()
    axes[0, 2].grid(True, alpha=0.3)
    
    # ExPerT Overall
    axes[1, 0].hist(expert_overall, bins=10, color='#f39c12', alpha=0.7, edgecolor='black')
    axes[1, 0].axvline(np.mean(expert_overall), color='red', linestyle='--', linewidth=2, label=f'Mean: {np.mean(expert_overall):.3f}')
    axes[1, 0].set_title('ExPerT Overall Score', fontweight='bold')
    axes[1, 0].set_xlabel('ExPerT Score')
    axes[1, 0].set_ylabel('Frequency')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # LLM Judge
    if llm_judge:
        axes[1, 1].hist(llm_judge, bins=10, color='#9b59b6', alpha=0.7, edgecolor='black')
        axes[1, 1].axvline(np.mean(llm_judge), color='red', linestyle='--', linewidth=2, label=f'Mean: {np.mean(llm_judge):.3f}')
        axes[1, 1].set_title('LLM-as-a-Judge Average Score', fontweight='bold')
        axes[1, 1].set_xlabel('Average Score (1-5)')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
    
    # Combined comparison
    metrics_data = {
        'Artifact F1': artifact_f1,
        'Intent F1': intent_f1,
        'ROUGE-L': rouge_l,
        'ExPerT': expert_overall
    }
    axes[1, 2].boxplot(metrics_data.values(), labels=metrics_data.keys(), patch_artist=True,
                       boxprops=dict(facecolor='lightblue', alpha=0.7))
    axes[1, 2].set_title('Metric Comparison (Box Plot)', fontweight='bold')
    axes[1, 2].set_ylabel('Score')
    axes[1, 2].grid(True, alpha=0.3)
    axes[1, 2].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'metric_distributions.png', dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_dir / 'metric_distributions.png'}")
    plt.close()

def plot_aggregate_metrics(agg_metrics, output_dir):
    """Plot aggregate metrics as bar charts."""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Aggregate Evaluation Metrics', fontsize=16, fontweight='bold')
    
    # Artifact Hit Rate
    art = agg_metrics['artifact_hit_rate']
    ax1 = axes[0, 0]
    bars1 = ax1.bar(['Precision', 'Recall', 'F1', 'Exact Match'], 
                    [art['mean_precision'], art['mean_recall'], art['mean_f1'], art['exact_match_rate']],
                    color=['#3498db', '#2ecc71', '#e74c3c', '#f39c12'], alpha=0.7, edgecolor='black')
    ax1.set_title('Artifact Hit Rate', fontweight='bold', fontsize=12)
    ax1.set_ylabel('Score')
    ax1.set_ylim(0, 1.1)
    ax1.grid(True, alpha=0.3, axis='y')
    for i, (bar, val) in enumerate(zip(bars1, [art['mean_precision'], art['mean_recall'], art['mean_f1'], art['exact_match_rate']])):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, 
                f'{val:.3f}', ha='center', va='bottom', fontweight='bold')
    
    # Intent Hit Rate
    intent = agg_metrics['intent_hit_rate']
    ax2 = axes[0, 1]
    bars2 = ax2.bar(['Precision', 'Recall', 'F1', 'Exact Match'], 
                    [intent['mean_precision'], intent['mean_recall'], intent['mean_f1'], intent['exact_match_rate']],
                    color=['#3498db', '#2ecc71', '#e74c3c', '#f39c12'], alpha=0.7, edgecolor='black')
    ax2.set_title('Intent Hit Rate', fontweight='bold', fontsize=12)
    ax2.set_ylabel('Score')
    ax2.set_ylim(0, 1.1)
    ax2.grid(True, alpha=0.3, axis='y')
    for i, (bar, val) in enumerate(zip(bars2, [intent['mean_precision'], intent['mean_recall'], intent['mean_f1'], intent['exact_match_rate']])):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, 
                f'{val:.3f}', ha='center', va='bottom', fontweight='bold')
    
    # ROUGE Scores
    rouge = agg_metrics['rouge_scores']
    ax3 = axes[1, 0]
    bars3 = ax3.bar(['ROUGE-1', 'ROUGE-2', 'ROUGE-L'], 
                    [rouge['mean_rouge1'], rouge['mean_rouge2'], rouge['mean_rougeL']],
                    color=['#e74c3c', '#c0392b', '#a93226'], alpha=0.7, edgecolor='black')
    ax3.set_title('ROUGE Scores', fontweight='bold', fontsize=12)
    ax3.set_ylabel('Score')
    ax3.set_ylim(0, 1.0)
    ax3.grid(True, alpha=0.3, axis='y')
    for bar, val in zip(bars3, [rouge['mean_rouge1'], rouge['mean_rouge2'], rouge['mean_rougeL']]):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, 
                f'{val:.3f}', ha='center', va='bottom', fontweight='bold')
    
    # ExPerT and LLM Judge
    expert = agg_metrics['expert_scores']
    llm = agg_metrics['llm_judge']
    ax4 = axes[1, 1]
    bars4 = ax4.bar(['ExPerT\nOverall', 'ExPerT\nSemantic', 'ExPerT\nStyle', 'LLM Judge\nAverage'], 
                    [expert['mean_overall'], expert['mean_semantic'], expert['mean_style'], 
                     llm['mean_average_score'] / 5.0],  # Normalize LLM judge to 0-1
                    color=['#9b59b6', '#8e44ad', '#7d3c98', '#6c3483'], alpha=0.7, edgecolor='black')
    ax4.set_title('ExPerT & LLM-as-a-Judge Scores', fontweight='bold', fontsize=12)
    ax4.set_ylabel('Score (Normalized)')
    ax4.set_ylim(0, 1.0)
    ax4.grid(True, alpha=0.3, axis='y')
    values = [expert['mean_overall'], expert['mean_semantic'], expert['mean_style'], llm['mean_average_score'] / 5.0]
    for bar, val in zip(bars4, values):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, 
                f'{val:.3f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'aggregate_metrics.png', dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_dir / 'aggregate_metrics.png'}")
    plt.close()

def plot_metric_correlation(results, output_dir):
    """Plot correlation between different metrics."""
    data = results['results']
    
    # Extract all metrics
    metrics = {
        'Artifact F1': [r['metrics']['artifact_hit_rate']['f1'] for r in data],
        'Intent F1': [r['metrics'].get('intent_hit_rate', {}).get('f1', 0) for r in data],
        'ROUGE-L': [r['metrics']['rouge_scores']['rougeL'] for r in data],
        'ExPerT Overall': [r['metrics']['expert_scores']['expert_overall'] for r in data],
        'LLM Judge': [r['metrics']['llm_judge_scores'].get('average_score', 0) / 5.0 
                     for r in data if 'error' not in r['metrics']['llm_judge_scores']]
    }
    
    # Filter to same length
    min_len = min(len(v) for v in metrics.values())
    metrics = {k: v[:min_len] for k, v in metrics.items()}
    
    # Calculate correlation matrix
    import pandas as pd
    df = pd.DataFrame(metrics)
    corr = df.corr()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(corr, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr.columns)))
    ax.set_yticks(range(len(corr.columns)))
    ax.set_xticklabels(corr.columns, rotation=45, ha='right')
    ax.set_yticklabels(corr.columns)
    
    # Add text annotations
    for i in range(len(corr.columns)):
        for j in range(len(corr.columns)):
            text = ax.text(j, i, f'{corr.iloc[i, j]:.2f}',
                          ha="center", va="center", color="black", fontweight='bold')
    
    ax.set_title('Metric Correlation Matrix', fontsize=14, fontweight='bold', pad=20)
    plt.colorbar(im, ax=ax, label='Correlation Coefficient')
    plt.tight_layout()
    plt.savefig(output_dir / 'metric_correlation.png', dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_dir / 'metric_correlation.png'}")
    plt.close()

def plot_performance_by_email(results, output_dir):
    """Plot performance metrics across all emails."""
    data = results['results']
    
    email_ids = [r['email_id'] for r in data]
    artifact_f1 = [r['metrics']['artifact_hit_rate']['f1'] for r in data]
    intent_f1 = [r['metrics'].get('intent_hit_rate', {}).get('f1', 0) for r in data]
    rouge_l = [r['metrics']['rouge_scores']['rougeL'] for r in data]
    
    fig, ax = plt.subplots(figsize=(16, 8))
    x = np.arange(len(email_ids))
    width = 0.25
    
    bars1 = ax.bar(x - width, artifact_f1, width, label='Artifact F1', color='#3498db', alpha=0.7)
    bars2 = ax.bar(x, intent_f1, width, label='Intent F1', color='#2ecc71', alpha=0.7)
    bars3 = ax.bar(x + width, rouge_l, width, label='ROUGE-L', color='#e74c3c', alpha=0.7)
    
    ax.set_xlabel('Email ID', fontweight='bold')
    ax.set_ylabel('Score', fontweight='bold')
    ax.set_title('Performance Metrics by Email', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(email_ids, rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim(0, 1.1)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'performance_by_email.png', dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_dir / 'performance_by_email.png'}")
    plt.close()

if __name__ == "__main__":
    import sys
    
    # Load results
    results_file = Path("eval/results/final_formatted_evaluation_results.json")
    if not results_file.exists():
        print(f"❌ Results file not found: {results_file}")
        sys.exit(1)
    
    results = load_results(results_file)
    output_dir = Path("eval/results/plots")
    output_dir.mkdir(exist_ok=True)
    
    print("📊 Generating plots...")
    plot_aggregate_metrics(results['aggregate_metrics'], output_dir)
    plot_metric_distribution(results, output_dir)
    plot_metric_correlation(results, output_dir)
    plot_performance_by_email(results, output_dir)
    
    print(f"\n✅ All plots saved to: {output_dir}")

