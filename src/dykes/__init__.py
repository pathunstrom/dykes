"""
Dykes is a tiny declarative argument parsing library.

The basic usage is to define a typed struct and pass that to
:func:`dykes.processing.parse_args`.

The public namespace includes :func:`~dykes.processing.parse_args`,
:func:`~dykes.processing.build_parser`, and the various types for declaring
various argparse options.
"""

from .processing import parse_args, build_parser
from .options import Action, Count, StoreFalse, StoreTrue

__all__ = [
    "options",
    "parse_args",
    "build_parser",
    "Action",
    "Count",
    "StoreFalse",
    "StoreTrue",
]
