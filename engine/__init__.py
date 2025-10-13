"""
Engine Module - Optional Integration Layer

Provides optional integration points for the self-care system with
existing or future development workflows.

This module is designed to be imported only when needed and
does not break existing functionality if not used.
"""

__version__ = "1.0.0"
__author__ = "Tiny Walnut Games Living Dev Agent"

# Optional imports - only available if modules exist
try:
    from .telemetry import DevelopmentTelemetry
    __all__ = ['DevelopmentTelemetry']
except ImportError:
    __all__ = []
    
"""Exports for the Cognitive Geo-Thermal Lore Engine scaffold."""
from .giant_compressor import GiantCompressor
from .melt_layer import MeltLayer
from .evaporation import EvaporationEngine
from .castle_graph import CastleGraph
from .selector import Selector
from .governance import Governance
from .telemetry import CycleTelemetry

__all__ = [
    "GiantCompressor",
    "MeltLayer",
    "EvaporationEngine",
    "CastleGraph",
    "Selector",
    "Governance",
    "CycleTelemetry",
]
