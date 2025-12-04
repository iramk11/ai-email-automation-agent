"""
Utility functions for evaluation pipeline.
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def load_golden_dataset(dataset_path: str) -> List[Dict[str, Any]]:
    """
    Load the golden benchmark dataset.
    
    Args:
        dataset_path: Path to the golden dataset JSON file
        
    Returns:
        List of email entries with labels
    """
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    logger.info(f"Loaded {len(data)} entries from golden dataset")
    return data


def save_results(results: Dict[str, Any], output_path: str):
    """
    Save evaluation results to JSON file.
    
    Args:
        results: Dictionary containing evaluation results
        output_path: Path to save results
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Results saved to {output_path}")


def _normalize_interchangeable(items: List[str], interchangeable_map: Dict[str, str]) -> set:
    """
    Normalize items by replacing interchangeable ones with a canonical form.
    
    Args:
        items: List of items to normalize
        interchangeable_map: Dict mapping item -> canonical form
        
    Returns:
        Set of normalized items
    """
    normalized = set()
    for item in items:
        # Check if this item has an interchangeable equivalent
        if item in interchangeable_map:
            # Use the canonical form (the one that appears first in the mapping)
            normalized.add(interchangeable_map[item])
        else:
            normalized.add(item)
    return normalized


def calculate_artifact_hit_rate(predicted: List[str], ground_truth: List[str]) -> Dict[str, float]:
    """
    Calculate artifact hit rate metrics with interchangeable artifacts support.
    
    Interchangeable artifacts:
    - zoom_link <-> calendly
    - report <-> draft
    
    Args:
        predicted: List of predicted artifacts
        ground_truth: List of ground truth artifacts
        
    Returns:
        Dictionary with precision, recall, F1, and exact match
    """
    # Define interchangeable artifacts (map to canonical form)
    # Using the first one as canonical
    artifact_interchangeable = {
        "zoom_link": "calendly",  # zoom_link -> calendly (canonical)
        "calendly": "calendly",   # calendly -> calendly (canonical)
        "report": "draft",        # report -> draft (canonical)
        "draft": "draft"          # draft -> draft (canonical)
    }
    
    # Normalize both sets
    predicted_normalized = _normalize_interchangeable(predicted, artifact_interchangeable)
    ground_truth_normalized = _normalize_interchangeable(ground_truth, artifact_interchangeable)
    
    if len(ground_truth_normalized) == 0:
        # If no artifacts expected, check if we predicted none
        if len(predicted_normalized) == 0:
            return {"precision": 1.0, "recall": 1.0, "f1": 1.0, "exact_match": 1.0}
        else:
            return {"precision": 0.0, "recall": 1.0, "f1": 0.0, "exact_match": 0.0}
    
    if len(predicted_normalized) == 0:
        return {"precision": 1.0, "recall": 0.0, "f1": 0.0, "exact_match": 0.0}
    
    # Calculate metrics using normalized sets
    true_positives = len(predicted_normalized & ground_truth_normalized)
    false_positives = len(predicted_normalized - ground_truth_normalized)
    false_negatives = len(ground_truth_normalized - predicted_normalized)
    
    precision = true_positives / len(predicted_normalized) if len(predicted_normalized) > 0 else 0.0
    recall = true_positives / len(ground_truth_normalized) if len(ground_truth_normalized) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    exact_match = 1.0 if predicted_normalized == ground_truth_normalized else 0.0
    
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "exact_match": exact_match,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives
    }


def calculate_intent_hit_rate(predicted: List[str], ground_truth: List[str]) -> Dict[str, float]:
    """
    Calculate intent hit rate metrics with interchangeable intents support.
    
    Interchangeable intents:
    - reschedule <-> schedule
    
    Args:
        predicted: List of predicted intents
        ground_truth: List of ground truth intents
        
    Returns:
        Dictionary with precision, recall, F1, and exact match
    """
    # Define interchangeable intents (map to canonical form)
    intent_interchangeable = {
        "reschedule": "schedule",  # reschedule -> schedule (canonical)
        "schedule": "schedule"     # schedule -> schedule (canonical)
    }
    
    # Normalize both sets
    predicted_normalized = _normalize_interchangeable(predicted, intent_interchangeable)
    ground_truth_normalized = _normalize_interchangeable(ground_truth, intent_interchangeable)
    
    if len(ground_truth_normalized) == 0:
        # If no intents expected, check if we predicted none
        if len(predicted_normalized) == 0:
            return {"precision": 1.0, "recall": 1.0, "f1": 1.0, "exact_match": 1.0}
        else:
            return {"precision": 0.0, "recall": 1.0, "f1": 0.0, "exact_match": 0.0}
    
    if len(predicted_normalized) == 0:
        return {"precision": 1.0, "recall": 0.0, "f1": 0.0, "exact_match": 0.0}
    
    # Calculate metrics using normalized sets
    true_positives = len(predicted_normalized & ground_truth_normalized)
    false_positives = len(predicted_normalized - ground_truth_normalized)
    false_negatives = len(ground_truth_normalized - predicted_normalized)
    
    precision = true_positives / len(predicted_normalized) if len(predicted_normalized) > 0 else 0.0
    recall = true_positives / len(ground_truth_normalized) if len(ground_truth_normalized) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    exact_match = 1.0 if predicted_normalized == ground_truth_normalized else 0.0
    
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "exact_match": exact_match,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives
    }

