#!/usr/bin/env python3
"""
Quick validation script to check if evaluation setup is correct.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_imports():
    """Check if all required imports work."""
    print("Checking imports...")
    try:
        from eval.evaluator import EmailEvaluator
        print("✅ Evaluator import successful")
    except Exception as e:
        print(f"❌ Evaluator import failed: {e}")
        return False
    
    try:
        from eval.metrics import MetricsCalculator
        print("✅ Metrics calculator import successful")
    except Exception as e:
        print(f"❌ Metrics calculator import failed: {e}")
        return False
    
    try:
        from eval.utils import load_golden_dataset
        print("✅ Utils import successful")
    except Exception as e:
        print(f"❌ Utils import failed: {e}")
        return False
    
    return True

def check_dependencies():
    """Check if optional dependencies are available."""
    print("\nChecking optional dependencies...")
    
    try:
        from rouge_score import rouge_scorer
        print("✅ rouge-score available")
    except ImportError:
        print("⚠️  rouge-score not available (install: pip install rouge-score)")
    
    try:
        import mauve
        print("✅ mauve-text available")
    except ImportError:
        print("⚠️  mauve-text not available (install: pip install mauve-text)")
    
    try:
        from sentence_transformers import SentenceTransformer
        print("✅ sentence-transformers available")
    except ImportError:
        print("⚠️  sentence-transformers not available (install: pip install sentence-transformers)")

def check_dataset():
    """Check if golden dataset exists."""
    print("\nChecking dataset...")
    dataset_path = Path(__file__).parent.parent / "data" / "golden_dataset_benchmark.json"
    if dataset_path.exists():
        print(f"✅ Dataset found: {dataset_path}")
        try:
            import json
            with open(dataset_path, 'r') as f:
                data = json.load(f)
            print(f"✅ Dataset valid JSON with {len(data)} entries")
            return True
        except Exception as e:
            print(f"❌ Dataset invalid: {e}")
            return False
    else:
        print(f"❌ Dataset not found: {dataset_path}")
        return False

def check_backend_services():
    """Check if backend services can be imported."""
    print("\nChecking backend services...")
    try:
        from backend.services.ollama_service import OllamaService
        print("✅ OllamaService import successful")
    except Exception as e:
        print(f"❌ OllamaService import failed: {e}")
        return False
    
    try:
        import ollama
        # Try a simple health check
        try:
            response = ollama.list()
            print("✅ Ollama service accessible")
        except Exception as e:
            print(f"⚠️  Ollama service not accessible: {e}")
            print("   Make sure Ollama is running: ollama serve")
    except ImportError:
        print("⚠️  ollama package not available")
    
    return True

if __name__ == "__main__":
    print("="*70)
    print("EVALUATION SETUP VALIDATION")
    print("="*70)
    
    all_ok = True
    all_ok &= check_imports()
    check_dependencies()
    all_ok &= check_dataset()
    all_ok &= check_backend_services()
    
    print("\n" + "="*70)
    if all_ok:
        print("✅ Setup validation complete! Ready to run evaluation.")
    else:
        print("⚠️  Some issues found. Please fix them before running evaluation.")
    print("="*70)

