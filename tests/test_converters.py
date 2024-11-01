import datetime
import zoneinfo
from typing import Any

import pytest
from sqlalchemy import Date, Time, cast, extract, func

from sqlalchemy_filter_converter import (
    AdvancedFilterConverter,
    BaseFilterConverter,
    DjangoLikeFilterConverter,
    SimpleFilterConverter,
)
from sqlalchemy_filter_converter.exc import FilterError
from tests.utils import MyModel

now = datetime.datetime.now(tz=zoneinfo.ZoneInfo("UTC"))
_date = now.date()
_date_future = now.date() + datetime.timedelta(days=1)
_time = now.time()
_time_future = (now + datetime.timedelta(hours=1)).time()


@pytest.mark.parametrize(
    ("converter_class", "filters", "expected_result"),
    [
        (
            SimpleFilterConverter,
            None,
            [],
        ),
        (
            SimpleFilterConverter,
            [MyModel.id == 25],  # noqa: PLR2004
            [str(MyModel.id == 25)],  # noqa: PLR2004
        ),
        (
            SimpleFilterConverter,
            {"id": 25, "name": "name"},
            [str(MyModel.id == 25), str(MyModel.name == "name")],  # noqa: PLR2004
        ),
        (
            SimpleFilterConverter,
            [{"id": 25}, {"name": "name"}],
            [str(MyModel.id == 25), str(MyModel.name == "name")],  # noqa: PLR2004
        ),
        (
            SimpleFilterConverter,
            {"full_name": "abc"},
            [str(MyModel.full_name == "abc")],  # type: ignore[reportUnknownMemberType]
        ),
        (
            AdvancedFilterConverter,
            [{"field": "id", "value": 25}, {"field": "name", "value": "abc"}],
            [str(MyModel.id == 25), str(MyModel.name == "abc")],  # noqa: PLR2004
        ),
        (
            AdvancedFilterConverter,
            [
                {"field": "id", "value": 25, "operator": "="},
                {"field": "id", "value": 25, "operator": ">"},
                {"field": "id", "value": 25, "operator": ">="},
                {"field": "id", "value": 25, "operator": "<"},
                {"field": "id", "value": 25, "operator": "<="},
                {"field": "id", "value": (25, 28), "operator": "between"},
                {"field": "id", "value": [1, 2, 3], "operator": "contains"},
            ],
            [
                str(MyModel.id == 25),  # noqa: PLR2004
                str(MyModel.id > 25),  # noqa: PLR2004
                str(MyModel.id >= 25),  # noqa: PLR2004
                str(MyModel.id < 25),  # noqa: PLR2004
                str(MyModel.id <= 25),  # noqa: PLR2004
                str(MyModel.id.between(25, 28)),
                str(MyModel.id.in_([1, 2, 3])),
            ],
        ),
        (
            DjangoLikeFilterConverter,
            {
                "id": 25,
                "id__exact": 25,
                "name__exact": None,
                "name__iexact": "abc",
                "name__contains": "abc",
                "name__icontains": "abc",
                "name__in": ["abc", "bca", "dce"],
                "name__startswith": "abc",
                "name__istartswith": "abc",
                "name__endswith": "abc",
                "name__iendswith": "abc",
                "id__range": [1, 2],
                "dt__date": _date,
                "dt__date__exact": _date,
                "dt__date__iexact": _date,
                "dt__date__in": [_date, _date_future],
                "dt__date__gt": _date,
                "dt__date__lt": _date,
                "dt__date__gte": _date,
                "dt__date__lte": _date,
                "dt__date__range": (_date, _date_future),
                "dt__year": 2024,
                "dt__year__exact": 2024,
                "dt__year__iexact": 2024,
                "dt__year__in": [2024, 2025],
                "dt__year__gt": 2024,
                "dt__year__lt": 2024,
                "dt__year__gte": 2024,
                "dt__year__lte": 2024,
                "dt__year__range": (2024, 2025),
                "dt__iso_year": 2025,
                "dt__iso_year__exact": 2024,
                "dt__iso_year__iexact": 2024,
                "dt__iso_year__in": [2024, 2025],
                "dt__iso_year__gt": 2024,
                "dt__iso_year__lt": 2024,
                "dt__iso_year__gte": 2024,
                "dt__iso_year__lte": 2024,
                "dt__iso_year__range": (2024, 2025),
                "dt__month": 1,
                "dt__month__exact": 1,
                "dt__month__iexact": 1,
                "dt__month__in": [1, 2],
                "dt__month__gt": 1,
                "dt__month__lt": 1,
                "dt__month__gte": 1,
                "dt__month__lte": 1,
                "dt__month__range": (1, 2),
                "dt__day": 2,
                "dt__day__exact": 2,
                "dt__day__iexact": 2,
                "dt__day__in": [2, 3],
                "dt__day__gt": 2,
                "dt__day__lt": 2,
                "dt__day__gte": 2,
                "dt__day__lte": 2,
                "dt__day__range": (2, 3),
                "dt__week": 3,
                "dt__week__exact": 3,
                "dt__week__iexact": 3,
                "dt__week__in": [3, 4],
                "dt__week__gt": 3,
                "dt__week__lt": 3,
                "dt__week__gte": 3,
                "dt__week__lte": 3,
                "dt__week__range": (3, 4),
                "dt__week_day": 4,
                "dt__week_day__exact": 4,
                "dt__week_day__iexact": 4,
                "dt__week_day__in": [4, 5],
                "dt__week_day__gt": 4,
                "dt__week_day__lt": 4,
                "dt__week_day__gte": 4,
                "dt__week_day__lte": 4,
                "dt__week_day__range": (4, 5),
                "dt__iso_week_day": 5,
                "dt__iso_week_day__exact": 5,
                "dt__iso_week_day__iexact": 5,
                "dt__iso_week_day__in": [5, 6],
                "dt__iso_week_day__gt": 5,
                "dt__iso_week_day__lt": 5,
                "dt__iso_week_day__gte": 5,
                "dt__iso_week_day__lte": 5,
                "dt__iso_week_day__range": (5, 6),
                "dt__quarter": 1,
                "dt__quarter__exact": 1,
                "dt__quarter__iexact": 1,
                "dt__quarter__in": [1, 2],
                "dt__quarter__gt": 1,
                "dt__quarter__lt": 1,
                "dt__quarter__gte": 1,
                "dt__quarter__lte": 1,
                "dt__quarter__range": (1, 2),
                "dt__time": _time,
                "dt__time__exact": _time,
                "dt__time__iexact": _time,
                "dt__time__in": [_time, _time_future],
                "dt__time__gt": _time,
                "dt__time__lt": _time,
                "dt__time__gte": _time,
                "dt__time__lte": _time,
                "dt__time__range": (_time, _time_future),
                "dt__hour": 1,
                "dt__hour__exact": 1,
                "dt__hour__iexact": 1,
                "dt__hour__in": [1, 2],
                "dt__hour__gt": 1,
                "dt__hour__lt": 1,
                "dt__hour__gte": 1,
                "dt__hour__lte": 1,
                "dt__hour__range": (1, 2),
                "dt__minute": 1,
                "dt__minute__exact": 1,
                "dt__minute__iexact": 1,
                "dt__minute__in": [1, 2],
                "dt__minute__gt": 1,
                "dt__minute__lt": 1,
                "dt__minute__gte": 1,
                "dt__minute__lte": 1,
                "dt__minute__range": (1, 2),
                "dt__second": 1,
                "dt__second__exact": 1,
                "dt__second__iexact": 1,
                "dt__second__in": [1, 2],
                "dt__second__gt": 1,
                "dt__second__lt": 1,
                "dt__second__gte": 1,
                "dt__second__lte": 1,
                "dt__second__range": (1, 2),
                "id__isnull": True,
                "name__isnull": False,
                "name__regex": "^(b|c)",
                "other_name__iregex": "^(b|c)",
            },
            [
                str(MyModel.id == 25),  # noqa: PLR2004
                str(MyModel.id == 25),  # noqa: PLR2004
                str(MyModel.name.is_(None)),
                str(MyModel.name.ilike("abc")),
                str(MyModel.name.like(r"%abc%")),
                str(MyModel.name.ilike(r"%abc%")),
                str(MyModel.name.in_(["abc", "bca", "dce"])),
                str(MyModel.name.like(r"abc%")),
                str(MyModel.name.ilike(r"abc%")),
                str(MyModel.name.like(r"%abc")),
                str(MyModel.name.ilike(r"%abc")),
                str(MyModel.id.between(1, 2)),
                str(cast(MyModel.dt, Date) == _date),
                str(cast(MyModel.dt, Date) == _date),
                str(cast(MyModel.dt, Date) == _date),
                str(cast(MyModel.dt, Date).in_([_date, _date_future])),
                str(cast(MyModel.dt, Date) > _date),
                str(cast(MyModel.dt, Date) < _date),
                str(cast(MyModel.dt, Date) >= _date),
                str(cast(MyModel.dt, Date) <= _date),
                str(cast(MyModel.dt, Date).between(_date, _date_future)),
                str(extract("year", MyModel.dt) == 2024),  # noqa: PLR2004
                str(extract("year", MyModel.dt) == 2024),  # noqa: PLR2004
                str(extract("year", MyModel.dt) == 2024),  # noqa: PLR2004
                str(extract("year", MyModel.dt).in_([2024, 2025])),
                str(extract("year", MyModel.dt) > 2024),  # noqa: PLR2004
                str(extract("year", MyModel.dt) < 2024),  # noqa: PLR2004
                str(extract("year", MyModel.dt) >= 2024),  # noqa: PLR2004
                str(extract("year", MyModel.dt) <= 2024),  # noqa: PLR2004
                str(extract("year", MyModel.dt).between(2024, 2025)),
                str(extract("isoyear", MyModel.dt) == 2025),  # noqa: PLR2004
                str(extract("isoyear", MyModel.dt) == 2025),  # noqa: PLR2004
                str(extract("isoyear", MyModel.dt) == 2025),  # noqa: PLR2004
                str(extract("isoyear", MyModel.dt).in_([2025, 2026])),
                str(extract("isoyear", MyModel.dt) > 2025),  # noqa: PLR2004
                str(extract("isoyear", MyModel.dt) < 2025),  # noqa: PLR2004
                str(extract("isoyear", MyModel.dt) >= 2025),  # noqa: PLR2004
                str(extract("isoyear", MyModel.dt) <= 2025),  # noqa: PLR2004
                str(extract("isoyear", MyModel.dt).between(2024, 2025)),
                str(extract("month", MyModel.dt) == 1),
                str(extract("month", MyModel.dt) == 1),
                str(extract("month", MyModel.dt) == 1),
                str(extract("month", MyModel.dt).in_([1, 2])),
                str(extract("month", MyModel.dt) > 1),
                str(extract("month", MyModel.dt) < 1),
                str(extract("month", MyModel.dt) >= 1),
                str(extract("month", MyModel.dt) <= 1),
                str(extract("month", MyModel.dt).between(1, 2)),
                str(extract("day", MyModel.dt) == 2),  # noqa: PLR2004
                str(extract("day", MyModel.dt) == 2),  # noqa: PLR2004
                str(extract("day", MyModel.dt) == 2),  # noqa: PLR2004
                str(extract("day", MyModel.dt).in_([2, 3])),
                str(extract("day", MyModel.dt) > 2),  # noqa: PLR2004
                str(extract("day", MyModel.dt) < 2),  # noqa: PLR2004
                str(extract("day", MyModel.dt) >= 2),  # noqa: PLR2004
                str(extract("day", MyModel.dt) <= 2),  # noqa: PLR2004
                str(extract("day", MyModel.dt).between(2, 3)),
                str(extract("week", MyModel.dt) == 3),  # noqa: PLR2004
                str(extract("week", MyModel.dt) == 3),  # noqa: PLR2004
                str(extract("week", MyModel.dt) == 3),  # noqa: PLR2004
                str(extract("week", MyModel.dt).in_([3, 4])),
                str(extract("week", MyModel.dt) > 3),  # noqa: PLR2004
                str(extract("week", MyModel.dt) < 3),  # noqa: PLR2004
                str(extract("week", MyModel.dt) >= 3),  # noqa: PLR2004
                str(extract("week", MyModel.dt) <= 3),  # noqa: PLR2004
                str(extract("week", MyModel.dt).between(3, 4)),
                str(extract("dow", MyModel.dt) == 4),  # noqa: PLR2004
                str(extract("dow", MyModel.dt) == 4),  # noqa: PLR2004
                str(extract("dow", MyModel.dt) == 4),  # noqa: PLR2004
                str(extract("dow", MyModel.dt).in_([4, 5])),
                str(extract("dow", MyModel.dt) > 4),  # noqa: PLR2004
                str(extract("dow", MyModel.dt) < 4),  # noqa: PLR2004
                str(extract("dow", MyModel.dt) >= 4),  # noqa: PLR2004
                str(extract("dow", MyModel.dt) <= 4),  # noqa: PLR2004
                str(extract("dow", MyModel.dt).between(4, 5)),
                str(extract("isodow", MyModel.dt) == 5),  # noqa: PLR2004
                str(extract("isodow", MyModel.dt) == 5),  # noqa: PLR2004
                str(extract("isodow", MyModel.dt) == 5),  # noqa: PLR2004
                str(extract("isodow", MyModel.dt).in_([5, 6])),
                str(extract("isodow", MyModel.dt) > 5),  # noqa: PLR2004
                str(extract("isodow", MyModel.dt) < 5),  # noqa: PLR2004
                str(extract("isodow", MyModel.dt) >= 5),  # noqa: PLR2004
                str(extract("isodow", MyModel.dt) <= 5),  # noqa: PLR2004
                str(extract("isodow", MyModel.dt).between(5, 6)),
                str(extract("quarter", MyModel.dt) == 1),
                str(extract("quarter", MyModel.dt) == 1),
                str(extract("quarter", MyModel.dt) == 1),
                str(extract("quarter", MyModel.dt).in_([1, 2])),
                str(extract("quarter", MyModel.dt) > 1),
                str(extract("quarter", MyModel.dt) < 1),
                str(extract("quarter", MyModel.dt) >= 1),
                str(extract("quarter", MyModel.dt) <= 1),
                str(extract("quarter", MyModel.dt).between(1, 2)),
                str(cast(MyModel.dt, Time) == _time),
                str(cast(MyModel.dt, Time) == _time),
                str(cast(MyModel.dt, Time) == _time),
                str(cast(MyModel.dt, Time).in_([_time, _time_future])),
                str(cast(MyModel.dt, Time) > _time),
                str(cast(MyModel.dt, Time) < _time),
                str(cast(MyModel.dt, Time) >= _time),
                str(cast(MyModel.dt, Time) <= _time),
                str(cast(MyModel.dt, Time).between(_time, _time_future)),
                str(extract("hour", MyModel.dt) == 1),
                str(extract("hour", MyModel.dt) == 1),
                str(extract("hour", MyModel.dt) == 1),
                str(extract("hour", MyModel.dt).in_([1, 2])),
                str(extract("hour", MyModel.dt) > 1),
                str(extract("hour", MyModel.dt) < 1),
                str(extract("hour", MyModel.dt) >= 1),
                str(extract("hour", MyModel.dt) <= 1),
                str(extract("hour", MyModel.dt).between(1, 2)),
                str(extract("minute", MyModel.dt) == 1),
                str(extract("minute", MyModel.dt) == 1),
                str(extract("minute", MyModel.dt) == 1),
                str(extract("minute", MyModel.dt).in_([1, 2])),
                str(extract("minute", MyModel.dt) > 1),
                str(extract("minute", MyModel.dt) < 1),
                str(extract("minute", MyModel.dt) >= 1),
                str(extract("minute", MyModel.dt) <= 1),
                str(extract("minute", MyModel.dt).between(1, 2)),
                str(extract("second", MyModel.dt) == 1),
                str(extract("second", MyModel.dt) == 1),
                str(extract("second", MyModel.dt) == 1),
                str(extract("second", MyModel.dt).in_([1, 2])),
                str(extract("second", MyModel.dt) > 1),
                str(extract("second", MyModel.dt) < 1),
                str(extract("second", MyModel.dt) >= 1),
                str(extract("second", MyModel.dt) <= 1),
                str(extract("second", MyModel.dt).between(1, 2)),
                str(MyModel.id.is_(None)),
                str(MyModel.name.is_not(None)),
                str(MyModel.name.regexp_match("^(b|c)")),
                str(func.lower(MyModel.other_name).regexp_match("^(b|c)")),
            ],
        ),
    ],
)
def test_converter(
    converter_class: type[BaseFilterConverter],
    filters: Any,  # noqa: ANN401
    expected_result: list[Any],
) -> None:
    converted_filters = converter_class().convert(MyModel, filters)
    if filters is not None:
        assert len(converted_filters) == len(filters)
    else:
        assert len(converted_filters) == 0
    for index, _filter in enumerate(converted_filters):
        assert str(_filter) == str(expected_result[index])


def test_simple_converter_with_specific_column_mapping() -> None:
    converted_filters = SimpleFilterConverter(
        specific_column_mapping={"my_very_cool_custom_filter_column": MyModel.id}
    ).convert(MyModel, {"my_very_cool_custom_filter_column": 25})
    assert len(converted_filters) == 1
    assert str(converted_filters[0]) == str(MyModel.id == 25)


def test_advanced_converter_with_specific_column_mapping() -> None:
    converted_filters = AdvancedFilterConverter(
        specific_column_mapping={"my_very_cool_custom_filter_column": MyModel.id}
    ).convert(MyModel, {"field": "my_very_cool_custom_filter_column", "value": 25})
    assert len(converted_filters) == 1
    assert str(converted_filters[0]) == str(MyModel.id == 25)


def test_django_like_converter_with_specific_column_mapping() -> None:
    converted_filters = DjangoLikeFilterConverter(
        specific_column_mapping={"my_very_cool_custom_filter_column": MyModel.id}
    ).convert(MyModel, {"my_very_cool_custom_filter_column__exact": 25})
    assert len(converted_filters) == 1
    assert str(converted_filters[0]) == str(MyModel.id == 25)


@pytest.mark.parametrize(
    ("converter_class", "filters"),
    [
        (
            SimpleFilterConverter,
            {"wrong_field_name": 25},
        ),
        (
            AdvancedFilterConverter,
            {"field": "wrong_field_name", "value": "abc"},
        ),
        (
            AdvancedFilterConverter,
            {"no_field_key": "wrong_field_name"},
        ),
        (
            DjangoLikeFilterConverter,
            {"id__wrong_lookup": 25},
        ),
        (
            DjangoLikeFilterConverter,
            {"dt__hour__gt__abc": 2},
        ),
        (
            DjangoLikeFilterConverter,
            {"dt_hour__wrong__gt": 2},
        ),
        (
            DjangoLikeFilterConverter,
            {"wrong_field_name__gt": 2},
        ),
    ],
)
def test_filter_not_valid(
    converter_class: type[BaseFilterConverter],
    filters: Any,  # noqa: ANN401
) -> None:
    with pytest.raises(FilterError):
        converter_class().convert(MyModel, filters)


def test_advanced_filter_never_situation() -> None:
    with pytest.raises(FilterError, match=""):
        AdvancedFilterConverter()._convert_filter(MyModel, {"abc": "abc"})  # type: ignore[reportPrivateUsage] # noqa: SLF001


def test_simple_get_lookup_mapping_error() -> None:
    with pytest.raises(
        ValueError,
        match="SimpleFilterConverter should not have any lookup mapping due to it inner logic.",
    ):
        SimpleFilterConverter()._get_lookup_mapping()
