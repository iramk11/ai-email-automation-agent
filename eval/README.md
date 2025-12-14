# Evaluation Pipeline

Comprehensive benchmarking pipeline for the AI Email Automation Agent.

## Quick Start

1. **Install dependencies**:
   ```bash
   # Install all dependencies (including evaluation dependencies)
   pip install -r requirements.txt
   
   # Or install only evaluation dependencies (if backend already installed)
   pip install rouge-score mauve-text pandas scikit-learn torch transformers
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
- Implementation details are covered in `EVAL_DOCUMENTATION.md`

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

