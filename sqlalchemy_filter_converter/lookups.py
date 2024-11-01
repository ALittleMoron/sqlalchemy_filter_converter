import operator as builtin_operator
from typing import TYPE_CHECKING

from sqlalchemy_filter_converter import operators as custom_operator

if TYPE_CHECKING:
    from sqlalchemy_filter_converter.types import (
        LookupMapping,
        LookupMappingWithNested,
        NestedFilterNames,
    )

EMPTY_NESTED_FILTER_NAMES: "NestedFilterNames" = set()
DJANGO_NESTED_FILTER_NAMES: "NestedFilterNames" = {
    "exact",
    "iexact",
    "in",
    "gt",
    "gte",
    "lt",
    "lte",
    "range",
}


ADVANCED_LOOKUP_MAPPING: "LookupMapping" = {  # pyright: ignore[reportAssignmentType]
    "=": builtin_operator.eq,
    ">": builtin_operator.gt,
    "<": builtin_operator.lt,
    ">=": builtin_operator.ge,
    "<=": builtin_operator.le,
    "is": custom_operator.is_,
    "is_not": custom_operator.is_not,
    "between": custom_operator.between,
    "contains": custom_operator.contains,
}
DJANGO_LIKE_LOOKUP_MAPPING: "LookupMappingWithNested" = {  # type: ignore[reportIncompatibleVariableOverride]
    "exact": (custom_operator.django_exact, EMPTY_NESTED_FILTER_NAMES),
    "iexact": (custom_operator.django_iexact, EMPTY_NESTED_FILTER_NAMES),
    "contains": (custom_operator.django_contains, EMPTY_NESTED_FILTER_NAMES),
    "icontains": (custom_operator.django_icontains, EMPTY_NESTED_FILTER_NAMES),
    "in": (custom_operator.django_in, EMPTY_NESTED_FILTER_NAMES),
    "gt": (builtin_operator.gt, EMPTY_NESTED_FILTER_NAMES),
    "gte": (builtin_operator.ge, EMPTY_NESTED_FILTER_NAMES),
    "lt": (builtin_operator.lt, EMPTY_NESTED_FILTER_NAMES),
    "lte": (builtin_operator.le, EMPTY_NESTED_FILTER_NAMES),
    "startswith": (custom_operator.django_startswith, EMPTY_NESTED_FILTER_NAMES),
    "istartswith": (custom_operator.django_istartswith, EMPTY_NESTED_FILTER_NAMES),
    "endswith": (custom_operator.django_endswith, EMPTY_NESTED_FILTER_NAMES),
    "iendswith": (custom_operator.django_iendswith, EMPTY_NESTED_FILTER_NAMES),
    "range": (custom_operator.django_range, EMPTY_NESTED_FILTER_NAMES),
    "date": (custom_operator.django_date, DJANGO_NESTED_FILTER_NAMES),
    "year": (custom_operator.django_year, DJANGO_NESTED_FILTER_NAMES),
    "iso_year": (custom_operator.django_iso_year, DJANGO_NESTED_FILTER_NAMES),
    "month": (custom_operator.django_month, DJANGO_NESTED_FILTER_NAMES),
    "day": (custom_operator.django_day, DJANGO_NESTED_FILTER_NAMES),
    "week": (custom_operator.django_week, DJANGO_NESTED_FILTER_NAMES),
    "week_day": (custom_operator.django_week_day, DJANGO_NESTED_FILTER_NAMES),
    "iso_week_day": (custom_operator.django_iso_week_day, DJANGO_NESTED_FILTER_NAMES),
    "quarter": (custom_operator.django_quarter, DJANGO_NESTED_FILTER_NAMES),
    "time": (custom_operator.django_time, DJANGO_NESTED_FILTER_NAMES),
    "hour": (custom_operator.django_hour, DJANGO_NESTED_FILTER_NAMES),
    "minute": (custom_operator.django_minute, DJANGO_NESTED_FILTER_NAMES),
    "second": (custom_operator.django_second, DJANGO_NESTED_FILTER_NAMES),
    "isnull": (custom_operator.django_isnull, EMPTY_NESTED_FILTER_NAMES),
    "regex": (custom_operator.django_regex, EMPTY_NESTED_FILTER_NAMES),
    "iregex": (custom_operator.django_iregex, EMPTY_NESTED_FILTER_NAMES),
}
