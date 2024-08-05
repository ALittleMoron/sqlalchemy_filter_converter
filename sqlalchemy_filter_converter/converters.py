"""Main module for sqlalchemy filters.

Contains base converter and 3 implementations:

1) Simple filter - filter with key-value format. (``key - field`` equals to ``value``)
2) Advanced filter - key-value filter with additional operator (what to do with value for given
key).
3) Django filter - django-sqlalchemy filter adapter.
"""

import enum
import operator as builtin_operator
from abc import ABC, abstractmethod
from collections.abc import Sequence
from inspect import signature
from typing import TYPE_CHECKING, Any, ClassVar, final

from dev_utils.abstract import Abstract, abstract_class_property
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy_dev_utils import get_sqlalchemy_attribute, get_valid_field_names

from sqlalchemy_filter_converter import operators as custom_operator
from sqlalchemy_filter_converter.exc import FilterError
from sqlalchemy_filter_converter.guards import has_nested_lookups, is_dict_simple_filter_dict

if TYPE_CHECKING:
    from sqlalchemy.orm import DeclarativeBase


IsValid = bool
Message = str
FilterDict = dict[str, Any]
SQLAlchemyFilter = ColumnElement[bool]
OperatorFunction = custom_operator.OperatorFunctionProtocol
NestedFilterNames = set[str]
LookupMapping = dict[enum.Enum | str, OperatorFunction]
LookupMappingWithNested = dict[enum.Enum | str, tuple[OperatorFunction, NestedFilterNames]]
AnyLookupMapping = LookupMapping | LookupMappingWithNested

empty_nested_filter_names: NestedFilterNames = set()
django_nested_filter_names: NestedFilterNames = {
    "exact",
    "iexact",
    "in",
    "gt",
    "gte",
    "lt",
    "lte",
    "range",
}


def execute_operator_function(
    func: OperatorFunction,
    a: Any,  # noqa: ANN401
    b: Any,  # noqa: ANN401
    subproduct_use: bool = False,  # noqa: FBT001, FBT002
) -> Any:  # noqa: ANN401
    """Call given operator function with checking for ``subproduct_use`` signature.

    Simple wrapper to not execute function every time with checking, that operator has
    subproduct_use.
    """
    function_signature = signature(func)
    if function_signature.parameters.get("subproduct_use"):
        return func(a, b, subproduct_use=subproduct_use)
    # function has no subproduct_use param.
    return func(a, b)


class BaseFilterConverter(ABC, Abstract):
    """Base class for filter converters."""

    lookup_mapping: ClassVar[AnyLookupMapping] = abstract_class_property(LookupMapping)

    @classmethod
    @abstractmethod
    def _is_filter_valid(
        cls,
        model: type["DeclarativeBase"],
        filter_: FilterDict,
    ) -> tuple[IsValid, Message]:
        """Check, if passed filter is valid or not.

        Parameters
        ----------
        model : DeclarativeBase
            any declarative model. Table objects not supported.
        filter : FilterDict
            any dict with keys as strings. Can has any structure, depends on your implementation.

        Returns
        -------
        IsValid : bool
            Validation flag.
        Message: str
            Validation message. It will be passed to FilterError, if IsValid will be False. For
            IsValid equals True you may pass empty string (``""``).
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def _convert_filter(
        cls,
        model: type["DeclarativeBase"],
        filter_: FilterDict,
    ) -> Sequence[SQLAlchemyFilter]:
        """Convert given filter dict to SQLAlchemy filter.

        Parameters
        ----------
        model : DeclarativeBase
            any declarative model. Table objects not supported.
        filter : FilterDict
            any dict with keys as strings. Can has any structure, depends on your implementation.

        Returns
        -------
        Sequence[SQLAlchemyFilter]
            any sequence of ColumnElement[bool].
        """
        raise NotImplementedError

    @classmethod
    @final
    def convert(
        cls,
        model: type["DeclarativeBase"],
        filters: (
            FilterDict | ColumnElement[bool] | Sequence[FilterDict | ColumnElement[bool]] | None
        ) = None,
    ) -> Sequence[SQLAlchemyFilter]:
        """Convert input dict or list of dicts to SQLAlchemy filter.

        Depends on abstract class methods ``_is_filter_valid`` and ``_convert_filter``. Implement
        them to make your own FilterConverter class works correct.

        Final implementation. Not override it.

        Usage:

        ```
        from sqlalchemy import select

        from your_models import YourModel
        from your_db import Session

        your_filter_dicts = [{...}, {...}]
        filters = SomeFilterConverter.convert(YourModel, your_filter_dicts)

        with Session() as session:
            stmt = select(YourModel).where(*filters)
            result = session.scalars(stmt).all()
            # your other code here.
        ```
        """
        result: Sequence[SQLAlchemyFilter] = []
        if filters is None:
            return result
        if not isinstance(filters, Sequence):
            filters = [filters]
        for filter_ in filters:
            if isinstance(filter_, ColumnElement):
                result.append(filter_)
                continue
            is_valid, message = cls._is_filter_valid(model, filter_)
            if not is_valid:
                msg = f"Filter with data {filter_} is not valid: {message}"
                raise FilterError(msg)
            result.extend(cls._convert_filter(model, filter_))
        return result

    @classmethod
    @final
    def _recursive_apply_operator(
        cls,
        model: "type[DeclarativeBase]",
        field_name: str,
        parent_lookup: str,
        value: Any,  # noqa: ANN401
        rest_lookups: list[str] | None = None,
    ) -> SQLAlchemyFilter:
        """Apply operator to SQLAlchemy field and value.

        Iterate through all passed lookups and evaluate operator, represents passed lookups.
        """
        sqlalchemy_field = get_sqlalchemy_attribute(model, field_name)
        if not has_nested_lookups(cls.lookup_mapping) or not rest_lookups:
            operator_func = cls.lookup_mapping[parent_lookup]
            if isinstance(operator_func, tuple):  # pragma: no cover
                # NOTE: never situation.
                # Made it just for sure (like, if there will be only empty sets in sub-lookup).
                operator_func, *_ = operator_func
            return operator_func(sqlalchemy_field, value)
        operator_func, nested_filter_names = cls.lookup_mapping[parent_lookup]
        filter_subproduct = execute_operator_function(
            operator_func,
            sqlalchemy_field,
            value,
            subproduct_use=bool(rest_lookups),
        )
        final_lookup = rest_lookups[-1]
        # NOTE: no nested lookups with 3 level or more depth level.
        # That is why below for-loop will not be executed.
        for rest_lookup in rest_lookups[:-1]:  # pragma: no cover
            if rest_lookup not in nested_filter_names:
                msg = (
                    f'lookup "{rest_lookup}" is not supported for parent lookup "{parent_lookup}".'
                )
                raise FilterError(msg)
            parent_lookup = rest_lookup
            operator_func, nested_filter_names = cls.lookup_mapping[parent_lookup]
            filter_subproduct = execute_operator_function(
                operator_func,
                sqlalchemy_field,
                filter_subproduct,
                subproduct_use=True,
            )
        operator_func, _ = cls.lookup_mapping[final_lookup]
        return execute_operator_function(
            operator_func,
            filter_subproduct,
            value,
            subproduct_use=False,
        )


class SimpleFilterConverter(BaseFilterConverter):
    """Simple filter converter, that works with pairs ``"field"-"value"``.

    Has no specific implementation. Has only equals operator. Very simple filter.
    """

    lookup_mapping = {}  # noqa: RUF012

    @classmethod
    def _is_filter_valid(
        cls,
        model: type["DeclarativeBase"],
        filter_: FilterDict,
    ) -> tuple[IsValid, Message]:
        for field_name in filter_:
            if field_name not in get_valid_field_names(model):
                return False, f'Model or select statement {model} has no field "{field_name}".'
        return True, ""

    @classmethod
    def _convert_filter(
        cls,
        model: type["DeclarativeBase"],
        filter_: FilterDict,
    ) -> Sequence[SQLAlchemyFilter]:
        operator_func = builtin_operator.eq
        sqlalchemy_filters: Sequence[SQLAlchemyFilter] = []
        for field_name, value in filter_.items():
            sqlalchemy_field = get_sqlalchemy_attribute(model, field_name)
            sqlalchemy_filters.append(operator_func(sqlalchemy_field, value))
        return sqlalchemy_filters


class AdvancedOperatorFilterConverter(BaseFilterConverter):
    """Advanced filter with operators.

    The structure of the advanced filter is the following:

    ```
        {
            "field": "some_field_of_your_model",
            "value": "Any value of any type.",
            "operator": "== (Can one of the available (see schemas of lookup_mapping)).",
        }
    ```
    """

    lookup_mapping: ClassVar[LookupMapping] = {  # type: ignore reportIncompatibleVariableOverride
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

    @classmethod
    def _is_filter_valid(
        cls,
        model: type["DeclarativeBase"],
        filter_: FilterDict,
    ) -> tuple[IsValid, Message]:
        if not is_dict_simple_filter_dict(filter_):
            return False, "filter dict is not subtype of OperatorFilterDict."
        field = filter_["field"]
        if field not in get_valid_field_names(model):
            return False, f'Model or select statement {model} has no field "{field}".'
        return True, ""

    @classmethod
    def _convert_filter(
        cls,
        model: type["DeclarativeBase"],
        filter_: FilterDict,
    ) -> "Sequence[SQLAlchemyFilter]":
        if not is_dict_simple_filter_dict(filter_):
            msg = "Never situation. Don't use _convert_filter method directly!"
            raise FilterError(msg)
        operator_str = filter_.get("operator", "=")
        operator_func = cls.lookup_mapping[operator_str]
        sqlalchemy_field = get_sqlalchemy_attribute(model, filter_["field"])
        return [operator_func(sqlalchemy_field, filter_["value"])]


class DjangoLikeFilterConverter(BaseFilterConverter):
    """Django filters adapter for SQLAlchemy.

    Attention (1)!
    --------------
    Current implementation not supports nested models filtering like
    ``field__nested_model__nested_field__gte=25``. Don't use it, if you want full adapter of django
    filters.

    Attention (2)!
    --------------
    Not production ready. Tested only by pytest (no manual tests in other
    projects).
    """

    lookup_mapping: ClassVar[LookupMappingWithNested] = {  # type: ignore reportIncompatibleVariableOverride
        "exact": (custom_operator.django_exact, empty_nested_filter_names),
        "iexact": (custom_operator.django_iexact, empty_nested_filter_names),
        "contains": (custom_operator.django_contains, empty_nested_filter_names),
        "icontains": (custom_operator.django_icontains, empty_nested_filter_names),
        "in": (custom_operator.django_in, empty_nested_filter_names),
        "gt": (builtin_operator.gt, empty_nested_filter_names),
        "gte": (builtin_operator.ge, empty_nested_filter_names),
        "lt": (builtin_operator.lt, empty_nested_filter_names),
        "lte": (builtin_operator.le, empty_nested_filter_names),
        "startswith": (custom_operator.django_startswith, empty_nested_filter_names),
        "istartswith": (custom_operator.django_istartswith, empty_nested_filter_names),
        "endswith": (custom_operator.django_endswith, empty_nested_filter_names),
        "iendswith": (custom_operator.django_iendswith, empty_nested_filter_names),
        "range": (custom_operator.django_range, empty_nested_filter_names),
        "date": (custom_operator.django_date, django_nested_filter_names),
        "year": (custom_operator.django_year, django_nested_filter_names),
        "iso_year": (custom_operator.django_iso_year, django_nested_filter_names),
        "month": (custom_operator.django_month, django_nested_filter_names),
        "day": (custom_operator.django_day, django_nested_filter_names),
        "week": (custom_operator.django_week, django_nested_filter_names),
        "week_day": (custom_operator.django_week_day, django_nested_filter_names),
        "iso_week_day": (custom_operator.django_iso_week_day, django_nested_filter_names),
        "quarter": (custom_operator.django_quarter, django_nested_filter_names),
        "time": (custom_operator.django_time, django_nested_filter_names),
        "hour": (custom_operator.django_hour, django_nested_filter_names),
        "minute": (custom_operator.django_minute, django_nested_filter_names),
        "second": (custom_operator.django_second, django_nested_filter_names),
        "isnull": (custom_operator.django_isnull, empty_nested_filter_names),
        "regex": (custom_operator.django_regex, empty_nested_filter_names),
        "iregex": (custom_operator.django_iregex, empty_nested_filter_names),
    }

    @classmethod
    def _is_filter_valid(
        cls,
        model: type["DeclarativeBase"],
        filter_: FilterDict,
    ) -> tuple[IsValid, Message]:
        for field in filter_:
            field_parts = field.split("__")
            if len(field_parts) == 1:
                field_name = field_parts[0]
                lookup = "exact"
                rest_lookups: list[str] = []
            else:
                field_name, lookup, *rest_lookups = field_parts
            if not all(rest_lookup in cls.lookup_mapping for rest_lookup in rest_lookups):
                rest_lookups_str = ", ".join(rest_lookups)
                msg = (
                    f"Not all sub-lookups ({rest_lookups_str}) are in cls.lookup_mapping keys. "
                    "Perhaps, you tried to pass related model name to filter by it. Not it is not "
                    "possible. Use sub-lookups only for filtering inside main model (like "
                    "field__hour__gt=12 or something like this)"
                )
                raise FilterError(msg)
            if field_name not in get_valid_field_names(model):
                return False, f'Model or select statement {model} has no field "{field_name}".'
            if lookup not in cls.lookup_mapping:
                all_lookup_mapping = list(cls.lookup_mapping.keys())
                message = f'Unexpected lookup "{lookup}". Valid lookups: {all_lookup_mapping}.'
                return False, message
        return True, ""

    @classmethod
    def _convert_filter(
        cls,
        model: type["DeclarativeBase"],
        filter_: FilterDict,
    ) -> Sequence[SQLAlchemyFilter]:
        sqlalchemy_filters: Sequence[SQLAlchemyFilter] = []
        for field, value in filter_.items():
            field_parts = field.split("__")
            if len(field_parts) == 1:
                field_name = field_parts[0]
                lookup = "exact"
                rest_lookups: list[str] = []
            else:
                field_name, lookup, *rest_lookups = field_parts
            sqlalchemy_filters.append(
                cls._recursive_apply_operator(
                    model=model,
                    field_name=field_name,
                    parent_lookup=lookup,
                    value=value,
                    rest_lookups=rest_lookups,
                ),
            )
        return sqlalchemy_filters
