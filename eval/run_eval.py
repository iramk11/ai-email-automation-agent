#!/usr/bin/env python3
"""
Main entry point for evaluation pipeline.
Run this script to evaluate the AI Email Automation Agent.
"""
import logging
import sys
import argparse
from pathlib import Path
import asyncio
from datetime import datetime

import sys
from pathlib import Path
# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from eval.evaluator import EmailEvaluator
from eval.utils import save_results

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('eval/evaluation.log')
    ]
)
logger = logging.getLogger(__name__)


async def main():
    """Main evaluation function."""
    parser = argparse.ArgumentParser(description='Evaluate AI Email Automation Agent')
    parser.add_argument(
        '--dataset',
        type=str,
        default='data/golden_dataset_benchmark.json',
        help='Path to golden benchmark dataset'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=5,
        help='Number of emails to evaluate (default: 5 for testing)'
    )
    parser.add_argument(
        '--start-idx',
        type=int,
        default=0,
        help='Starting index in dataset (default: 0)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output path for results (default: eval/results/results_<timestamp>.json)'
    )
    
    args = parser.parse_args()
    
    # Resolve dataset path
    dataset_path = Path(args.dataset)
    if not dataset_path.is_absolute():
        dataset_path = Path(__file__).parent.parent / dataset_path
    
    if not dataset_path.exists():
        logger.error(f"Dataset not found: {dataset_path}")
        sys.exit(1)
    
    logger.info("="*70)
    logger.info("AI EMAIL AUTOMATION AGENT - EVALUATION PIPELINE")
    logger.info("="*70)
    logger.info(f"Dataset: {dataset_path}")
    logger.info(f"Limit: {args.limit}")
    logger.info(f"Start Index: {args.start_idx}")
    logger.info("="*70)
    
    try:
        # Initialize evaluator
        evaluator = EmailEvaluator(str(dataset_path))
        
        # Run evaluation
        results = await evaluator.evaluate_dataset(
            limit=args.limit,
            start_idx=args.start_idx
        )
        
        # Save results
        if args.output:
            output_path = args.output
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"eval/results/results_{timestamp}.json"
        
        save_results(results, output_path)
        
        # Print summary
        logger.info("\n" + "="*70)
        logger.info("EVALUATION SUMMARY")
        logger.info("="*70)
        
        agg = results.get("aggregate_metrics", {})
        
        logger.info(f"Total Emails: {results['total_emails']}")
        logger.info(f"Valid Results: {results['valid_results']}")
        logger.info(f"Errors: {results['errors']}")
        
        if "artifact_hit_rate" in agg:
            art = agg["artifact_hit_rate"]
            logger.info(f"\n📊 Artifact Hit Rate:")
            logger.info(f"   F1 Score: {art['mean_f1']:.3f}")
            logger.info(f"   Precision: {art['mean_precision']:.3f}")
            logger.info(f"   Recall: {art['mean_recall']:.3f}")
            logger.info(f"   Exact Match Rate: {art['exact_match_rate']:.3f}")
        
        if "intent_hit_rate" in agg:
            intent = agg["intent_hit_rate"]
            logger.info(f"\n📊 Intent Hit Rate:")
            logger.info(f"   F1 Score: {intent['mean_f1']:.3f}")
            logger.info(f"   Precision: {intent['mean_precision']:.3f}")
            logger.info(f"   Recall: {intent['mean_recall']:.3f}")
            logger.info(f"   Exact Match Rate: {intent['exact_match_rate']:.3f}")
        
        if "rouge_scores" in agg:
            rouge = agg["rouge_scores"]
            logger.info(f"\n📊 ROUGE Scores:")
            logger.info(f"   ROUGE-1: {rouge['mean_rouge1']:.3f}")
            logger.info(f"   ROUGE-2: {rouge['mean_rouge2']:.3f}")
            logger.info(f"   ROUGE-L: {rouge['mean_rougeL']:.3f}")
        
        if "expert_scores" in agg:
            expert = agg["expert_scores"]
            logger.info(f"\n📊 ExPerT Scores:")
            logger.info(f"   Overall: {expert['mean_overall']:.3f}")
            logger.info(f"   Semantic: {expert['mean_semantic']:.3f}")
            logger.info(f"   Style: {expert['mean_style']:.3f}")
        
        if "llm_judge" in agg:
            llm = agg["llm_judge"]
            logger.info(f"\n📊 LLM-as-a-Judge:")
            logger.info(f"   Average Score: {llm['mean_average_score']:.3f}")
        
        if "mauve" in agg:
            mauve = agg["mauve"]
            if "mauve_score" in mauve and mauve["mauve_score"] is not None:
                logger.info(f"\n📊 MAUVE Score:")
                logger.info(f"   MAUVE: {mauve['mauve_score']:.3f}")
            else:
                logger.info(f"\n📊 MAUVE Score: Not available")
        
        logger.info(f"\n✅ Results saved to: {output_path}")
        logger.info("="*70)
        
    except Exception as e:
        logger.error(f"Evaluation failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

