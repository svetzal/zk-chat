"""
Agent runner for programmatic execution of zk-chat.

Invokes the zk-chat CLI via subprocess and captures results.
"""
import subprocess
import sys
import time
from pathlib import Path

from pydantic import BaseModel


class ExecutionResult(BaseModel):
    """Result of agent execution"""
    success: bool
    output: str
    error: str | None = None
    duration: float = 0.0


class AgentRunner:
    """Runs the zk-chat agent programmatically"""

    def __init__(
        self,
        vault_path: Path,
        gateway: str,
        model: str | None = None,
        visual_model: str | None = None,
        agent_mode: str = "interactive"
    ):
        self.vault_path = vault_path
        self.gateway = gateway
        self.model = model
        self.visual_model = visual_model
        self.agent_mode = agent_mode  # Note: For documentation only; query always uses agent mode

    def run(self, prompt: str, timeout: int = 300) -> ExecutionResult:
        """
        Execute agent with given prompt.

        Uses subprocess to invoke `zk-chat query` which runs the agent.
        The query command always uses agent mode with autonomous problem-solving.

        Returns ExecutionResult with output and timing.
        """
        start_time = time.time()

        cmd = [
            sys.executable, "-m", "zk_chat.main", "query",
            "--vault", str(self.vault_path),
            "--gateway", self.gateway
        ]

        if self.model:
            cmd.extend(["--model", self.model])

        if self.visual_model:
            cmd.extend(["--visual-model", self.visual_model])

        # Note: query command now always uses agent mode, no flag needed

        cmd.append(prompt)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            duration = time.time() - start_time

            return ExecutionResult(
                success=(result.returncode == 0),
                output=result.stdout,
                error=result.stderr if result.returncode != 0 else None,
                duration=duration
            )

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return ExecutionResult(
                success=False,
                output="",
                error=f"Agent execution timed out after {timeout} seconds",
                duration=duration
            )

        except Exception as e:
            duration = time.time() - start_time
            return ExecutionResult(
                success=False,
                output="",
                error=str(e),
                duration=duration
            )
