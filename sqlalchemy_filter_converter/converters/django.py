from dataclasses import dataclass
from typing import TYPE_CHECKING

from sqlalchemy_filter_converter.converters.base import BaseFilterConverter
from sqlalchemy_filter_converter.exc import FilterError
from sqlalchemy_filter_converter.lookups import DJANGO_LIKE_LOOKUP_MAPPING

if TYPE_CHECKING:
    from sqlalchemy.orm import DeclarativeBase

    from sqlalchemy_filter_converter.types import (
        FilterDict,
        IsValid,
        LookupMappingWithNested,
        Message,
        SQLAlchemyFilter,
    )


@dataclass(kw_only=True)
class DjangoLikeFilterConverter(BaseFilterConverter):
    """Django filters adapter for SQLAlchemy.

    Attention (1)!
    --------------
    Current implementation not supports nested models filtering like
    ``field__nested_model__nested_field__gte=25``. Don't use it, if you want full adapter of django
    filters.
    """

    def _get_lookup_mapping(self) -> "LookupMappingWithNested":
        return DJANGO_LIKE_LOOKUP_MAPPING

    def _is_filter_valid(
        self,
        model: type["DeclarativeBase"],
        filter_: "FilterDict",
    ) -> "tuple[IsValid, Message]":
        lookup_mapping = self._get_lookup_mapping()
        for field_ in filter_:
            field_parts = field_.split("__")
            if len(field_parts) == 1:
                field_name = field_parts[0]
                lookup = "exact"
                rest_lookups: list[str] = []
            else:
                field_name, lookup, *rest_lookups = field_parts
            if not all(rest_lookup in lookup_mapping for rest_lookup in rest_lookups):
                rest_lookups_str = ", ".join(rest_lookups)
                msg = (
                    f"Not all sub-lookups ({rest_lookups_str}) are in cls.lookup_mapping keys. "
                    "Perhaps, you tried to pass related model name to filter by it. Not it is not "
                    "possible. Use sub-lookups only for filtering inside main model (like "
                    "field__hour__gt=12 or something like this)"
                )
                raise FilterError(msg)
            if field_name not in self.get_field_names(model):
                return False, f'Model or select statement {model} has no field "{field_name}".'
            if lookup not in lookup_mapping:
                all_lookup_mapping = list(lookup_mapping.keys())
                message = f'Unexpected lookup "{lookup}". Valid lookups: {all_lookup_mapping}.'
                return False, message
        return True, ""

    def _convert_filter(
        self,
        model: type["DeclarativeBase"],
        filter_: "FilterDict",
    ) -> "list[SQLAlchemyFilter]":
        sqlalchemy_filters: "list[SQLAlchemyFilter]" = []
        for field, value in filter_.items():
            field_parts = field.split("__")
            if len(field_parts) == 1:
                field_name = field_parts[0]
                lookup = "exact"
                rest_lookups: list[str] = []
            else:
                field_name, lookup, *rest_lookups = field_parts
            sqlalchemy_filters.append(
                self._recursive_apply_operator(
                    model=model,
                    field_name=field_name,
                    parent_lookup=lookup,
                    value=value,
                    rest_lookups=rest_lookups,
                ),
            )
        return sqlalchemy_filters
