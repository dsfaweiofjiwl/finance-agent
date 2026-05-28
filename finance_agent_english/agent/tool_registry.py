#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool Registry - Tool registration and management
Agents can call tools to retrieve real-time data
"""

import json
import inspect
from typing import Dict, Callable, Any, List
from dataclasses import dataclass


@dataclass
class Tool:
    """Tool definition"""
    name: str
    description: str
    func: Callable
    parameters: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to LLM function call format"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": json.loads(self.parameters) if isinstance(self.parameters, str) else self.parameters
            }
        }


class ToolRegistry:
    """Tool registry manager"""

    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        func: Callable,
    ) -> None:
        """Register a tool"""
        tool = Tool(
            name=name,
            description=description,
            func=func,
            parameters=json.dumps(parameters, ensure_ascii=False)
        )
        self._tools[name] = tool

    def get_tool(self, name: str) -> Tool:
        """Get tool by name"""
        return self._tools.get(name)

    def list_tools(self) -> List[Tool]:
        """List all registered tools"""
        return list(self._tools.values())

    def get_openai_tools(self) -> List[Dict[str, Any]]:
        """Get tool definitions in OpenAI format"""
        return [t.to_dict() for t in self._tools.values()]

    def execute(self, name: str, **kwargs) -> Any:
        """Execute a tool"""
        tool = self.get_tool(name)
        if not tool:
            return f"Error: Tool '{name}' not found"
        return tool.func(**kwargs)
