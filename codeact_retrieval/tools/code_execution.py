"""
Code execution tool for CodeAct framework.
"""

from codeact_retrieval.utils.persistent_kernel import PersistentKernel


def code_execution(code: str, kernel: PersistentKernel) -> str:
    """Execute the given code and return the result."""
    ## execute the code
    result = kernel.execute(code)
    return result["output"] if result["success"] else f"Error: {result['error']}"
