"""
Claude Code Integration Module

This module provides integration with Claude Code for AI reasoning and task processing.
It implements the actual functionality that was previously simulated in orchestrator.py.
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ClaudeResponse:
    """Represents a response from Claude Code."""
    success: bool
    content: str
    metadata: Dict[str, Any]
    error: Optional[str] = None


class ClaudeCodeIntegration:
    """Integration class for connecting with Claude Code."""

    def __init__(self):
        self.api_key = os.getenv("CLAUDE_API_KEY")
        self.base_url = os.getenv("CLAUDE_BASE_URL", "https://api.anthropic.com")
        self.default_model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")

        # Initialize connection settings
        self.session = None

    async def initialize(self):
        """Initialize the Claude Code connection."""
        try:
            # Import aiohttp for async HTTP requests
            import aiohttp
            self.session = aiohttp.ClientSession()
            logger.info("Claude Code integration initialized")
            return True
        except ImportError:
            logger.warning("aiohttp not available, using simulated Claude processing")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Claude Code integration: {e}")
            return False

    async def close(self):
        """Close the Claude Code connection."""
        if self.session:
            await self.session.close()

    async def process_task_with_claude(self, task_content: str, task_metadata: Dict[str, Any] = None) -> ClaudeResponse:
        """
        Process a task using Claude Code.

        Args:
            task_content: The content of the task to process
            task_metadata: Additional metadata about the task

        Returns:
            ClaudeResponse containing the result
        """
        if not self.session:
            # Fallback to simulated processing if no real connection
            return await self._simulate_claude_processing(task_content, task_metadata)

        try:
            # Prepare the request to Claude
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": self.api_key,
                "anthropic-version": "2023-06-01"
            }

            # Build the prompt for Claude based on the task content and skills
            prompt = await self._build_prompt_for_task(task_content, task_metadata)

            payload = {
                "model": self.default_model,
                "max_tokens": 1024,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }

            # Make the API call to Claude
            async with self.session.post(
                f"{self.base_url}/v1/messages",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result['content'][0]['text'] if result['content'] else ""

                    return ClaudeResponse(
                        success=True,
                        content=content,
                        metadata=result.get('usage', {})
                    )
                else:
                    error_text = await response.text()
                    logger.error(f"Claude API error: {response.status} - {error_text}")
                    return ClaudeResponse(
                        success=False,
                        content="",
                        metadata={},
                        error=f"API error: {response.status} - {error_text}"
                    )

        except Exception as e:
            logger.error(f"Error processing task with Claude: {e}")
            return await self._simulate_claude_processing(task_content, task_metadata)

    async def _build_prompt_for_task(self, task_content: str, task_metadata: Dict[str, Any]) -> str:
        """Build a prompt for Claude based on the task and available skills."""
        # Read the available skills from the vault
        skills_dir = Path("./AI_Employee_Vault/.claude/skills")
        skills_content = []

        if skills_dir.exists():
            for skill_file in skills_dir.glob("*.md"):
                try:
                    with open(skill_file, 'r', encoding='utf-8') as f:
                        skills_content.append(f"Skill: {skill_file.name}\n{f.read()}\n---\n")
                except Exception as e:
                    logger.warning(f"Could not read skill file {skill_file}: {e}")

        skills_text = "\n".join(skills_content)

        # Build the comprehensive prompt
        prompt = f"""You are an AI employee tasked with processing the following request:

TASK CONTENT:
{task_content}

AVAILABLE SKILLS AND GUIDELINES:
{skills_text}

METADATA:
{json.dumps(task_metadata, indent=2) if task_metadata else 'None'}

Based on the task and available skills, please provide:
1. An analysis of what needs to be done
2. A plan for execution (following the task_processor.md guidelines)
3. Any approval requirements (following the guidelines in the skills)
4. Specific next steps to take

Format your response as a structured plan that can be executed by the system."""

        return prompt

    async def _simulate_claude_processing(self, task_content: str, task_metadata: Dict[str, Any] = None) -> ClaudeResponse:
        """
        Simulate Claude processing when real API is not available.
        This maintains backward compatibility with the original simulate_claude_processing function.
        """
        logger.info(f"Simulating Claude processing for task")

        # Determine next action based on content (similar to original simulate function)
        if "approval" in task_content.lower() or "requires approval" in task_content.lower():
            # Return content indicating it needs approval
            content = """# Task Processing Result

## Analysis
The task requires human approval based on its content.

## Recommended Action
Move to Pending Approval queue for human review.

## Approval Required
Yes - this task requires human approval before proceeding.
"""
            next_folder = "Pending_Approval"
        else:
            # Return content indicating it can be completed
            content = """# Task Processing Result

## Analysis
The task can be processed automatically based on the provided information.

## Recommended Action
Move to Done queue as task is complete.

## Approval Required
No - this task can be completed automatically.
"""
            next_folder = "Done"

        return ClaudeResponse(
            success=True,
            content=content,
            metadata={"simulation": True, "next_folder": next_folder},
            error=None
        )


# Global instance for use in orchestrator
claude_integration = ClaudeCodeIntegration()


async def initialize_claude_integration():
    """Initialize the Claude integration globally."""
    return await claude_integration.initialize()


async def process_task_with_claude(task_content: str, task_metadata: Dict[str, Any] = None) -> ClaudeResponse:
    """Process a task with Claude Code."""
    return await claude_integration.process_task_with_claude(task_content, task_metadata)


async def close_claude_integration():
    """Close the Claude integration."""
    await claude_integration.close()