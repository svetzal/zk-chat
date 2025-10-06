"""
Agent runner for programmatic execution of zk-chat.

Invokes the zk-chat CLI via subprocess and captures results.
"""
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ExecutionResult:
    """Result of agent execution"""
    success: bool
    output: str
    error: Optional[str] = None
    duration: float = 0.0


class AgentRunner:
    """Runs the zk-chat agent programmatically"""

    def __init__(
        self,
        vault_path: Path,
        gateway: str,
        model: Optional[str] = None,
        visual_model: Optional[str] = None,
        agent_mode: str = "interactive",
        unsafe: bool = False,
        use_git: bool = False
    ):
        self.vault_path = vault_path
        self.gateway = gateway
        self.model = model
        self.visual_model = visual_model
        self.agent_mode = agent_mode
        self.unsafe = unsafe
        self.use_git = use_git

    def run(self, prompt: str, timeout: int = 300) -> ExecutionResult:
        """
        Execute agent with given prompt.

        Uses subprocess to invoke zk-chat CLI with the prompt.
        Returns ExecutionResult with output and timing.
        """
        start_time = time.time()

        cmd = [
            "zk-chat", "query",
            "--vault", str(self.vault_path),
            "--gateway", self.gateway
        ]

        if self.model:
            cmd.extend(["--model", self.model])

        if self.visual_model:
            cmd.extend(["--visual-model", self.visual_model])

        if self.agent_mode == "autonomous":
            cmd.append("--agent")

        if self.unsafe:
            cmd.append("--unsafe")

        if self.use_git:
            cmd.append("--git")

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
