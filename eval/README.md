# Evaluation Pipeline

Comprehensive benchmarking pipeline for the AI Email Automation Agent.

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r eval/requirements.txt
   ```

2. **Validate setup**:
   ```bash
   python eval/validate_setup.py
   ```

3. **Run evaluation** (test on first 5 emails):
   ```bash
   python eval/run_eval.py --limit 5
   ```

## Documentation

- **[EVAL_DOCUMENTATION.md](EVAL_DOCUMENTATION.md)**: Comprehensive guide to all metrics and usage
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)**: Implementation details and design decisions

## Metrics

1. **Artifact Hit Rate**: Precision, Recall, F1, Exact Match
2. **ROUGE Scores**: ROUGE-1, ROUGE-2, ROUGE-L
3. **MAUVE**: Distributional style similarity
4. **ExPerT**: Personalized text quality (semantic + style)
5. **LLM-as-a-Judge**: 5-dimension style rubric evaluation

## Results

Results are saved to `eval/results/results_<timestamp>.json` with:
- Per-email detailed metrics
- Aggregate mean scores
- Error tracking

## Requirements

- Ollama running with model (default: `llama3`)
- Qdrant database initialized
- Graph built from email pairs
- Python 3.8+

See [EVAL_DOCUMENTATION.md](EVAL_DOCUMENTATION.md) for detailed setup instructions.

