import types
import typing

from . import internal, options

_Annotation: typing.TypeAlias = type | typing._SpecialForm


def _strip_decor(t: _Annotation) -> type | typing._SpecialForm:
    """
    Strip Optional, Annotated, Final, etc
    """
    origin = typing.get_origin(t)
    args = list(typing.get_args(t))
    match origin:
        case typing.Annotated:
            return _strip_decor(args[0])
        case typing.Optional:
            return _strip_decor(args[0])
        case typing.Union if len(args) == 2 and types.NoneType in args:
            # X|None, semantically the same as Optional
            args.remove(types.NoneType)
            return args[0]
        case typing.Union:
            # Dubious that we should handle this
            return typing.Union[*map(_strip_decor, args)]
        # FIXME: Do more
        case _:
            return t


def get_origin_type(t: _Annotation) -> type:
    """
    Get true type from a hint. (That is, the actual type of the annotated variable.)

    A version of typing.get_origin that exposed Annotated types to their root
    and also returns the input for un-subscripted types.
    """
    t = _strip_decor(t)
    result = typing.get_origin(t)
    if result is None:
        # "unsupported types" ie plain classes
        return t  # type: ignore
    elif t is typing.Annotated:
        raise ValueError(
            "Annotated without a type or annotations. Please subscript Annotated."
        )
    elif result is typing.Annotated:
        # Despite the name, get_origin gets the outer type and __origin__ is the inner type
        inner: _Annotation = t.__origin__  # type: ignore
        return get_origin_type(inner)
    else:
        # This covers:
        # * Regular annotations (list[str])
        # * Jamie isn't sure what else
        assert isinstance(result, type)
        return result


def get_inner_type(cls: _Annotation) -> type:
    """
    Get the type that's used to construct individual items.
    """
    cls = _strip_decor(cls)
    outer = get_origin_type(cls)
    origin = typing.get_origin(cls)
    print(f"{cls=} {outer=} {origin=} {_strip_decor(cls)=}")
    # breakpoint()
    if outer is list:
        if type(cls) is typing._AnnotatedAlias:  # type:ignore
            type_args = typing.get_args(typing.get_args(cls)[0])
        else:
            type_args = typing.get_args(cls)
        if len(type_args) > 1:
            change_to = " or ".join(f"list[{t.__name__}]" for t in typing.get_args(cls))
            raise ValueError(
                f"dykes does not support lists with multiple type values. Convert {cls} to {change_to}"
            )
        elif len(type_args) == 0:
            return str
        else:
            inner = _strip_decor(type_args[0])
            assert isinstance(inner, type)
            return inner
    else:
        assert isinstance(cls, type)
        return cls


def fill_meta_args[FieldType](
    annos: list, parameter_options: internal.ParameterOptions
) -> internal.ParameterOptions[FieldType]:
    for datum in annos:
        if is_instance_unique(datum, options.Action, parameter_options):
            parameter_options.action = datum
        elif is_instance_unique(datum, str, parameter_options):
            parameter_options.help = datum
        elif is_instance_unique(datum, options.NArgs, parameter_options):
            parameter_options.nargs = datum.value
        elif is_instance_unique(datum, options.Flags, parameter_options):
            parameter_options.flags = datum.value

    return parameter_options


type_map = {
    options.Action: "action",
    options.NArgs: "nargs",
    options.Flags: "flags",
    str: "help",
}


def is_instance_unique[T: (str, options.Action, options.NArgs, options.Flags)](
    value: typing.Any, check_type: type[T], parameter_options: internal.ParameterOptions
) -> typing.TypeGuard[T]:
    if not isinstance(value, check_type):
        return False

    if getattr(parameter_options, type_map[check_type]) != internal.UNSET:
        raise ValueError(
            f"Found multiple {check_type.__name__} in Annotated. Please use only one {check_type.__name__}"
        )

    return True
