from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("agentic_init")
except PackageNotFoundError:
    __version__ = "0.0.0"
