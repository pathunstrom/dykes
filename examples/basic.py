import dataclasses
import pathlib
import typing

import simple_parser


@dataclasses.dataclass
class WordCounterArgs:
    """A simple word counter. Provide file name to count words."""

    path: typing.Annotated[pathlib.Path, "The path to the file to word count."]
    dry_run: bool
    verbosity: typing.Annotated[simple_parser.Count, "Verbosity of script. Provide up to 3 times."]


if __name__ == "__main__":
    args = simple_parser.parse_args(WordCounterArgs)
    print(args)

#
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
