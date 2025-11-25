#!/bin/bash
# Script to start the Graph RAG Email Assistant backend

echo "🚀 Starting Graph RAG Email Assistant Backend..."
echo ""

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Conda not found. Please install Miniconda or Anaconda."
    exit 1
fi

# Check if environment exists
if ! conda env list | grep -q "graph_rag"; then
    echo "📦 Creating conda environment 'graph_rag'..."
    conda create -n graph_rag python=3.10 -y
fi

# Activate environment
echo "🔧 Activating environment..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate graph_rag

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
if [ ! -d "qdrant_data" ]; then
    echo "⚠️  Warning: qdrant_data directory not found."
    echo "   Please run your notebook first to generate the knowledge base."
    echo ""
fi

# Start the server
echo "✅ Starting FastAPI server..."
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo "   Health: http://localhost:8000/api/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo "─────────────────────────────────────────────────"

python -m backend.main

