"""
Test script for the Graph RAG Email Assistant backend.
Run this after starting the backend to verify everything works.
"""
import requests
import json
from colorama import init, Fore, Style
import sys

init(autoreset=True)

API_BASE_URL = "http://localhost:8000/api"

def print_header(text):
    """Print a formatted header."""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}{text:^60}")
    print(f"{Fore.CYAN}{'='*60}\n")

def print_success(text):
    """Print success message."""
    print(f"{Fore.GREEN}✅ {text}")

def print_error(text):
    """Print error message."""
    print(f"{Fore.RED}❌ {text}")

def print_warning(text):
    """Print warning message."""
    print(f"{Fore.YELLOW}⚠️  {text}")

def print_info(text):
    """Print info message."""
    print(f"{Fore.BLUE}ℹ️  {text}")

def test_health_check():
    """Test the health check endpoint."""
    print_header("Testing Health Check")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Health endpoint responding")
            print_info(f"Status: {data.get('status', 'unknown')}")
            
            services = data.get('services', {})
            for service, is_healthy in services.items():
                if is_healthy:
                    print_success(f"{service.capitalize()} service: healthy")
                else:
                    print_error(f"{service.capitalize()} service: unhealthy")
            
            return data.get('status') == 'healthy'
        else:
            print_error(f"Health check failed with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to backend. Is it running?")
        print_info("Start with: python -m backend.main")
        return False
    except Exception as e:
        print_error(f"Health check error: {e}")
        return False

def test_generate_reply():
    """Test the reply generation endpoint."""
    print_header("Testing Reply Generation")
    
    test_email = {
        "subject": "Meeting Request",
        "sender": "professor@university.edu",
        "body": "Hi, I hope you're doing well. Can we schedule a meeting to discuss your project progress?"
    }
    
    print_info("Sending test email:")
    print(f"  Subject: {test_email['subject']}")
    print(f"  Sender: {test_email['sender']}")
    print(f"  Body: {test_email['body'][:50]}...")
    
    try:
        print_info("\nGenerating reply... (this may take 10-30 seconds)")
        response = requests.post(
            f"{API_BASE_URL}/generate-reply",
            json=test_email,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print_success("Reply generated successfully!")
            print(f"\n{Fore.WHITE}{'─'*60}")
            print(f"{Fore.GREEN}Intent:{Style.RESET_ALL} {data.get('intent', 'unknown')}")
            print(f"{Fore.GREEN}Confidence:{Style.RESET_ALL} {data.get('confidence_score', 0):.2%}")
            print(f"{Fore.GREEN}Auto-send:{Style.RESET_ALL} {data.get('auto_send', False)}")
            print(f"\n{Fore.GREEN}Generated Draft:{Style.RESET_ALL}")
            print(f"{Fore.WHITE}{'─'*60}")
            print(data.get('draft_reply', 'No reply generated'))
            print(f"{Fore.WHITE}{'─'*60}\n")
            
            # Show context used
            context = data.get('context_used', {})
            faq_hits = context.get('faq_hits', [])
            graph_nodes = context.get('graph_nodes', [])
            
            print_info(f"Context: {len(faq_hits)} FAQ hits, {len(graph_nodes)} graph nodes")
            
            if faq_hits:
                print(f"\n{Fore.CYAN}Top FAQ Match:")
                top_faq = faq_hits[0]
                print(f"  Q: {top_faq.get('question', 'N/A')[:70]}...")
                print(f"  Score: {top_faq.get('score', 0):.3f}")
            
            return True
        else:
            print_error(f"Generation failed with status {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print_error("Request timed out. This might indicate:")
        print_warning("  - Ollama is not running (run: ollama serve)")
        print_warning("  - Llama3 model is not pulled (run: ollama pull llama3)")
        print_warning("  - Backend is processing slowly")
        return False
    except Exception as e:
        print_error(f"Generation error: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint."""
    print_header("Testing Root Endpoint")
    
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Root endpoint responding")
            print_info(f"API: {data.get('name', 'Unknown')}")
            print_info(f"Version: {data.get('version', 'Unknown')}")
            return True
        else:
            print_error(f"Root endpoint failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Root endpoint error: {e}")
        return False

def main():
    """Run all tests."""
    print(f"\n{Fore.MAGENTA}{'='*60}")
    print(f"{Fore.MAGENTA}Graph RAG Email Assistant - Backend Test Suite")
    print(f"{Fore.MAGENTA}{'='*60}\n")
    
    results = []
    
    # Test 1: Root endpoint
    results.append(("Root Endpoint", test_root_endpoint()))
    
    # Test 2: Health check
    results.append(("Health Check", test_health_check()))
    
    # Test 3: Reply generation (only if health check passed)
    if results[-1][1]:
        results.append(("Reply Generation", test_generate_reply()))
    else:
        print_warning("Skipping reply generation test (health check failed)")
        results.append(("Reply Generation", False))
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
    
    print(f"\n{Fore.WHITE}{'─'*60}")
    if passed == total:
        print(f"{Fore.GREEN}All tests passed! ({passed}/{total})")
        print(f"{Fore.GREEN}✨ Backend is working correctly!")
        return 0
    else:
        print(f"{Fore.YELLOW}Some tests failed ({passed}/{total})")
        print(f"{Fore.YELLOW}Check the errors above and troubleshoot.")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Tests interrupted by user.")
        sys.exit(1)

