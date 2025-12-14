# Evaluation Pipeline Documentation

## Overview

This evaluation pipeline provides comprehensive benchmarking for the AI Email Automation Agent using multiple metrics to assess:
1. **Artifact Classification Accuracy** (Hit Rate)
2. **Reply Quality** (ROUGE scores)
3. **Distributional Style Match** (MAUVE)
4. **Personalized Text Quality** (ExPerT)
5. **Style Match via LLM-as-a-Judge**

## Installation

### 1. Install Evaluation Dependencies

```bash
cd /Users/iramkamdar/Downloads/AI_EMAIL_AUTOMATION_AGENT
pip install -r eval/requirements.txt
```

**Note**: Some dependencies may require additional setup:
- `mauve-text` requires PyTorch
- `sentence-transformers` requires transformers library

### 2. Ensure Backend Services are Ready

The evaluation pipeline uses the same backend services as the main application:
- **Ollama**: Must be running with the model (default: `llama3`)
- **Qdrant**: Database must be initialized with FAQ data
- **Graph**: NetworkX graph must be built from email pairs

## Usage

### Basic Usage (Test on First 5 Emails)

```bash
cd /Users/iramkamdar/Downloads/AI_EMAIL_AUTOMATION_AGENT
python eval/run_eval.py --limit 5
```

### Custom Dataset and Range

```bash
# Evaluate first 10 emails starting from index 0
python eval/run_eval.py --dataset data/golden_dataset_benchmark.json --limit 10 --start-idx 0

# Evaluate emails 5-15
python eval/run_eval.py --limit 10 --start-idx 5

# Custom output path
python eval/run_eval.py --limit 5 --output eval/results/my_results.json
```

### Full Dataset Evaluation

```bash
# Evaluate all emails (remove --limit)
python eval/run_eval.py --dataset data/golden_dataset_benchmark.json
```

## Metrics Explained

### 1. Artifact Hit Rate

**What it measures**: How accurately the system identifies which artifacts (resumes, links, etc.) are needed for a reply.

**Metrics**:
- **Precision**: Of predicted artifacts, how many were correct?
- **Recall**: Of ground truth artifacts, how many were found?
- **F1 Score**: Harmonic mean of precision and recall
- **Exact Match**: Percentage of emails where all artifacts matched exactly

**Example**:
- Ground Truth: `["ds_resume", "calendly"]`
- Predicted: `["ds_resume", "linkedin_profile"]`
- Precision: 0.5 (1 correct out of 2 predicted)
- Recall: 0.5 (1 found out of 2 expected)
- F1: 0.5
- Exact Match: 0.0

### 2. ROUGE Scores

**What it measures**: How similar the generated reply is to the ground truth reply in terms of overlapping n-grams.

**Metrics**:
- **ROUGE-1**: Overlap of unigrams (single words)
- **ROUGE-2**: Overlap of bigrams (word pairs)
- **ROUGE-L**: Longest common subsequence (captures sentence structure)

**Range**: 0.0 to 1.0 (higher is better)

**Interpretation**:
- > 0.5: Good overlap
- > 0.7: Very good overlap
- < 0.3: Poor overlap

### 3. MAUVE Score

**What it measures**: How similar the overall distribution of generated emails is to the distribution of real user emails.

**Range**: 0.0 to 1.0 (higher is better)

**Interpretation**:
- Measures if the model writes "like this person overall"
- Captures style, length, vocabulary patterns
- Requires multiple samples to calculate

### 4. ExPerT Score

**What it measures**: Personalized text quality combining semantic similarity and style matching.

**Components**:
- **Semantic**: How similar is the meaning to the reference?
- **Style**: How similar is the writing style to user's past emails?
- **Overall**: Weighted combination (60% semantic, 40% style)

**Range**: 0.0 to 1.0 (higher is better)

### 5. LLM-as-a-Judge

**What it measures**: Expert evaluation of style match using a rubric.

**Dimensions** (1-5 scale):
- **Tone Match**: Formality, warmth, politeness
- **Phrasing Style**: Similarity to user's typical phrasing
- **Structure**: Follows user's typical email structure
- **Content Appropriateness**: Contextually appropriate
- **Overall Style Match**: Overall assessment

**Average Score**: Mean of all dimensions

## Output Format

Results are saved as JSON with the following structure:

```json
{
  "total_emails": 5,
  "valid_results": 5,
  "errors": 0,
  "aggregate_metrics": {
    "artifact_hit_rate": {
      "mean_f1": 0.85,
      "mean_precision": 0.90,
      "mean_recall": 0.80,
      "exact_match_rate": 0.60
    },
    "rouge_scores": {
      "mean_rouge1": 0.65,
      "mean_rouge2": 0.45,
      "mean_rougeL": 0.60
    },
    "expert_scores": {
      "mean_overall": 0.75,
      "mean_semantic": 0.80,
      "mean_style": 0.70
    },
    "llm_judge": {
      "mean_average_score": 4.2
    },
    "mauve": {
      "mauve_score": 0.72
    }
  },
  "individual_results": [
    {
      "email_id": "benchmark_001",
      "prospect_email": "...",
      "ground_truth_reply": "...",
      "generated_reply": "...",
      "artifact_metrics": {...},
      "rouge_scores": {...},
      "expert_scores": {...},
      "llm_judge_scores": {...}
    },
    ...
  ]
}
```

## Architecture

```
eval/
├── __init__.py
├── evaluator.py          # Main evaluation orchestrator
├── metrics.py            # All metric calculations
├── utils.py              # Helper functions
├── run_eval.py           # Entry point script
├── requirements.txt      # Evaluation dependencies
├── EVAL_DOCUMENTATION.md # This file
└── results/              # Output directory for results
```

## Evaluation Flow

1. **Initialize Services**: Loads RAG service, Qdrant, Graph, Ollama
2. **Load Dataset**: Reads golden benchmark dataset
3. **Get Style Examples**: Extracts user's past replies for style matching
4. **For Each Email**:
   - Generate reply using RAG pipeline
   - Extract predicted artifacts and intents
   - Calculate all metrics
5. **Aggregate**: Compute mean scores across all emails
6. **Save Results**: Write to JSON file

## Troubleshooting

### Issue: "Ollama not running"
**Solution**: Start Ollama service:
```bash
ollama serve
# In another terminal
ollama pull llama3
```

### Issue: "Qdrant database locked"
**Solution**: Close any Jupyter notebooks that might be using Qdrant

### Issue: "MAUVE calculation fails"
**Solution**: 
- Ensure PyTorch is installed: `pip install torch`
- MAUVE requires GPU or sufficient RAM for large datasets

### Issue: "Import errors"
**Solution**: Install all dependencies:
```bash
pip install -r eval/requirements.txt
```

### Issue: "Graph not found"
**Solution**: The evaluator will automatically rebuild the graph from `data/generated_email_pairs.json` if needed

## Performance Notes

- **Evaluation Time**: ~30-60 seconds per email (depends on Ollama model speed)
- **MAUVE Calculation**: Can take several minutes for larger datasets
- **LLM Judge**: Adds ~10-20 seconds per email

## Next Steps

1. **Expand Dataset**: Test on full 20-email golden dataset
2. **Baseline Comparison**: Compare against simpler baselines
3. **A/B Testing**: Test different prompt variations
4. **Error Analysis**: Analyze which emails fail and why
5. **Metric Correlation**: Understand which metrics correlate with human judgment

