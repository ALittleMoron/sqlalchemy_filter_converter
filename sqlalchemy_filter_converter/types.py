"""Types module.

Contains types and structures, represents its types.
"""

import enum
from typing import Any, Literal, NotRequired, Protocol, TypedDict, get_args

from sqlalchemy import ColumnElement

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
IsValid = bool
Message = str
FilterDict = dict[str, Any]
SQLAlchemyFilter = ColumnElement[bool]
NestedFilterNames = set[str]


class OperatorFilterDict(TypedDict):
    """Operator filter dict, that contains key-value for field and value with operator for them."""

    field: str
    value: Any
    operator: NotRequired[AdvancedOperatorsLiteral]


class OperatorFunctionProtocol(Protocol):  # pragma: no cover
    def __call__(
        self,
        a: Any,
        b: Any,
        *,
        subproduct_use: bool = False,
    ) -> Any: ...


LookupMapping = dict[enum.Enum | str, OperatorFunctionProtocol]
LookupMappingWithNested = dict[enum.Enum | str, tuple[OperatorFunctionProtocol, NestedFilterNames]]
AnyLookupMapping = LookupMapping | LookupMappingWithNested
