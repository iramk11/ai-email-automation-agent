# AI Automation Agent

An intelligent email automation system that uses Retrieval-Augmented Generation (RAG) and GraphRAG to provide personalized email responses based on historical email patterns and replies.

## Features

- **Personalized Email Responses**: Uses your historical email replies to generate contextually appropriate responses
- **Intent Classification**: Automatically categorizes incoming emails (follow-ups, interview schedules, acceptances, rejections, etc.)
- **Vector Search**: Employs semantic search to find the most relevant historical responses
- **Graph-based Relationships**: Uses Neo4j to model and query relationships between entities in emails
- **Hybrid Retrieval**: Combines vector similarity search with graph-based relationship queries
- **Local LLM Integration**: Uses Ollama for local language model inference
- **Qdrant Vector Database**: Efficient storage and retrieval of email embeddings
- **Neo4j Graph Database**: Persistent storage of knowledge graphs and entity relationships

## How It Works

### Basic RAG (rag.py)
1. **Data Ingestion**: Historical email-reply pairs are embedded using SentenceTransformers
2. **Vector Storage**: Embeddings are stored in Qdrant for fast similarity search
3. **Query Processing**: Incoming emails are embedded and matched against historical data
4. **Response Generation**: The system retrieves relevant examples and generates personalized replies using a local LLM

### Advanced GraphRAG (graphrag.py)
1. **Data Ingestion**: Historical email-reply pairs are processed and embedded
2. **Graph Construction**: Entities and relationships are extracted and stored in Neo4j
3. **Vector Storage**: Embeddings are stored in Qdrant for semantic similarity
4. **Hybrid Retrieval**: Combines vector search with graph-based relationship queries
5. **Enhanced Context**: Uses both semantic similarity and entity relationships for richer context
6. **Response Generation**: Generates more contextually aware responses using the hybrid approach

## Dataset

The system includes a dataset of 31 email-reply pairs covering various scenarios:
- Job application follow-ups
- Interview scheduling
- Acceptance and rejection notifications
- Application status updates

## Prerequisites

- Python 3.8+ (recommended: Python 3.9 or 3.10)
- Docker (for Qdrant and Neo4j)
- Qdrant vector database (running on localhost:6333)
- Neo4j graph database (running on localhost:7687) - for GraphRAG
- Ollama with a language model (e.g., llama3)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/iramk11/ai-automation-agent.git
cd ai-automation-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start Qdrant:
```bash
docker run -p 6333:6333 qdrant/qdrant
```

4. Pull an Ollama model:
```bash
ollama pull llama3
```

## Usage

### Quick Setup
See [SETUP.md](SETUP.md) for detailed installation instructions.

### Basic RAG
1. Load and ingest the dataset:
```bash
python rag.py
```

This will:
- Create a Qdrant collection
- Embed and store all email-reply pairs
- Demonstrate the system with a sample query

### Advanced GraphRAG
1. Ensure Neo4j is running (see SETUP.md)
2. Run the GraphRAG implementation:
```bash
python graphrag.py
```

This will:
- Create a knowledge graph in Neo4j
- Build vector embeddings in Qdrant
- Demonstrate hybrid retrieval with both vector and graph search
- Generate contextually enhanced responses

Both systems will automatically:
- Retrieve similar historical emails
- Generate a personalized response
- Display the results

## Example Output

```
--- Retrieved Context ---
- follow_up: Follow Up - TechSphere (0.823)
- follow_up: Follow Up - DataSense (0.789)
- interview_schedule: Interview Schedule - TechSphere (0.745)

--- Generated Personalized Reply ---
Hi there,

Yes, absolutely! I remain very interested in the opportunity and am happy to provide any additional information if needed.

Thanks,
Ali
```

## Architecture

```
Incoming Email → Embedding → Vector Search → Retrieved Examples → LLM Generation → Personalized Reply
```

## Dependencies

- `qdrant-client`: Vector database client
- `sentence-transformers`: Text embeddings
- `tqdm`: Progress bars
- `ollama`: Local LLM integration (via subprocess)

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the [MIT License](LICENSE).
