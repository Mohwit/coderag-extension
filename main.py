import os
import sys
from dotenv import load_dotenv
from codeact_retrieval.agent import Agent
from codeact_retrieval.functions import FUNCTIONS
from codeact_retrieval.tools.tools_schema import TOOLS_SCHEMA
from codeact_retrieval.utils.prompts import system_prompt
from codeact_retrieval.utils.persistent_kernel import PersistentKernel


def initialize_agent():
    """Initialize the CodeAct agent with configuration."""
    load_dotenv()
    ## api key for anthropic
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not found in environment variables.")
        print("Please set your API key in a .env file or environment variable.")
        sys.exit(1)

    ## return agent with anthropic model
    return Agent(
        model="claude-4-sonnet-20250514",
        api_key=api_key,
        system_prompt=system_prompt,
        base_url="https://api.anthropic.com/v1",
        tools=TOOLS_SCHEMA,
        kernel=PersistentKernel(namespace=FUNCTIONS, imports=""),
    )
    
if __name__ == "__main__":
    from coderag import Repository, ChromaDBStore
    from codeact_retrieval.repository_singleton import RepositorySingleton

    # Initialize vector store
    vector_store = ChromaDBStore(
        collection_name="my_repo",
        persist_directory="./vector_db"
    )

    # Initialize repository handler
    repo = Repository(
        repo_path="/Users/msingh/Desktop/coderag-extension",
        vector_store=vector_store,
        use_code_summaries=True  # Optional: use AI summaries for better embeddings
    )
    
    # repo.index()
    
    # Initialize the singleton with the repository instance
    RepositorySingleton().initialize(repo)
    
    agent = initialize_agent()
    while True:
        user_prompt = input("Enter your prompt: ")
        if user_prompt == "exit":
            break
        
        print("\nProcessing your query...\n")
        
        response = agent.query(user_prompt)
        
        # Display the final output
        print("\n" + "=" * 50)
        print("FINAL OUTPUT:")
        print("=" * 50)
        if response.get("content"):
            print(response.get("content"))
        print("=" * 50 + "\n")
        