import typing

from dykes import internal, options


def get_origin(t: type) -> type:
    """
    Get true type from a hint.

    A version of typing.get_origin that exposed Annotated types to their root
    and also returns the input for un-subscripted types.
    """
    result = typing.get_origin(t)
    if result is None:
        return t
    elif result is typing.Annotated:
        if isinstance(t, internal.HasOrigin) and isinstance(t.__origin__, (type, typing.GenericAlias)):  # Make mypy happy.
            return get_origin(t.__origin__)
        else:
            raise ValueError(
                "Annotated without a type or annotations. Please subscript Annotated."
            )
    return result


def get_field_type[T](cls: type[T] | list[type[T]]) -> type[T]:
    origin = get_origin(cls)
    if origin is list:
        if type(cls) is typing._AnnotatedAlias:
            type_args = typing.get_args(typing.get_args(cls)[0])
        else:
            type_args = typing.get_args(cls)
        if len(type_args) > 1:
            print(origin, typing.get_args(cls), type(cls))
            change_to = " or ".join(f"list[{t.__name__}]" for t in typing.get_args(cls))
            raise ValueError(
                f"dykes does not support lists with multiple type values. Convert {cls} to {change_to}"
            )
        elif len(type_args) == 0:
            return str
        else:
            return type_args[0]
    else:
        return cls


def get_meta_args[FieldType](cls: type[FieldType], parameter_options: internal.ParameterOptions) -> internal.ParameterOptions[FieldType]:
    if (meta := getattr(cls, "__metadata__", None)) is not None:
        for datum in meta:
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


def is_instance_unique[T: (str, options.Action, options.NArgs, options.Flags)](value: typing.Any, check_type: type[T], parameter_options: internal.ParameterOptions) -> typing.TypeGuard[T]:
    if not isinstance(value, check_type):
        return False

    if getattr(parameter_options, type_map[check_type]) != internal.UNSET:
        raise ValueError(f"Found multiple {check_type.__name__} in Annotated. Please use only one {check_type.__name__}")

    return True
