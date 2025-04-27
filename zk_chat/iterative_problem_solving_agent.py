from typing import List, Optional

import structlog

from mojentic.llm import LLMBroker, ChatSession
from mojentic.llm.tools.llm_tool import LLMTool

logger = structlog.get_logger()


class IterativeProblemSolvingAgent:
    """An agent that iteratively attempts to solve a problem using available tools.

    This solver uses a chat-based approach to break down and solve complex problems.
    It will continue attempting to solve the problem until it either succeeds,
    fails explicitly, or reaches the maximum number of iterations.

    Attributes
    ----------
    max_iterations : int
        Maximum number of attempts to solve the problem
    chat : ChatSession
        The chat session used for problem-solving interaction
    """

    max_iterations: int
    chat: ChatSession

    def __init__(self, llm: LLMBroker, available_tools: Optional[List[LLMTool]] = None, max_iterations: int = 3,
                 system_prompt: Optional[str] = None):
        """Initialize the IterativeProblemSolver.

        Parameters
        ----------
        llm : LLMBroker
            The language model broker to use for generating responses
        available_tools : Optional[List[LLMTool]], optional
            List of tools that can be used to solve the problem, by default None
        max_iterations : int, optional
            Maximum number of attempts to solve the problem, by default 3
        """
        self.max_iterations = max_iterations
        self.available_tools = available_tools or []
        self.chat = ChatSession(
            llm=llm,
            system_prompt=system_prompt or "You are a problem-solving assistant that can solve complex problems step by step. "
                                           "You analyze problems, break them down into smaller parts, and solve them systematically. "
                                           "If you cannot solve a problem completely in one step, you make progress and identify what to do next.",
            tools=self.available_tools,
            temperature=0.0,
        )

    def solve(self, problem: str):
        """Execute the problem-solving process.

        This method runs the iterative problem-solving process, continuing until one of
        these conditions is met:
        - The task is completed successfully ("DONE")
        - The task fails explicitly ("FAIL")
        - The maximum number of iterations is reached

        Parameters
        ----------
        problem : str
            The problem or request to be solved

        Returns
        -------
        str
            A summary of the final result, excluding the process details
        """
        iterations_remaining = self.max_iterations

        while True:
            result = self._step(problem)

            if "FAIL".lower() in result.lower():
                logger.info("Task failed", user_request=problem, result=result)
                break
            elif "DONE".lower() in result.lower():
                logger.info("Task completed", user_request=problem, result=result)
                break

            iterations_remaining -= 1
            if iterations_remaining == 0:
                logger.info("Max iterations reached", max_iterations=self.max_iterations,
                            user_request=problem, result=result)
                break

        result = self.chat.send(
            "Summarize the final result, and only the final result, without commenting on the process by which you achieved it.")

        return result

    def _step(self, problem: str) -> str:
        """Execute a single problem-solving step.

        This method sends a prompt to the chat session asking it to work on the user's request
        using available tools. The response should indicate success ("DONE") or failure ("FAIL").

        Parameters
        ----------
        problem : str
            The problem or request to be solved

        Returns
        -------
        str
            The response from the chat session, indicating the step's outcome
        """
        prompt = f"""
Given the user request:
{problem}

Use the tools at your disposal to act on their request. You may wish to create a step-by-step plan for more complicated requests.

If you cannot provide an answer, say only "FAIL".
If you have the answer, say only "DONE".
"""
        return self.chat.send(prompt)
