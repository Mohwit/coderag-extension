"""Tools schema for Code generation."""

from codeact_retrieval.tools.code_execution import code_execution

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "code_execution",
            "description": "Execute Python code in a persistent kernel. \
            The kernel maintains state between executions. \
            Supports web servers - when code contains serve() calls, \
            the server will be started in the background and accessible via browser.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python code to execute"}
                },
                "required": ["code"],
            },
            "callable": code_execution,
        },
    }
]
