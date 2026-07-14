"""Public command-line tools for the Seabed API."""

from seabed_cli.client import SeabedClient
from seabed_cli.config import SeabedConfig

__all__ = ["SeabedClient", "SeabedConfig"]
__version__ = "0.1.0"
