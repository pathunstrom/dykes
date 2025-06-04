import dataclasses
import pathlib
import typing

import dykes


@dataclasses.dataclass
class WordCounterArgs:
    """A simple word counter. Provide file name to count words."""

    path: typing.Annotated[pathlib.Path, "The path to the file to word count."]
    dry_run: bool
    verbosity: typing.Annotated[dykes.Count, "Verbosity of script. Provide up to 3 times."]


if __name__ == "__main__":
    args = dykes.parse_args(WordCounterArgs)
    print(args)

# The equivalent code without dykes
#
# import argparse
# import dataclasses
# import pathlib
#
#
# @dataclasses.dataclass
# class WordCounterArgs:
#     """A simple word counter. Provide file name to count words."""
#
#     path: pathlib.Path
#     dry_run: bool
#
#
# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(
#         description="A simple word counter. Provide file name to count words."
#     )
#     parser.add_argument(
#         "path", type=pathlib.Path, help="The path to the file to word count."
#     )
#     parser.add_argument("-d", "--dry-run", action="store_true", dest="dry_run")
#     name_space = parser.parse_args()
#     args = WordCounterArgs(**vars(name_space))
#     print(args)
