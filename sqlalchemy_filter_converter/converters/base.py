from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, final

from sqlalchemy import ColumnElement
from sqlalchemy_dev_utils import get_sqlalchemy_attribute, get_valid_field_names

from sqlalchemy_filter_converter.exc import FilterError
from sqlalchemy_filter_converter.guards import has_nested_lookups
from sqlalchemy_filter_converter.utils import execute_operator_function

if TYPE_CHECKING:
    from sqlalchemy.orm import DeclarativeBase, QueryableAttribute

    from sqlalchemy_filter_converter.types import (
        AnyLookupMapping,
        FilterDict,
        IsValid,
        Message,
        SQLAlchemyFilter,
    )


@dataclass(kw_only=True)
class BaseFilterConverter(ABC):
    """Base class for filter converters."""

    specific_column_mapping: "dict[str, QueryableAttribute[Any]]" = field(default_factory=dict)

    @abstractmethod
    def _get_lookup_mapping(self) -> "AnyLookupMapping":
        """Get lookup mapping by user defined mapping.

        Returns
        -------
        AnyLookupMapping : dict
            User defined lookup mapping.
        """
        raise NotImplementedError

    @abstractmethod
    def _is_filter_valid(
        self,
        model: type["DeclarativeBase"],
        filter_: "FilterDict",
    ) -> "tuple[IsValid, Message]":
        """Check, if passed filter is valid or not.

        Parameters
        ----------
        model : DeclarativeBase
            any declarative model. Table objects not supported.
        filter_ : FilterDict
            any dict with keys as strings. It may contain any structure, depends on your
            implementation.

        Returns
        -------
        IsValid : bool
            Validation flag.
        Message: str
            Validation message. It will be passed to FilterError, if IsValid will be False. For
            IsValid equals True you may pass empty string (``""``).
        """
        raise NotImplementedError

    @abstractmethod
    def _convert_filter(
        self,
        model: type["DeclarativeBase"],
        filter_: "FilterDict",
    ) -> "list[SQLAlchemyFilter]":
        """Convert given filter dict to SQLAlchemy filter.

        Parameters
        ----------
        model : DeclarativeBase
            any declarative model. Table objects not supported.
        filter_ : FilterDict
            any dict with keys as strings. It may contain any structure, depends on your
            implementation.

        Returns
        -------
        Sequence[SQLAlchemyFilter]
            any sequence of ColumnElement[bool].
        """
        raise NotImplementedError

    def get_sqlalchemy_field(
        self,
        model: type["DeclarativeBase"],
        field_name: str,
    ) -> "QueryableAttribute[Any]":
        """Get sqlalchemy field (column) or relationship object from given model.

        Include check for specific columns from init.

        Args
        ----
        model : type[DeclarativeBase]
            SQLAlchemy declarative model.
        field_name : str
            name of field to find in model.

        Returns
        -------
        QueryableAttribute[Any]
            any attribute from model, that can be used in queries.
        """
        return (
            self.specific_column_mapping[field_name]
            if field_name in self.specific_column_mapping
            else get_sqlalchemy_attribute(model, field_name)
        )

    def get_field_names(self, model: type["DeclarativeBase"]) -> set[str]:
        """Get sqlalchemy field names as strings from given model.

        Include check for specific columns from init.

        Args
        ----
        model : type[DeclarativeBase]
            SQLAlchemy declarative model.

        Returns
        -------
        set[str]
            set of model fields as strings.
        """
        return get_valid_field_names(model=model) | set(self.specific_column_mapping.keys())

    @final
    def convert(
        self,
        model: type["DeclarativeBase"],
        filters: (
            "FilterDict | ColumnElement[bool] | Sequence[FilterDict | ColumnElement[bool]] | None"
        ) = None,
    ) -> "list[SQLAlchemyFilter]":
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
        result: list[SQLAlchemyFilter] = []
        if filters is None:
            return result
        if not isinstance(filters, Sequence):
            filters = [filters]
        for filter_ in filters:
            if isinstance(filter_, ColumnElement):
                result.append(filter_)
                continue
            is_valid, message = self._is_filter_valid(model, filter_)
            if not is_valid:
                msg = f"Filter with data {filter_} is not valid: {message}"
                raise FilterError(msg)
            result.extend(self._convert_filter(model, filter_))
        return result

    @final
    def _recursive_apply_operator(
        self,
        model: "type[DeclarativeBase]",
        field_name: str,
        parent_lookup: str,
        value: Any,  # noqa: ANN401
        rest_lookups: list[str] | None = None,
    ) -> "SQLAlchemyFilter":
        """Apply operator to SQLAlchemy field and value.

        Iterate through all passed lookups and evaluate operator, represents passed lookups.
        """
        lookup_mapping = self._get_lookup_mapping()
        sqlalchemy_field = self.get_sqlalchemy_field(model=model, field_name=field_name)
        if not has_nested_lookups(lookup_mapping) or not rest_lookups:
            operator_func = lookup_mapping[parent_lookup]
            if isinstance(operator_func, tuple):  # pragma: no cover
                # NOTE: never situation.
                # Made it just for sure (like, if there will be only empty sets in sub-lookup).
                operator_func, *_ = operator_func
            return operator_func(sqlalchemy_field, value)
        operator_func, nested_filter_names = lookup_mapping[parent_lookup]
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
            operator_func, nested_filter_names = lookup_mapping[parent_lookup]
            filter_subproduct = execute_operator_function(
                operator_func,
                sqlalchemy_field,
                filter_subproduct,
                subproduct_use=True,
            )
        operator_func, _ = lookup_mapping[final_lookup]
        return execute_operator_function(
            operator_func,
            filter_subproduct,
            value,
            subproduct_use=False,
        )
