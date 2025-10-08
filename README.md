# CodeAct Retrieval Agent

An intelligent code retrieval system that uses AI-powered agents to search and analyze codebases. The agent uses parallel search strategies with deduplication to efficiently retrieve relevant code chunks and provides structured JSON responses with explanations and source references.

## Features

- 🤖 **AI-Powered Code Search**: Uses Claude (Anthropic) with tool calling for intelligent code retrieval
- 🔍 **Parallel Search**: Executes multiple search queries simultaneously for comprehensive results
- 📊 **Vector Database**: Leverages ChromaDB for efficient semantic code search
- 🧠 **Code Summaries**: Optional AI-generated summaries for better embeddings
- 🔄 **Persistent Kernel**: Maintains state across code executions
- 🎯 **Deduplication**: Automatically filters duplicate chunks from search results
- 📝 **Structured JSON Output**: Returns results with explanations and complete metadata
- 🏗️ **Hierarchical Code Understanding**: Tracks classes, methods, and their relationships

## Installation

### Prerequisites

- Python 3.8+
- Anthropic API key

### Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd coderag-extension
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file and add your Anthropic API key:

```bash
ANTHROPIC_API_KEY=your_api_key_here
```

## Quick Start

### Basic Usage

Run the interactive agent:

```bash
python main.py
```

Then enter your queries:

```
Enter your prompt: How does the Agent class handle tool calls?
```

### Programmatic Usage

```python
from coderag import Repository, ChromaDBStore
from codeact_retrieval.agent import Agent
from codeact_retrieval.repository_singleton import RepositorySingleton
from codeact_retrieval.tools.tools_schema import TOOLS_SCHEMA
from codeact_retrieval.utils.prompts import system_prompt
from codeact_retrieval.utils.persistent_kernel import PersistentKernel
from codeact_retrieval.functions import FUNCTIONS

# Initialize vector store
vector_store = ChromaDBStore(
    collection_name="my_repo",
    persist_directory="./vector_db"
)

# Initialize repository
repo = Repository(
    repo_path="/path/to/your/codebase",
    vector_store=vector_store,
    use_code_summaries=True
)

# Index the repository (first time only)
repo.index()

# Initialize singleton
RepositorySingleton().initialize(repo)

# Create agent
agent = Agent(
    model="claude-4-sonnet-20250514",
    api_key="your_api_key",
    system_prompt=system_prompt,
    tools=TOOLS_SCHEMA,
    kernel=PersistentKernel(namespace=FUNCTIONS, imports="")
)

# Query the agent
response = agent.query("Find all error handling functions")
print(response.get("content"))
```

## Output Format

The agent returns results in a structured JSON format:

```json
{
  "Explanation": "A detailed explanation addressing your query, including insights about the code and how it relates to your question",
  "Source": [
    {
      "content": "The actual code chunk content",
      "metadata": {
        "file_path": "path/to/file.py",
        "line_start": 10,
        "line_end": 50,
        "chunk_id": "unique_identifier",
        "type": "class|method|function",
        "parent": "parent_context",
        "children": ["child_methods"],
        "summary": "AI-generated summary (if enabled)"
      }
    }
  ]
}
```

### Output Fields

- **Explanation**: Contextual explanation of the retrieved code and how it answers your query
- **Source**: Array of relevant code chunks with:
  - `content`: The actual source code
  - `metadata`: Complete metadata including:
    - `file_path`: Full path to the source file
    - `line_start`: Starting line number of the chunk
    - `line_end`: Ending line number of the chunk
    - `chunk_id`: Unique identifier for the chunk
    - `type`: Type of code element (class, method, function, etc.)
    - `parent`: Parent context (e.g., class name for methods)
    - `children`: List of child elements (e.g., methods in a class)
    - `summary`: AI-generated summary (if enabled)

## Architecture

### Project Structure

```
coderag-extension/
├── codeact_retrieval/
│   ├── agent.py                 # Main Agent class
│   ├── functions/
│   │   ├── __init__.py         # Function registry
│   │   └── search.py           # Code search function
│   ├── repository_singleton.py # Repository singleton pattern
│   ├── tools/
│   │   ├── code_execution.py   # Code execution tool
│   │   └── tools_schema.py     # Tool definitions
│   └── utils/
│       ├── persistent_kernel.py # Jupyter kernel wrapper
│       └── prompts.py          # System prompts
├── vector_db/                  # ChromaDB storage
├── main.py                     # Main entry point
├── example.py                  # Usage example
└── requirements.txt            # Dependencies
```

### Key Components

#### Agent (`codeact_retrieval/agent.py`)

The core AI agent that:

- Manages conversation state
- Executes tool calls (code execution)
- Handles LLM interactions
- Processes responses in a loop until completion

#### Code Search (`codeact_retrieval/functions/search.py`)

Semantic search function that:

- Queries the vector database
- Returns ranked code chunks
- Integrates with the repository singleton

#### Persistent Kernel (`codeact_retrieval/utils/persistent_kernel.py`)

Jupyter kernel wrapper that:

- Maintains state between code executions
- Executes Python code safely
- Supports interactive development

#### Repository Singleton (`codeact_retrieval/repository_singleton.py`)

Singleton pattern ensuring:

- Single repository instance
- Global access to search functionality
- Thread-safe operations

## Configuration

### Agent Configuration

```python
Agent(
    model="claude-4-sonnet-20250514",  # Model name
    api_key="your_key",                # API key
    system_prompt=system_prompt,       # System instructions
    base_url="https://api.anthropic.com/v1",
    temperature=0.0,                   # Response randomness
    max_tokens=8096,                   # Max response length
    tools=TOOLS_SCHEMA,                # Available tools
    kernel=PersistentKernel(...)       # Code execution kernel
)
```

### Repository Configuration

```python
Repository(
    repo_path="/path/to/code",         # Codebase path
    vector_store=vector_store,         # Vector DB instance
    use_code_summaries=True,           # Enable AI summaries
)
```

## Search Strategy

The agent implements an efficient parallel search strategy:

1. **Parallel Queries**: Generates multiple related queries and executes them simultaneously
2. **Result Collection**: Aggregates results from all queries
3. **Deduplication**: Removes duplicate chunks based on file path and content hash
4. **Analysis**: Analyzes unique results to answer the query
5. **Structured Response**: Returns JSON with explanation and sources

Example from system prompt:

```python
queries = [
    "function to handle HTTP requests",
    "HTTP request handler implementation",
    "API endpoint handlers"
]

with ThreadPoolExecutor(max_workers=len(queries)) as executor:
    future_to_query = {
        executor.submit(code_search, query, 5): query
        for query in queries
    }
    # Collect and deduplicate results...
```

## Advanced Usage

### Custom Search

```python
from codeact_retrieval.functions.search import code_search

# Direct search
results = code_search("authentication logic", top_k=10)

for result in results:
    print(f"File: {result['metadata']['file_path']}")
    print(f"Score: {result['score']}")
    print(f"Code: {result['metadata']['content']}")
```

### Using with Different Models

The agent supports any LiteLLM-compatible model:

```python
# Using OpenAI
agent = Agent(
    model="gpt-4",
    api_key="openai_key",
    # ... other params
)

# Using local models
agent = Agent(
    model="ollama/codellama",
    api_key="not-needed",
    base_url="http://localhost:11434",
    # ... other params
)
```

## Environment Variables

Create a `.env` file with:

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...

# Optional
OPENAI_API_KEY=sk-...          # If using OpenAI models
LOG_LEVEL=INFO                  # Logging verbosity
```

## Examples

See `example.py` for a basic search example without the agent:

```bash
python example.py
```

## Troubleshooting

### Repository Not Initialized Error

```python
RuntimeError: Repository not initialized. Call initialize() first.
```

**Solution**: Ensure you initialize the singleton before querying:

```python
RepositorySingleton().initialize(repo)
```

### ChromaDB Persistence Issues

If you encounter database locks or corruption:

```bash
rm -rf vector_db/
# Then re-index your repository
```

### API Rate Limits

If you hit rate limits, adjust the search parameters:

```python
# Reduce top_k to fetch fewer results
code_search(query, top_k=3)
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [CodeRAG](https://github.com/Mohwit/coderag) for vector-based code retrieval
- Powered by [Claude](https://anthropic.com) from Anthropic
- Uses [LiteLLM](https://github.com/BerriAI/litellm) for model flexibility
- Vector storage with [ChromaDB](https://www.trychroma.com/)

## Support

For issues, questions, or contributions, please open an issue on the GitHub repository.
