#!/usr/bin/env python3
"""
Dry test script for interchangeable artifacts and intents.
Tests the hit rate calculation without LLM calls.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from eval.utils import calculate_artifact_hit_rate, calculate_intent_hit_rate

def test_artifact_interchangeable():
    """Test artifact interchangeable logic."""
    print("="*70)
    print("TESTING ARTIFACT INTERCHANGEABLE LOGIC")
    print("="*70)
    
    test_cases = [
        {
            "name": "zoom_link <-> calendly (predicted zoom, truth calendly)",
            "predicted": ["zoom_link"],
            "ground_truth": ["calendly"],
            "expected_hit": True
        },
        {
            "name": "zoom_link <-> calendly (predicted calendly, truth zoom)",
            "predicted": ["calendly"],
            "ground_truth": ["zoom_link"],
            "expected_hit": True
        },
        {
            "name": "report <-> draft (predicted report, truth draft)",
            "predicted": ["report"],
            "ground_truth": ["draft"],
            "expected_hit": True
        },
        {
            "name": "report <-> draft (predicted draft, truth report)",
            "predicted": ["draft"],
            "ground_truth": ["report"],
            "expected_hit": True
        },
        {
            "name": "Multiple artifacts with interchangeables",
            "predicted": ["zoom_link", "ds_resume"],
            "ground_truth": ["calendly", "ds_resume"],
            "expected_hit": True
        },
        {
            "name": "Multiple interchangeables",
            "predicted": ["zoom_link", "report"],
            "ground_truth": ["calendly", "draft"],
            "expected_hit": True
        },
        {
            "name": "No match (different artifacts)",
            "predicted": ["zoom_link"],
            "ground_truth": ["ds_resume"],
            "expected_hit": False
        },
        {
            "name": "Exact match",
            "predicted": ["calendly", "ds_resume"],
            "ground_truth": ["calendly", "ds_resume"],
            "expected_hit": True
        },
        {
            "name": "Partial match with interchangeable",
            "predicted": ["zoom_link", "github"],
            "ground_truth": ["calendly", "linkedin_profile"],
            "expected_hit": True  # calendly matches (zoom_link), so partial hit (F1 > 0)
        },
        {
            "name": "Empty predicted",
            "predicted": [],
            "ground_truth": ["calendly"],
            "expected_hit": False
        },
        {
            "name": "Empty ground truth",
            "predicted": ["calendly"],
            "ground_truth": [],
            "expected_hit": False
        },
        {
            "name": "Both empty",
            "predicted": [],
            "ground_truth": [],
            "expected_hit": True
        }
    ]
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        result = calculate_artifact_hit_rate(test["predicted"], test["ground_truth"])
        is_hit = result["f1"] > 0.0 or (result["precision"] == 1.0 and result["recall"] == 1.0)
        
        status = "✅ PASS" if is_hit == test["expected_hit"] else "❌ FAIL"
        if is_hit == test["expected_hit"]:
            passed += 1
        else:
            failed += 1
        
        print(f"\n{status}: {test['name']}")
        print(f"   Predicted: {test['predicted']}")
        print(f"   Ground Truth: {test['ground_truth']}")
        print(f"   Expected Hit: {test['expected_hit']}, Got Hit: {is_hit}")
        print(f"   Metrics: F1={result['f1']:.3f}, P={result['precision']:.3f}, R={result['recall']:.3f}")
    
    print("\n" + "="*70)
    print(f"Artifact Tests: {passed} passed, {failed} failed")
    print("="*70)
    return passed, failed


def test_intent_interchangeable():
    """Test intent interchangeable logic."""
    print("\n" + "="*70)
    print("TESTING INTENT INTERCHANGEABLE LOGIC")
    print("="*70)
    
    test_cases = [
        {
            "name": "reschedule <-> schedule (predicted reschedule, truth schedule)",
            "predicted": ["reschedule"],
            "ground_truth": ["schedule"],
            "expected_hit": True
        },
        {
            "name": "reschedule <-> schedule (predicted schedule, truth reschedule)",
            "predicted": ["schedule"],
            "ground_truth": ["reschedule"],
            "expected_hit": True
        },
        {
            "name": "Multiple intents with interchangeable",
            "predicted": ["reschedule", "request_feedback"],
            "ground_truth": ["schedule", "request_feedback"],
            "expected_hit": True
        },
        {
            "name": "No match (different intents)",
            "predicted": ["reschedule"],
            "ground_truth": ["send_materials"],
            "expected_hit": False
        },
        {
            "name": "Exact match",
            "predicted": ["schedule", "request_feedback"],
            "ground_truth": ["schedule", "request_feedback"],
            "expected_hit": True
        },
        {
            "name": "Partial match with interchangeable",
            "predicted": ["reschedule", "send_materials"],
            "ground_truth": ["schedule", "request_feedback"],
            "expected_hit": True  # schedule matches (reschedule), so partial hit (F1 > 0)
        },
        {
            "name": "Empty predicted",
            "predicted": [],
            "ground_truth": ["schedule"],
            "expected_hit": False
        },
        {
            "name": "Empty ground truth",
            "predicted": ["schedule"],
            "ground_truth": [],
            "expected_hit": False
        },
        {
            "name": "Both empty",
            "predicted": [],
            "ground_truth": [],
            "expected_hit": True
        }
    ]
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        result = calculate_intent_hit_rate(test["predicted"], test["ground_truth"])
        is_hit = result["f1"] > 0.0 or (result["precision"] == 1.0 and result["recall"] == 1.0)
        
        status = "✅ PASS" if is_hit == test["expected_hit"] else "❌ FAIL"
        if is_hit == test["expected_hit"]:
            passed += 1
        else:
            failed += 1
        
        print(f"\n{status}: {test['name']}")
        print(f"   Predicted: {test['predicted']}")
        print(f"   Ground Truth: {test['ground_truth']}")
        print(f"   Expected Hit: {test['expected_hit']}, Got Hit: {is_hit}")
        print(f"   Metrics: F1={result['f1']:.3f}, P={result['precision']:.3f}, R={result['recall']:.3f}")
    
    print("\n" + "="*70)
    print(f"Intent Tests: {passed} passed, {failed} failed")
    print("="*70)
    return passed, failed


def test_complex_cases():
    """Test complex cases with multiple elements."""
    print("\n" + "="*70)
    print("TESTING COMPLEX CASES")
    print("="*70)
    
    test_cases = [
        {
            "name": "Multiple artifacts: zoom+report vs calendly+draft",
            "predicted": ["zoom_link", "report"],
            "ground_truth": ["calendly", "draft"],
            "expected_f1": 1.0
        },
        {
            "name": "Multiple artifacts: zoom+ds_resume vs calendly+ds_resume",
            "predicted": ["zoom_link", "ds_resume"],
            "ground_truth": ["calendly", "ds_resume"],
            "expected_f1": 1.0
        },
        {
            "name": "Multiple intents: reschedule+request_feedback vs schedule+request_feedback",
            "predicted": ["reschedule", "request_feedback"],
            "ground_truth": ["schedule", "request_feedback"],
            "expected_f1": 1.0
        },
        {
            "name": "Mixed: some match, some don't",
            "predicted": ["zoom_link", "github"],
            "ground_truth": ["calendly", "linkedin_profile"],
            "expected_f1": 0.5  # calendly matches, but github != linkedin_profile
        }
    ]
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        if "zoom_link" in test["predicted"] or "calendly" in test["predicted"]:
            result = calculate_artifact_hit_rate(test["predicted"], test["ground_truth"])
        else:
            result = calculate_intent_hit_rate(test["predicted"], test["ground_truth"])
        
        f1_match = abs(result["f1"] - test["expected_f1"]) < 0.01
        
        status = "✅ PASS" if f1_match else "❌ FAIL"
        if f1_match:
            passed += 1
        else:
            failed += 1
        
        print(f"\n{status}: {test['name']}")
        print(f"   Predicted: {test['predicted']}")
        print(f"   Ground Truth: {test['ground_truth']}")
        print(f"   Expected F1: {test['expected_f1']:.3f}, Got F1: {result['f1']:.3f}")
        print(f"   Metrics: P={result['precision']:.3f}, R={result['recall']:.3f}")
    
    print("\n" + "="*70)
    print(f"Complex Tests: {passed} passed, {failed} failed")
    print("="*70)
    return passed, failed


if __name__ == "__main__":
    print("\n" + "="*70)
    print("DRY TEST: INTERCHANGEABLE ARTIFACTS AND INTENTS")
    print("="*70)
    
    art_passed, art_failed = test_artifact_interchangeable()
    intent_passed, intent_failed = test_intent_interchangeable()
    complex_passed, complex_failed = test_complex_cases()
    
    total_passed = art_passed + intent_passed + complex_passed
    total_failed = art_failed + intent_failed + complex_failed
    
    print("\n" + "="*70)
    print("OVERALL SUMMARY")
    print("="*70)
    print(f"Total: {total_passed} passed, {total_failed} failed")
    
    if total_failed == 0:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)

