import operator as builtin_operator
from dataclasses import dataclass
from typing import TYPE_CHECKING

from sqlalchemy_filter_converter.converters.base import BaseFilterConverter

if TYPE_CHECKING:
    from sqlalchemy.orm import DeclarativeBase

    from sqlalchemy_filter_converter.types import (
        AnyLookupMapping,
        FilterDict,
        IsValid,
        Message,
        SQLAlchemyFilter,
    )


@dataclass(kw_only=True)
class SimpleFilterConverter(BaseFilterConverter):
    """Simple filter converter, that works with pairs ``"field"-"value"``.

    Has no specific implementation. Has only equals operator. Very simple filter.
    """

    def _get_lookup_mapping(self) -> "AnyLookupMapping":
        msg = "SimpleFilterConverter should not have any lookup mapping due to it inner logic."
        raise ValueError(msg)

    def _is_filter_valid(
        self,
        model: type["DeclarativeBase"],
        filter_: "FilterDict",
    ) -> "tuple[IsValid, Message]":
        for field_name in filter_:
            if field_name not in self.get_field_names(model=model):
                return False, f'Model or select statement {model} has no field "{field_name}".'
        return True, ""

    def _convert_filter(
        self,
        model: type["DeclarativeBase"],
        filter_: "FilterDict",
    ) -> "list[SQLAlchemyFilter]":
        operator_func = builtin_operator.eq
        sqlalchemy_filters: "list[SQLAlchemyFilter]" = []
        for field_name, value in filter_.items():
            sqlalchemy_field = self.get_sqlalchemy_field(model, field_name)
            sqlalchemy_filters.append(operator_func(sqlalchemy_field, value))
        return sqlalchemy_filters
