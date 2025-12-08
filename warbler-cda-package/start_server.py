#!/usr/bin/env python3
"""Direct server starter for Warbler CDA API Server.

This script provides a simple way to start the FastAPI server with uvicorn.
It includes basic debugging output and error handling.
"""

import argparse
import logging
import os
import sys
import traceback
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

import uvicorn
from warbler_cda.api.service import app

# Constants
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
DEFAULT_LOG_LEVEL = "info"
SEPARATOR_LENGTH = 40


@dataclass
class ServerConfig:
    """Configuration for the server."""
    host: str
    port: int
    log_level: str
    reload: bool

    def __post_init__(self) -> None:
        """Validate configuration values."""
        if not (1 <= self.port <= 65535):
            raise ValueError(f"Port must be between 1 and 65535, got {self.port}")

        # Basic host validation - accept localhost, IP addresses, or domain names
        if not self.host or len(self.host) > 253:
            raise ValueError(f"Invalid host: {self.host}")

        # Check if it's a valid hostname/IP
        try:
            urlparse(f"http://{self.host}")
        except ValueError:
            raise ValueError(f"Invalid host format: {self.host}")

        # Validate log level
        valid_levels = ["critical", "error", "warning", "info", "debug", "trace"]
        if self.log_level.lower() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}, got {self.log_level}")


def parse_args() -> ServerConfig:
    """Parse command line arguments and return validated configuration."""
    parser = argparse.ArgumentParser(
        description="Start the Warbler CDA API server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--host", default=os.getenv("HOST", DEFAULT_HOST),
        help="Host to bind the server to"
    )
    parser.add_argument(
        "--port", "-p", type=int, default=int(os.getenv("PORT", str(DEFAULT_PORT))),
        help="Port to bind the server to"
    )
    parser.add_argument(
        "--log-level", "-l",
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        default=os.getenv("LOG_LEVEL", DEFAULT_LOG_LEVEL).lower(),
        help="Uvicorn log level"
    )
    parser.add_argument(
        "--reload", action="store_true",
        help="Enable auto-reload (not recommended for Windows)"
    )

    args = parser.parse_args()

    # Handle reload default from environment
    reload_default = os.getenv("RELOAD", "").lower() in ("true", "1", "yes")
    if not args.reload:
        args.reload = reload_default

    return ServerConfig(
        host=args.host,
        port=args.port,
        log_level=args.log_level,
        reload=args.reload
    )


def print_startup_info(host: str, port: int) -> None:
    """Print server startup information."""
    print("Warbler CDA API Server")
    print("=" * SEPARATOR_LENGTH)
    print(f"App: {app.title}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print()
    print("Endpoints:")
    print(f"  Health check: http://{host}:{port}/health")
    print(f"  API docs:     http://{host}:{port}/docs")
    print()
    print("Press Ctrl+C to stop")


def setup_logging(log_level: str) -> None:
    """Configure logging for both application and uvicorn."""
    level = getattr(logging, log_level.upper())

    # Configure application logging
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Configure uvicorn to use our logging
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(level)


def main() -> None:
    """Main entry point."""
    try:
        config = parse_args()
    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)

    setup_logging(config.log_level)
    print_startup_info(config.host, config.port)

    try:
        uvicorn.run(
            app,
            host=config.host,
            port=config.port,
            log_level=config.log_level,
            reload=config.reload,
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        sys.exit(0)
    except ImportError as e:
        print(f"Import Error: {e}")
        traceback.print_exc()
        sys.exit(1)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"Port {config.port} is already in use")
        else:
            print(f"Network error: {e}")
        sys.exit(1)
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error("Error starting server: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
