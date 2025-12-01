#!/bin/bash
# Script to start the Graph RAG Email Assistant backend

echo "🚀 Starting Graph RAG Email Assistant Backend..."
echo ""

# Check if virtual environment exists, if not create it
if [ ! -d "email-agent" ]; then
    echo "📦 Creating virtual environment 'email-agent'..."
    python3 -m venv email-agent
fi

# Activate environment
echo "🔧 Activating environment..."
source email-agent/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r backend/requirements.txt --quiet

# Check if Ollama is running
echo "🔍 Checking Ollama..."
if ! curl -s http://localhost:11434 > /dev/null 2>&1; then
    echo "⚠️  Warning: Ollama doesn't seem to be running."
    echo "   Please start Ollama in another terminal: ollama serve"
    echo "   Then pull the model: ollama pull llama3"
    echo ""
fi

# Check if Qdrant data exists
if [ ! -d "graphrag_local/qdrant_data" ]; then
    echo "⚠️  Warning: graphrag_local/qdrant_data directory not found."
    echo "   Please run your notebook first to generate the knowledge base."
    echo ""
fi

# Check if Qdrant is locked (notebook might be running)
if [ -f "graphrag_local/qdrant_data/.lock" ]; then
    echo "⚠️  Warning: Qdrant database appears to be locked."
    echo "   Please close the Jupyter notebook first, or remove the lock file:"
    echo "   rm -f graphrag_local/qdrant_data/.lock"
    echo ""
fi

# Start the server
echo "✅ Starting FastAPI server..."
echo "   API: http://localhost:8001"
echo "   Docs: http://localhost:8001/docs"
echo "   Health: http://localhost:8001/api/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo "─────────────────────────────────────────────────"

# Run from project root using uvicorn
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload

