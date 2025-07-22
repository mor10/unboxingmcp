"""
Open-Meteo Weather MCP Server Package

A comprehensive weather server implementation using the Model Context Protocol (MCP)
and Open-Meteo APIs for weather forecasting and location services.
"""

from .server import mcp, main
from .tools import register_tools
from .resources import register_resources  
from .prompts import register_prompts

__all__ = ["mcp", "main", "register_tools", "register_resources", "register_prompts"]