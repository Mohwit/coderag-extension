"""Persistent Kernel for CodeAct framework.

This class provides a persistent kernel for the CodeAct framework.
It allows for the execution of code with persistent state.
"""
import threading
import time
import sys
from io import StringIO
from typing import Any, Dict, Optional
import ast

class PersistentKernel:
    """Persistent Kernel for CodeAct framework."""

    def __init__(self, namespace: Optional[Dict[str, Any]] = None, imports: str = "", timeout: int = 30) -> None:
        """Initialize the persistent kernel with optional imports and timeout.

        Args:
            namespace: Optional initial namespace.
            imports: String containing import statements to execute initially.
            timeout: Maximum execution time in seconds for code (default 30).
        """
        self.namespace: Dict[str, Any] = namespace or {}
        self.imports = imports
        self.timeout = timeout
        self.background_threads = []

        if self.imports:
            self._safe_exec(self.imports)

    def reset(self) -> None:
        """Reset the kernel namespace, keeping only initial imports."""
        self.namespace.clear()
        if self.imports:
            self._safe_exec(self.imports)

    def execute_background(self, code: str) -> Dict[str, Any]:
        """Execute code in a background thread (useful for servers)."""
        def run_code():
            try:
                self._safe_exec(code)
            except Exception as e:
                print(f"Background execution error: {e}")

        thread = threading.Thread(target=run_code, daemon=True)
        thread.start()
        self.background_threads.append(thread)
        time.sleep(2)  # Give the server a moment to start

        # Clean up finished threads
        self.background_threads = [t for t in self.background_threads if t.is_alive()]

        return {
            "success": True,
            "output": "Code started in background thread",
            "error": None
        }

    def execute(self, code: str) -> Dict[str, Any]:
        """Execute the given code in the persistent kernel with a timeout."""
        if not isinstance(code, str):
            return {
                "success": False,
                "output": "",
                "error": "Code must be a string",
            }

        old_stdout = sys.stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            exec_thread = threading.Thread(target=self._safe_exec, args=(code,))
            exec_thread.start()
            exec_thread.join(timeout=self.timeout)

            if exec_thread.is_alive():
                raise TimeoutError(f"Execution timed out after {self.timeout} seconds")

            output = captured_output.getvalue()
            return {"success": True, "output": output, "error": None}

        except Exception as e:
            return {
                "success": False,
                "output": captured_output.getvalue(),
                "error": str(e),
            }

        finally:
            sys.stdout = old_stdout

    def _safe_exec(self, code: str) -> None:
        """Safely execute code after basic security checks."""
        try:
            ast.parse(code)  # Basic syntax check
        except SyntaxError as e:
            raise SyntaxError(f"Invalid Python syntax: {e}")

        exec(code, self.namespace)

if __name__ == "__main__":
    # Example usage
    kernel = PersistentKernel(imports="import math")

    # Example 1: Basic execution
    result = kernel.execute("x = 2\nprint(f'x = {x}')")
    print("Example 1 result:", result)

    # Example 2: Using previous variable
    result = kernel.execute("y = x * math.pi\nprint(f'y = {y}')")
    print("Example 2 result:", result)

    # Example 3: Timeout example
    result = kernel.execute("import time\nwhile True: time.sleep(1)")
    print("Example 3 result:", result)

    # Example 4: Background execution
    result = kernel.execute_background("import time\nwhile True: print('Background task running'); time.sleep(5)")
    print("Example 4 result:", result)

    # Wait a bit to see background execution
    time.sleep(12)
    print("Main thread finished")
