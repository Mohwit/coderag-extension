"""Search function for retrieval agent."""
from codeact_retrieval.repository_singleton import get_repository

def code_search(query: str, top_k: int = 5) -> list:
    """Search for code related to the query and returns a list of result dictionaries."""
    # Get the singleton repository instance
    repository = get_repository()
    # Search for code
    results = repository.search(query, top_k=top_k)
   
    return results