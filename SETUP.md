# Setup Guide for AI Automation Agent

This guide will help you set up the environment for running the AI automation agent with GraphRAG capabilities.

## Prerequisites

- Python 3.8+ (recommended: Python 3.9 or 3.10)
- Docker (for Qdrant and Neo4j)
- Ollama (for local LLM)

## Environment Setup

### Option 1: Using Conda (Recommended)

```bash
# Create a new conda environment
conda create -n ai-automation python=3.10
conda activate ai-automation

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Using Virtual Environment

```bash
# Create virtual environment
python -m venv ai-automation-env

# Activate environment
# On macOS/Linux:
source ai-automation-env/bin/activate
# On Windows:
# ai-automation-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## External Services Setup

### 1. Qdrant Vector Database

```bash
# Start Qdrant using Docker
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

Verify it's running: http://localhost:6333/dashboard

### 2. Neo4j Graph Database

```bash
# Start Neo4j using Docker
docker run \
    --name neo4j \
    -p 7474:7474 -p 7687:7687 \
    -d \
    -v $HOME/neo4j/data:/data \
    -v $HOME/neo4j/logs:/logs \
    -v $HOME/neo4j/import:/var/lib/neo4j/import \
    -v $HOME/neo4j/plugins:/plugins \
    --env NEO4J_AUTH=neo4j/test1234 \
    neo4j:latest
```

Access Neo4j Browser: http://localhost:7474
- Username: `neo4j`
- Password: `test1234`

### 3. Ollama (Local LLM)

```bash
# Install Ollama (macOS)
brew install ollama

# Start Ollama service
ollama serve

# Pull the required model (in another terminal)
ollama pull llama3
```

## Running the Applications

### Basic RAG (rag.py)
```bash
python rag.py
```

### Advanced GraphRAG (graphrag.py)
```bash
python graphrag.py
```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Make sure you're in the correct environment and all dependencies are installed.

2. **Connection refused to Qdrant**: Ensure Qdrant is running on port 6333.

3. **Neo4j connection failed**: Verify Neo4j is running and credentials are correct.

4. **Ollama model not found**: Make sure you've pulled the llama3 model with `ollama pull llama3`.

### Environment Variables

You can customize the connection settings by setting these environment variables:

```bash
export QDRANT_HOST=localhost
export QDRANT_PORT=6333
export NEO4J_URL=bolt://localhost:7687
export NEO4J_USERNAME=neo4j
export NEO4J_PASSWORD=test1234
```

## Development

### Adding New Dependencies

1. Install the new package in your environment
2. Update `requirements.txt` with the new dependency
3. Test the installation with a fresh environment

### Code Structure

- `rag.py`: Basic RAG implementation with Qdrant
- `graphrag.py`: Advanced GraphRAG with Neo4j + Qdrant
- `emails_dataset_with_replies.jsonl`: Sample email dataset
- `requirements.txt`: Python dependencies
- `README.md`: Project documentation
- `SETUP.md`: This setup guide
