from typing import Any

import pytest

from sqlalchemy_filter_converter import converters, guards

any_value = object()


@pytest.mark.parametrize(
    ("_dct", "expected_result"),
    [
        ({"field": "abc", "value": any_value, "operator": ">"}, True),
        ({"field": "abc", "value": any_value}, True),
        ({"field": 125, "value": any_value}, False),
        ({"field": 125, "value": any_value, "operator": ">"}, False),
        ({"field": "abc", "value": any_value, "operator": "pow"}, False),  # no such operator
        ({"field": "abc", "operator": ">"}, False),  # no value
    ],
)
def test_is_dict_simple_filter_dict(
    _dct: dict[Any, Any],  # noqa: PT019
    expected_result: bool,  # noqa: FBT001
) -> None:
    assert guards.is_dict_simple_filter_dict(_dct) == expected_result


@pytest.mark.parametrize(
    ("_dct", "expected_result"),
    [
        (converters.SimpleFilterConverter.lookup_mapping, False),
        (converters.AdvancedOperatorFilterConverter.lookup_mapping, False),
        (converters.DjangoLikeFilterConverter.lookup_mapping, True),
        ({"abc": (1, 2)}, False),
        ({"abc": (1, 2, 3)}, False),
    ],
)
def test_has_nested_lookups(
    _dct: dict[Any, Any],  # noqa: PT019
    expected_result: bool,  # noqa: FBT001
) -> None:
    assert guards.has_nested_lookups(_dct) == expected_result
