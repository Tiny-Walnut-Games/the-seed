"""
Warbler CDA API Module.

Production-ready FastAPI service for FractalStat-enabled RAG retrieval.
"""

from .service import app
from .cli import cli, APIClient

__all__ = ["app", "APIClient", "cli"]
