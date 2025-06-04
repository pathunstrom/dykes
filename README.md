# Do You Know Every Selection?

`dykes` helps you get a handle on your tools.

It uses `typing.NamedTuples` or `dataclasses` to declaratively set up your argument parser and then returns an instance of your argument class.

An example usage, in example_application.py

    from dataclasses import dataclass
    from pathlib import Path
    from typing import Annotated

    import dykes

    @dataclass
    class ExampleApplication:
        path: Annotated[Path, "The paths to operate on."]
        dry_run: bool
        prompt: dykes.StoreFalse
        verbosity: dykes.Count

    if __name__ == "__main__":
        arguments = dykes.parse_args(ExampleApplication)
        print(arguments)

Use this from the command line:

    python example_application.py ~ -d -vv

And the output looks like:

    ExampleApplication(path=Path('~'), dry_run=True, prompt=True, verbosity=2)

## Inlining `dykes`

While `dykes` is packaged to be used with pip, it's operational code is in a single file.
If you would like to vendor it, take the `src/dykes/__init__.py` and include it in your own project.

## What works

* Positional parameters
* Store True flags
  * Two variants: type a `bool` or use `dykes.StoreTrue`
* Store False flags
* Count flags
* A StrEnum of Argparse actions. `dykes.Action` instances can be passed to directly to `argparse.add_parameter`
* Parameter help strings: provide a bare string via Annotated
* Application description via your `dataclass` or `NamedTuple`'s docstring.
* `snake_case` field names converted to `--kebab-case` long options.

## What works but is underwhelming

* Parameter defaults. (positional parameters can't use them, and the other supported fields have good ones.)

## Coming Soon

* More actions
  * Store Const
  * Append
  * Append Const
  * Extend
  * Version
* More Options
  * Defining custom flags (currently derived from names)
  * nargs
  * const
  * choices
  * required
  * deprecated
* Proper documentation

## Coming Maybe

* Application framework based on `__call__`
* Subcommands

## Isn't That Name Insensitive?

Author and maintainer here: I am a transgender lesbian and I find it funny.
If you don't want that word in your project, that's fine!
Please see instructions above on how to inline the project.
Feel free to rename it.
