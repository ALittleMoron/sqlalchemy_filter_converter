"""TypeGuards module.

Contains functions-checkers of filter types.
"""

from typing import TYPE_CHECKING, Any, TypeGuard

from sqlalchemy_filter_converter.types import AdvancedOperatorsSet, OperatorFilterDict

if TYPE_CHECKING:
    from sqlalchemy_filter_converter.types import AnyLookupMapping, LookupMappingWithNested


def is_dict_simple_filter_dict(value: dict[Any, Any]) -> TypeGuard["OperatorFilterDict"]:
    """TypeGuard for checking dict is ``OperatorFilterDict`` (typed dict) instance.

    OperatorFilterDict should has ``field``, ``value``, and ``operator`` keys with validated values:

    ``field``: any string.
    ``value``: any value.
    ``operator``: any string of ``AdvancedOperatorsLiteral``.
    """
    if "field" not in value or not isinstance(value["field"], str):
        return False
    if "value" not in value:
        return False
    return not ("operator" in value and value["operator"] not in AdvancedOperatorsSet)


def has_nested_lookups(mapping: "AnyLookupMapping") -> TypeGuard["LookupMappingWithNested"]:
    """TypeGuard for specify converter mapping type with nested lookups.

    By default, all mappings can have either operator function or tuple of operator function and
    available sub-lookups set.
    """
    if not mapping:
        return False
    for value in mapping.values():
        if not isinstance(value, tuple):  # type: ignore[reportUnnecessaryIsInstance]
            return False
        if len(value) != 2:  # type: ignore[reportUnnecessaryIsInstance] # noqa: PLR2004
            return False
        if not isinstance(value[1], set):  # type: ignore[reportUnnecessaryIsInstance]
            return False
    return True
