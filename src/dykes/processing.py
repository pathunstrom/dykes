"""
The dykes plumbing module.

This is all the things used internally to turn your definitions into something useful.
"""

import argparse
import dataclasses
import typing
import warnings
from inspect import getdoc
from sys import argv

from . import options, internal, utils

NO_TYPE = options.Action.COUNT, options.Action.STORE_FALSE, options.Action.STORE_TRUE
MUST_BE_FLAG = (
    options.Action.COUNT,
    options.Action.STORE_TRUE,
    options.Action.STORE_FALSE,
)


def parse_args[ArgsType](
    parameter_definition: type[ArgsType], *, args: list | None = None
) -> ArgsType:
    """
    Process arguments and conform them to an input type.

    Supports dataclasses and NamedTuples.

    Sample use:

        from dataclasses import dataclass
        from pathlib import Path

        from dykes import parse_args, Count

        @dataclass
        class Application:
            input: Path
            dry_run: bool
            verbosity: dykes.Count

        args = parse_args(Application)
        print(args)
    """
    if args is None:
        args = argv[1:]
    parser = build_parser(parameter_definition)
    parsed = parser.parse_args(args)
    return build_instance(parameter_definition, vars(parsed))


def build_parser(application_definition: type) -> argparse.ArgumentParser:
    description = getdoc(application_definition)
    parser = argparse.ArgumentParser(description=description)
    _build_parser("", application_definition, parser)
    return parser


def _build_parser(
    path: str, application_definition: type, parser: argparse.ArgumentParser
):
    fields = _get_fields(application_definition)
    subparsers = None

    parser.set_defaults(**{f"cls:{path}": application_definition})

    for fname, field in fields:
        # field.type is the rich type of the attribute
        # outer_type is the rich type simplified to a real class
        # inner_type is the innermost type of any collections (ie, the construction type of arguments)
        # On *_type, Optional[] (aka _|None) is stripped
        outer_type = utils.get_origin_type(field.type)
        inner_type = utils.get_inner_type(field.type)
        parameter_options: internal.ParameterOptions = internal.ParameterOptions(
            dest=f"{path}.{fname}" if path else fname,
            type=inner_type,
            metavar=fname,
            # default=internal.UNSET if field.default is internal.UNSET else repr(field.default),
        )

        if options._SUBPARSER in field.annotations:
            assert len(field.annotations) == 1, (
                "Can't mix other annotations with Subparser"
            )
            assert outer_type == inner_type
            innercls = inner_type
            if subparsers is None:
                subparsers = parser.add_subparsers(dest=f"subparser:{path}")
            subparser = subparsers.add_parser(fname, help=innercls.__doc__)
            _build_parser(f"{path}.{fname}" if path else fname, innercls, subparser)
        else:
            parameter_options = utils.fill_meta_args(
                field.annotations, parameter_options
            )

            if parameter_options.action is internal.UNSET:
                if inner_type is bool:
                    if field.default is True:
                        parameter_options.action = options.Action.STORE_FALSE
                    elif field.default in (False, internal.UNSET):
                        parameter_options.action = options.Action.STORE_TRUE

            if parameter_options.action in NO_TYPE:
                parameter_options.type = internal.UNSET

            store_flag_unset = (
                parameter_options.action is options.Action.STORE
                and parameter_options.flags is internal.UNSET
            )
            # If explicit Store action, we assume it's a flag.
            must_be_flag_unset = (
                parameter_options.action in MUST_BE_FLAG and not parameter_options.flags
            )
            if store_flag_unset or must_be_flag_unset:
                parameter_options.flags = [
                    f"-{fname[0]}",
                    f"--{fname.replace('_', '-')}",
                ]

            # if parameter_options.action is options.Action.COUNT:
            #     parameter_options.default = (
            #         parameter_options.default if parameter_options.default else 0
            #     )

            if outer_type is list and parameter_options.nargs is internal.UNSET:
                parameter_options.nargs = "+"

            flag_unset = parameter_options.flags is internal.UNSET
            # default_set = parameter_options.default is not internal.UNSET
            default_set = field.default
            nargs_not_default_friendly = parameter_options.nargs not in ("?", "*")
            if default_set and flag_unset and nargs_not_default_friendly:
                raise ValueError(
                    "Positional arguments cannot have defaults without NumberOfArguments '?' or '*'."
                )

            arguments = parameter_options.as_dict()
            flags = arguments.pop("flags", None)
            if not flags:
                name_or_flags = [arguments.pop("dest")]
            else:
                name_or_flags = flags
                if arguments.get("action", None) not in (
                    None,
                    options.Action.STORE,
                    options.Action.APPEND,
                    options.Action.EXTEND,
                ):
                    arguments.pop("metavar")
            # Don't let argparse deal with defaults; that's the struct's job
            # FIXME: Do this so that %(default)s in help works
            parser.add_argument(*name_or_flags, default=argparse.SUPPRESS, **arguments)

    return parser


def _get_default_dataclass(data_class_field: dataclasses.Field):
    if data_class_field.default is not dataclasses.MISSING:
        return data_class_field.default
    elif data_class_field.default_factory is not dataclasses.MISSING:
        return data_class_field.default_factory()
    else:
        return internal.UNSET


def _get_dataclass_fields(cls: type) -> list[str] | None:
    try:
        return [f.name for f in dataclasses.fields(cls)]
    except TypeError:
        return None


class UsageWarning(RuntimeWarning):
    pass


def _get_fields(cls: type) -> typing.Iterable[tuple[str, internal.Field]]:
    """
    Reads all the data from attributes, annotations, library field objects, etc.
    """
    # Doesn't include Annotated
    simple_annos = typing.get_type_hints(cls)
    # Does include Annotated
    full_annos = typing.get_type_hints(cls, include_extras=True)
    if (attrnames := _get_dataclass_fields(cls)) is not None:
        pass
    elif issubclass(cls, tuple):
        # Assumed to be NamedTuple
        try:
            attrnames = list(cls._fields)  # type: ignore
        except AttributeError as exc:
            raise TypeError(
                "Must use typing.NamedTuple or collections.namedtuple. Got {cls!r}"
            ) from exc
    else:
        # Vanilla, read the attributes off the class
        attrnames = [
            n
            for c in cls.__mro__
            if c is not tuple
            # Not dir(), only want things defined on this class, in definition order
            for n in vars(c).keys()
            if not n.startswith("_")
        ]

        assert not set(full_annos.keys()) - set(attrnames), (
            "FIXME: Mix in annotations with defined fields"
        )

        # Methods are callables without annotations
        for aname in attrnames[:]:
            if callable(getattr(cls, aname)) and aname not in full_annos:
                attrnames.remove(aname)

    for field_name in attrnames:
        field_default = getattr(cls, field_name, internal.UNSET)
        field_type = simple_annos.get(field_name, object)
        field_anno = full_annos.get(field_name, None)
        is_subparser = False

        if typing.get_origin(field_type) is options.Subparser:
            field_type = typing.get_args(field_type)[0]
            is_subparser = True

        if field_anno is field_type:  # Simple annotation
            field_anno = None

        if field_anno is not None:
            anno_list = list(typing.get_args(field_anno))
            anno_list.pop(0)  # Remove the base type, that's field_type
        else:
            anno_list = []

        if is_subparser:
            anno_list.append(options._SUBPARSER)

        if issubclass(cls, tuple):
            # NamedTuple
            # asserting this was covered above
            assert hasattr(cls, "_field_defaults")
            field_default = cls._field_defaults.get(field_name, internal.UNSET)
        elif isinstance(field_default, dataclasses.Field):
            # dataclass
            field_default = _get_default_dataclass(field_default)
        elif hasattr(field_default, "default"):
            # XXX: Should this be an exception?
            warnings.warn(
                f"Saw a {field_default!r} as a default value; is this an unsupported struct?",
                UsageWarning,
            )

        yield (
            field_name,
            internal.Field(
                name=field_name,
                default=field_default,
                type=field_type,
                annotations=anno_list,
            ),
        )


def _dict_remove_prefix(prefix: str, dct: dict) -> dict:
    return {
        key.removeprefix(prefix): value
        for key, value in dct.items()
        if key.startswith(prefix)
    }


def build_instance[T](cls: type[T], params: dict[str, typing.Any]) -> T:
    # First, instantiate any inner classes that need to happen
    subparsers: dict[str, str] = _dict_remove_prefix("subparser:", params)
    classes: dict[str, type] = _dict_remove_prefix("cls:", params)
    params = {key: value for key, value in params.items() if ":" not in key}
    return _build_instance(cls, params, subparsers, classes)


def _build_instance[T](
    cls: type[T],
    params: dict[str, typing.Any],
    subparsers: dict[str, str],
    classes: dict[str, type],
) -> T:
    # Get this level of params handled
    attrs = {key: value for key, value in params.items() if "." not in key}

    if subparsers and subparsers[""] is not None:
        subitem = subparsers.pop("")
        attrs[subitem] = _build_instance(
            classes[subitem],
            _dict_remove_prefix(f"{subitem}.", params),
            _dict_remove_prefix(f"{subitem}.", subparsers),
            _dict_remove_prefix(f"{subitem}.", classes),
        )

    return cls(**attrs)
