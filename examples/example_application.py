from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import dykes


@dataclass
class ExampleApplication:
    """
    This is a sample script that operates on a file on disk.
    """
    path: Annotated[Path, "The paths to operate on."]
    dry_run: bool
    prompt: dykes.StoreFalse
    verbosity: dykes.Count


if __name__ == "__main__":
    arguments = dykes.parse_args(ExampleApplication)
    print(arguments)
