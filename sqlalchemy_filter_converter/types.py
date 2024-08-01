"""Types module.

Contains types and structures, represents its types.
"""

from typing import Any, Literal, NotRequired, TypedDict, get_args

DjangoOperatorsLiteral = Literal[
    "exact",
    "iexact",
    "contains",
    "icontains",
    "in",
    "gt",
    "gte",
    "lt",
    "lte",
    "startswith",
    "istartswith",
    "endswith",
    "iendswith",
    "range",
    "date",
    "year",
    "iso_year",
    "month",
    "day",
    "week",
    "week_day",
    "iso_week_day",
    "quarter",
    "time",
    "hour",
    "minute",
    "second",
    "isnull",
    "regex",
    "iregex",
]
DjangoOperatorsSet: set[DjangoOperatorsLiteral] = set(get_args(DjangoOperatorsLiteral))
AdvancedOperatorsLiteral = Literal["=", ">", "<", ">=", "<=", "between", "contains"]
AdvancedOperatorsSet: set[AdvancedOperatorsLiteral] = set(get_args(AdvancedOperatorsLiteral))
FilterConverterStrategiesLiteral = Literal["simple", "advanced", "django"]
FilterConverterStrategiesSet: set[FilterConverterStrategiesLiteral] = set(
    get_args(FilterConverterStrategiesLiteral),
)


class OperatorFilterDict(TypedDict):
    """Operator filter dict, that contains key-value for field and value with operator for them."""

    field: str
    value: Any
    operator: NotRequired[AdvancedOperatorsLiteral]
