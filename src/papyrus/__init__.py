from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("Papyrus")
except PackageNotFoundError:
    __version__ = "unknown"
