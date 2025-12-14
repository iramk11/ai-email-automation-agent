#!/usr/bin/env python3
"""
Create a formatted JSON with prospect_email, actual_reply, generated_email, and all metrics.
"""
import json
import sys
from pathlib import Path

def format_results(input_file: str, output_file: str):
    """Format evaluation results into cleaner JSON."""
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    formatted_results = []
    
    for result in data.get("individual_results", []):
        if "error" in result:
            continue
        
        formatted_entry = {
            "prospect_email": result.get("prospect_email", ""),
            "actual_reply": result.get("ground_truth_reply", ""),
            "generated_email": result.get("generated_reply", ""),
            "metrics": {
                "artifact_hit_rate": result.get("artifact_metrics", {}),
                "intent_hit_rate": result.get("intent_metrics", {}),
                "rouge_scores": result.get("rouge_scores", {}),
                "expert_scores": result.get("expert_scores", {}),
                "llm_judge_scores": result.get("llm_judge_scores", {})
            },
            "predicted_artifacts": result.get("predicted_artifacts", []),
            "ground_truth_artifacts": result.get("ground_truth_artifacts", []),
            "predicted_intents": result.get("predicted_intents", []),
            "ground_truth_intents": result.get("ground_truth_intents", []),
            "email_id": result.get("email_id", "")
        }
        
        formatted_results.append(formatted_entry)
    
    # Add aggregate metrics
    output = {
        "aggregate_metrics": data.get("aggregate_metrics", {}),
        "total_emails": data.get("total_emails", 0),
        "valid_results": data.get("valid_results", 0),
        "results": formatted_results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Formatted results saved to: {output_file}")
    print(f"   Total entries: {len(formatted_results)}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Format evaluation results')
    parser.add_argument('--input', type=str, help='Input results file path')
    parser.add_argument('--output', type=str, help='Output formatted file path')
    args = parser.parse_args()
    
    if args.input and args.output:
        # Use provided paths
        input_file = args.input
        output_file = args.output
    else:
        # Find the most recent results file
        results_dir = Path("eval/results")
        result_files = sorted(results_dir.glob("results_*.json"), reverse=True)
        
        if not result_files:
            print("❌ No results files found!")
            sys.exit(1)
        
        input_file = str(result_files[0])
        output_file = str(results_dir / "formatted_evaluation_results.json")
    
    print(f"📊 Processing: {input_file}")
    format_results(input_file, output_file)

