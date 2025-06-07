import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated


@dataclass
class ExampleApplication:
    path: Annotated[Path, "The paths to operate on."]
    dry_run: bool
    prompt: bool
    verbosity: int


if __name__ == "__main__":
    parser = argparse.ArgumentParser("This is a sample script that operates on a file on disk")

    parser.add_argument("path", type=Path, help="The paths to operate on.")
    parser.add_argument("-d", "--dry-run", dest="dry_run", action="store_true")
    parser.add_argument("-p", "--prompt", dest="prompt", action="store_false")
    parser.add_argument("-v", "--verbosity", dest="verbosity", action="count", default=0)

    parsed = parser.parse_args()
    arguments = ExampleApplication(**vars(parsed))
    print(arguments)
