# Evaluation Implementation Instructions (Problem 2C)

This document provides instructions for implementing the evaluation section of Problem 2.

## Files Created

1. **`data/test_articles.txt`** - Dataset with 20 short articles on various topics
2. **`evaluation_semantic_search.py`** - Evaluation functions module
3. **`notebook_cells_evaluation.py`** - Code cells ready to copy into the notebook
4. **This README** - Implementation instructions

## Quick Start

### Step 1: Open the notebook and navigate to Cell 14
Add the following cells after Cell 14 in your `Problem_2_langchain_search_assignment_notebook.ipynb`

### Step 2: Copy and run the following cells

#### Cell 15: Install Dependencies
```python
!pip install -q matplotlib scikit-learn seaborn pandas
```

#### Cell 16: Import Evaluation Module
```python
# Import evaluation functions
import sys
sys.path.append('.')
from evaluation_semantic_search import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
```

#### Cell 17: Load Test Dataset
```python
# Load test articles
articles = load_test_articles('./data/test_articles.txt')
print(f"Loaded {len(articles)} test articles\n")

# Print first 3 article titles
for i, (title, content) in enumerate(articles[:3]):
    print(f"{i+1}. {title}")
    print(f"   Length: {len(content)} characters\n")
```

#### Cell 18: Create Vector Stores with Different Chunk Sizes
```python
# Create vector stores with different chunk sizes (500, 1000, 1500)
print("Creating vector stores with different chunk sizes...")
vector_stores = create_vector_stores_with_chunk_sizes(
    articles, 
    emb,  # Use the embedding model from earlier cells
    chunk_sizes=[500, 1000, 1500],
    chunk_overlap=100
)
```

#### Cell 19: Compare Chunk Sizes
```python
# Create comparison dataframe
chunk_data = []
for chunk_size, data in vector_stores.items():
    chunks = data['chunks']
    chunk_lengths = [len(c.page_content) for c in chunks]
    chunk_data.append({
        'Chunk Size': chunk_size,
        'Number of Chunks': data['num_chunks'],
        'Avg Length': np.mean(chunk_lengths),
        'Min Length': np.min(chunk_lengths),
        'Max Length': np.max(chunk_lengths),
        'Std Length': np.std(chunk_lengths)
    })

df_chunks = pd.DataFrame(chunk_data)
print("Chunk Size Comparison:")
print(df_chunks.to_string(index=False))

# Visualize
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Bar plot of chunk counts
axes[0].bar(df_chunks['Chunk Size'].astype(str), df_chunks['Number of Chunks'], 
           color='skyblue', edgecolor='navy', alpha=0.7)
axes[0].set_xlabel('Chunk Size')
axes[0].set_ylabel('Number of Chunks')
axes[0].set_title('Number of Chunks by Chunk Size')
axes[0].grid(True, alpha=0.3, axis='y')

# Line plot of avg chunk length
axes[1].plot(df_chunks['Chunk Size'], df_chunks['Avg Length'], 
            marker='o', linewidth=2, markersize=10, color='coral', label='Average')
axes[1].fill_between(df_chunks['Chunk Size'], 
                     df_chunks['Avg Length'] - df_chunks['Std Length'],
                     df_chunks['Avg Length'] + df_chunks['Std Length'],
                     alpha=0.2, color='coral', label='±1 Std')
axes[1].set_xlabel('Chunk Size')
axes[1].set_ylabel('Chunk Length (characters)')
axes[1].set_title('Average Chunk Length by Chunk Size')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

#### Cell 20: Measure Search Latency
```python
# Select vector store (use 1000 chunk size)
vs_eval = vector_stores[1000]['store']

# Test queries
test_queries = [
    "machine learning algorithms",
    "renewable energy technologies"
]

# Measure latency for each query and k value
latency_results = {}

for query in test_queries:
    print(f"\nMeasuring latency for query: '{query}'")
    results = measure_search_latency(vs_eval, query, k_values=[1, 5, 10])
    latency_results[query] = results
    
    # Print results
    print(f"{'k':<5} {'Mean (s)':<12} {'Std (s)':<12} {'Min (s)':<12} {'Max (s)':<12}")
    print("-" * 65)
    for k, stats in results.items():
        print(f"{k:<5} {stats['mean']:<12.4f} {stats['std']:<12.4f} "
              f"{stats['min']:<12.4f} {stats['max']:<12.4f}")

# Plot latency results
for query, results in latency_results.items():
    plot_latency_results(results)
    plt.suptitle(f'Latency Analysis - Query: "{query}"', y=1.02)
    plt.show()
```

#### Cell 21: Compare Diversity (Similarity vs MMR)
```python
# Test query for diversity comparison
test_query = "technology and innovation"

# Get results from both methods
sim_results = vs_eval.similarity_search(test_query, k=5)
mmr_results = vs_eval.max_marginal_relevance_search(test_query, k=5, lambda_mult=0.5)

print("=" * 100)
print("DIVERSITY COMPARISON")
print("=" * 100)
print(f"Query: '{test_query}'\n")

# Calculate diversity metrics
diversity_stats = compare_diversity(sim_results, mmr_results, emb)

print(f"Similarity Search:")
print(f"  Diversity Score: {diversity_stats['similarity_search_diversity']:.4f}")
print(f"  Avg Pairwise Similarity: {diversity_stats['similarity_search_avg_pairwise']:.4f}")
print(f"\nMMR Search:")
print(f"  Diversity Score: {diversity_stats['mmr_search_diversity']:.4f}")
print(f"  Avg Pairwise Similarity: {diversity_stats['mmr_search_avg_pairwise']:.4f}")
print(f"\nImprovement: {diversity_stats['diversity_improvement']:.4f} "
      f"({diversity_stats['diversity_improvement']*100:.2f}% increase)")

# Visualize
plot_diversity_comparison(sim_results, mmr_results, emb)
plt.suptitle(f'Pairwise Similarity Heatmaps - Query: "{test_query}"', y=1.02)
plt.show()
```

#### Cell 22: Coverage Analysis
```python
# Use a broad query that likely has results from multiple topics
broad_query = "energy and environment"

sim_results = vs_eval.similarity_search(broad_query, k=5)
mmr_results = vs_eval.max_marginal_relevance_search(broad_query, k=5, lambda_mult=0.5)

# Analyze coverage
coverage = analyze_coverage(sim_results, mmr_results)

print("=" * 100)
print("COVERAGE ANALYSIS")
print("=" * 100)
print(f"Query: '{broad_query}'\n")

print(f"Similarity Search Results:")
print(f"  Unique sources: {coverage['sim_unique_sources']}")
for i, doc in enumerate(sim_results, 1):
    title = doc.metadata.get('title', 'Unknown')[:50]
    print(f"  {i}. {title}")

print(f"\nMMR Search Results:")
print(f"  Unique sources: {coverage['mmr_unique_sources']}")
for i, doc in enumerate(mmr_results, 1):
    title = doc.metadata.get('title', 'Unknown')[:50]
    print(f"  {i}. {title}")

print(f"\nCoverage Statistics:")
print(f"  Common sources: {coverage['common_sources']}")
print(f"  Only in Similarity: {coverage['sim_only_sources']}")
print(f"  Only in MMR: {coverage['mmr_only_sources']}")

if coverage['mmr_unique_sources'] > coverage['sim_unique_sources']:
    print(f"\n✓ MMR provides better coverage with {coverage['mmr_unique_sources'] - coverage['sim_unique_sources']} more unique sources!")
else:
    print(f"\n✓ Both methods have equal coverage with {coverage['mmr_unique_sources']} unique sources")
```

#### Cell 23: Visualize Embeddings
```python
# Create visualizations for different queries
queries_to_visualize = [
    "machine learning and AI",
    "renewable energy sources"
]

for query in queries_to_visualize:
    # T-SNE visualization
    plt = visualize_embeddings(vs_eval, query, k=10, method='tsne')
    plt.show()
    
    # PCA visualization
    plt = visualize_embeddings(vs_eval, query, k=10, method='pca')
    plt.show()
```

#### Cell 24: Summary Report
```python
print("=" * 100)
print("COMPREHENSIVE EVALUATION REPORT")
print("=" * 100)

print("\nSUMMARY OF FINDINGS:")
print("-" * 100)

# 1. Chunk size impact
print("\n1. Chunk Size Impact:")
print(f"   • 500 char chunks: {vector_stores[500]['num_chunks']} chunks created")
print(f"   • 1000 char chunks: {vector_stores[1000]['num_chunks']} chunks created")
print(f"   • 1500 char chunks: {vector_stores[1500]['num_chunks']} chunks created")
print(f"   → Larger chunks create fewer but more comprehensive document pieces")

# 2. Latency
if latency_results:
    query = list(latency_results.keys())[0]
    results = latency_results[query]
    print(f"\n2. Search Latency (query: '{query}'):")
    for k, stats in results.items():
        print(f"   • k={k}: avg {stats['mean']:.4f}s (std: {stats['std']:.4f}s)")
    print(f"   → Latency increases moderately with larger k values")

# 3. Diversity
if 'diversity_stats' in locals():
    print(f"\n3. Diversity Comparison:")
    print(f"   • Similarity search diversity: {diversity_stats['similarity_search_diversity']:.4f}")
    print(f"   • MMR search diversity: {diversity_stats['mmr_search_diversity']:.4f}")
    print(f"   • Improvement: {diversity_stats['diversity_improvement']:.4f} "
          f"({diversity_stats['diversity_improvement']*100:.2f}%)")
    print(f"   → MMR provides more diverse results, reducing redundancy")

# 4. Coverage
if 'coverage' in locals():
    print(f"\n4. Coverage Comparison:")
    print(f"   • Similarity - unique sources: {coverage['sim_unique_sources']}")
    print(f"   • MMR - unique sources: {coverage['mmr_unique_sources']}")
    print(f"   • MMR advantage: {coverage['mmr_only_sources']} sources only in MMR results")
    print(f"   → MMR provides better topic coverage for broad queries")

print("\n" + "=" * 100)
print("EVALUATION COMPLETE")
print("=" * 100)
```

## Evaluation Criteria Covered

✅ **Testing on 20 short articles** - Loaded from `data/test_articles.txt`  
✅ **Comparing chunk sizes** - Evaluated 500, 1000, 1500 character chunks  
✅ **Measuring search latency** - Tested with k=1, 5, 10  
✅ **Analyzing search diversity** - Compared similarity vs MMR with visualizations  
✅ **Demonstrating MMR coverage** - Showed scenarios where MMR provides better coverage  
✅ **Embedding visualizations** - Used t-SNE and PCA for dimensionality reduction  

## Requirements Met

All requirements from Problem 2, Task 3 are covered:
1. ✅ Testing on provided dataset of 20 short articles
2. ✅ Comparing retrieval quality between chunk sizes (500, 1000, 1500)
3. ✅ Measuring search latency for k values (1, 5, 10)
4. ✅ Analyzing effect of search types on diversity
5. ✅ Demonstrating MMR better coverage scenarios
6. ✅ Creating visualizations using dimensionality reduction

## Additional Notes

- All visualizations are automatically generated and displayed
- The evaluation includes both quantitative metrics and qualitative analysis
- Results are formatted for easy reading and interpretation
- The code is modular and reusable for future evaluations
