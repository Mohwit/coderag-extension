"""CodeAct Agent class for CodeAct framework.

This class provides a CodeAct agent for the CodeAct framework.
It allows for the execution of code with persistent state.
"""

import json
from typing import Any, Dict, List, Optional, Union

from litellm import completion

from codeact_retrieval.utils.persistent_kernel import PersistentKernel


class Agent:
    """CodeAct Agent for retrieval."""

    def __init__(
        self,
        model: str,
        api_key: str,
        system_prompt: str,
        base_url: Optional[str] = None,
        temperature: float = 0.0,
        tools: Optional[Dict[str, Any]] = None,
        max_tokens: int = 8096,
        messages: Optional[
            List[Dict[str, Any]]
        ] = None,
        kernel: Optional[PersistentKernel] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the CodeAct Agent."""
        self.model = model
        self.api_key = api_key
        self.system_prompt = system_prompt
        self.base_url = base_url
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.tools = tools
        self.messages = messages if messages is not None else []
        self.kwargs = kwargs
        self.kernel = kernel
        ## Create a mapping of tool names to their callable functions
        self._tool_functions = {}
        for tool in self.tools:
            if tool.get("type") == "function":
                func_info = tool.get("function", {})
                name = func_info.get("name")
                callable_func = func_info.get("callable")
                if name and callable_func:
                    self._tool_functions[name] = callable_func

    ## Query the agent with the provided user prompt.
    ## Continues conversation until final response is received.
    def query(self, user_prompt: str) -> Dict[str, Any]:
        """
        Query the agent with the provided user prompt.
        Continues conversation until final response is received.
        """
        self._set_system_prompt(self.system_prompt)
        self.messages.append({"role": "user", "content": user_prompt})

        # Continue conversation loop until we get a final response
        while True:
            response = self._make_api_call()
            print("Response: ", response.get("content"))
            self.messages.append(response.choices[0].message.model_dump())

            # If there are tool calls, process them and continue
            if response.choices[0].message.tool_calls:
                self._process_tool_calls(response.choices[0].message.tool_calls)
                continue

            # If no tool calls, this is the final response
            return {
                "content": response.choices[0].message.content or "",
                "tool_calls": response.choices[0].message.tool_calls or None,
            }

    ## Process multiple tool calls and add their responses to messages.
    def _process_tool_calls(self, tool_calls: List[Any]) -> None:
        """
        Process multiple tool calls and add their responses to messages.
        """
        for tool_call in tool_calls:
            # Parse and display arguments
            try:
                args = json.loads(tool_call.function.arguments)
                # Print the code being executed instead of arguments
                if tool_call.function.name == "code_execution" and "code" in args:
                    print(f"\nExecuting Code:\n{args['code']}\n")
                else:
                    print(f"Arguments: {args}")
            except json.JSONDecodeError:
                print("Failed to parse arguments")

            tool_call_response = self._execute_tool_call(tool_call)

            # Show execution result status - check if it's an actual error message
            response_str = str(tool_call_response["tool_response"])
            if (
                response_str.startswith("Error:")
                or response_str.startswith("Error executing tool")
                or response_str.startswith("Error parsing tool arguments")
            ):
                print(f"Failed: {tool_call_response['tool_response']}")
            else:
                # Print the output from code execution (e.g., JSON results)
                if tool_call.function.name == "code_execution" and tool_call_response["tool_response"]:
                    # print(tool_call_response["tool_response"])
                    print()  # Blank line after output for consistency

            self.messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call_response["tool_call_id"],
                    "name": tool_call_response["tool_name"],
                    "content": str(tool_call_response["tool_response"]),
                }
            )

    ## Make an API call to the OpenAI client.
    def _make_api_call(self) -> Any:
        """
        Make an API call to the OpenAI client.
        """
        # Create clean tool definitions without callable functions for API
        clean_tools = []
        for tool in self.tools:
            if tool.get("type") == "function":
                func_info = tool.get("function", {})
                clean_tool = {
                    "type": "function",
                    "function": {
                        "name": func_info.get("name"),
                        "description": func_info.get("description", ""),
                        "parameters": func_info.get("parameters", {}),
                    },
                }
                clean_tools.append(clean_tool)

        return completion(
            model=self.model,
            messages=self.messages,  # type: ignore
            temperature=self.temperature,
            max_completion_tokens=self.max_tokens,
            tools=clean_tools if clean_tools else None,
        )

    ## Execute a single tool call and return the response.
    def _execute_tool_call(self, tool_call: Any) -> Dict[str, Any]:
        """
        Execute a single tool call and return the response.
        """
        tool_call_id = tool_call.id
        tool_name = tool_call.function.name

        try:
            if tool_name == "code_execution":
                tool_args = json.loads(tool_call.function.arguments)
                tool_args["kernel"] = self.kernel
            else:
                tool_args = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError as e:
            return {
                "tool_call_id": tool_call_id,
                "tool_name": tool_name,
                "tool_args": {},
                "tool_response": f"Error parsing tool arguments: {str(e)}",
            }

        # Get the tool function from our mapping
        tool_function = self._tool_functions.get(tool_name)

        if tool_function is None:
            tool_response = f"Error: Tool '{tool_name}' not found"
        else:
            try:
                tool_response = tool_function(**tool_args)
            except (TypeError, ValueError, AttributeError, RuntimeError) as e:
                tool_response = f"Error executing tool '{tool_name}': {str(e)}"

        return {
            "tool_call_id": tool_call_id,
            "tool_name": tool_name,
            "tool_args": tool_args,
            "tool_response": tool_response,
        }

    ## Set the system prompt for the agent if not already set.
    def _set_system_prompt(self, system_prompt: str) -> None:
        """
        Set the system prompt for the agent if not already set.
        """
        if not self.messages:
            self.messages.append({"role": "system", "content": system_prompt})
        elif self.messages[0].get("role") != "system":
            self.messages.insert(0, {"role": "system", "content": system_prompt})
