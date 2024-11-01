from dataclasses import dataclass
from typing import TYPE_CHECKING

from sqlalchemy_filter_converter.converters.base import BaseFilterConverter
from sqlalchemy_filter_converter.exc import FilterError
from sqlalchemy_filter_converter.guards import is_dict_simple_filter_dict
from sqlalchemy_filter_converter.lookups import ADVANCED_LOOKUP_MAPPING
from sqlalchemy_filter_converter.types import IsValid, Message

if TYPE_CHECKING:
    from sqlalchemy.orm import DeclarativeBase

    from sqlalchemy_filter_converter.types import FilterDict, LookupMapping, SQLAlchemyFilter


@dataclass(kw_only=True)
class AdvancedFilterConverter(BaseFilterConverter):
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

    def _get_lookup_mapping(self) -> "LookupMapping":
        return ADVANCED_LOOKUP_MAPPING

    def _is_filter_valid(
        self,
        model: type["DeclarativeBase"],
        filter_: "FilterDict",
    ) -> tuple[IsValid, Message]:
        if not is_dict_simple_filter_dict(filter_):
            return False, "filter dict is not subtype of OperatorFilterDict."
        field_ = filter_["field"]
        if field_ not in self.get_field_names(model):
            return False, f'Model or select statement {model} has no field "{field_}".'
        return True, ""

    def _convert_filter(
        self,
        model: type["DeclarativeBase"],
        filter_: "FilterDict",
    ) -> "list[SQLAlchemyFilter]":
        lookup_mapping = self._get_lookup_mapping()
        if not is_dict_simple_filter_dict(filter_):
            msg = "Never situation. Don't use _convert_filter method directly!"
            raise FilterError(msg)
        operator_str = filter_.get("operator", "=")
        operator_func = lookup_mapping[operator_str]
        sqlalchemy_field = self.get_sqlalchemy_field(model, filter_["field"])
        return [operator_func(sqlalchemy_field, filter_["value"])]
