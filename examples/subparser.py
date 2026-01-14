import dataclasses
import typing

import dykes


@dataclasses.dataclass
class ConfigCmd:
    """
    Configure the command
    """

    pass


@dataclasses.dataclass
class DoCmd:
    """
    Do the thing
    """

    path: typing.Annotated[str, "Path to do thing with"]
    dest: typing.Annotated[
        str,
        "Where to put it",
        dykes.Action.STORE,
    ]


@dataclasses.dataclass
class ComplexArgs:
    """A simple word counter. Provide file name to count words."""

    verbose: typing.Annotated[dykes.StoreTrue, "Be verbose"] = False
    dry_run: bool = False

    config: dykes.Subparser[ConfigCmd] = None
    do: dykes.Subparser[DoCmd] = None


if __name__ == "__main__":
    args = dykes.parse_args(ComplexArgs)
    print(args)
