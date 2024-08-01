from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any

import pytest
from fastapi import Depends, FastAPI, status
from fastapi.testclient import TestClient
from sqlalchemy import ColumnElement, select

from sqlalchemy_filter_converter.ext.fastapi import (
    AdvancedFilterSchema,
    _convert_key_value_filters,  # type: ignore reportPrivateUsage
    advanced_converter_depends,
    django_converter_depends,
    get_advanced_filter_dicts,
    get_advanced_filters,
    get_django_filters,
    get_simple_filters,
    simple_converter_depends,
)
from tests.types import SyncFactoryFunctionProtocol
from tests.utils import MyModel

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


@pytest.fixture()
def app_with_filters():  # noqa: ANN201
    def _inner(db_sync_session: "Session") -> TestClient:
        app = FastAPI()
        my_advanced_model_filter_depends = advanced_converter_depends(MyModel)
        my_simple_model_filter_depends = simple_converter_depends(MyModel)
        my_django_model_filter_depends = django_converter_depends(MyModel)

        @app.get("/x")
        def _x(filters: list[AdvancedFilterSchema] = Depends(get_advanced_filters)):  # type: ignore reportUnusedFunction # noqa: ANN202
            return filters

        @app.get("/y")
        def _y(filters: list[dict[str, Any]] = Depends(get_advanced_filter_dicts)):  # type: ignore reportUnusedFunction # noqa: ANN202
            return filters

        @app.get("/z")
        def _z(  # noqa: ANN202 # type: ignore reportUnusedFunction
            filters: Sequence[ColumnElement[bool]] = Depends(my_advanced_model_filter_depends),
        ):
            stmt = select(MyModel).where(*filters)
            return [item.as_dict() for item in db_sync_session.scalars(stmt).all()]

        @app.get("/simple")
        def _simple(filters: list[dict[str, Any]] = Depends(get_simple_filters)):  # type: ignore reportUnusedFunction # noqa: ANN202
            return filters

        @app.get("/django")
        def _django(filters: list[dict[str, Any]] = Depends(get_django_filters)):  # type: ignore reportUnusedFunction # noqa: ANN202
            return filters

        @app.get("/simple-query")
        def _simple_query(  # type: ignore reportUnusedFunction # noqa: ANN202
            filters: Sequence[ColumnElement[bool]] = Depends(my_simple_model_filter_depends),
        ):
            stmt = select(MyModel).where(*filters)
            return [item.as_dict() for item in db_sync_session.scalars(stmt).all()]

        @app.get("/django-query")
        def _django_query(  # type: ignore reportUnusedFunction # noqa: ANN202
            filters: Sequence[ColumnElement[bool]] = Depends(my_django_model_filter_depends),
        ):
            stmt = select(MyModel).where(*filters)
            return [item.as_dict() for item in db_sync_session.scalars(stmt).all()]

        return TestClient(app)

    return _inner


def test_get_advanced_filters(
    db_sync_session: "Session",
    app_with_filters: Callable[["Session"], TestClient],
) -> None:
    app = app_with_filters(db_sync_session)
    response = app.get("/x", params={"filters": '{"field": "id", "value": 1}'})
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == [{"field": "id", "value": 1, "operator": "="}]
    response = app.get(
        "/x",
        params={"filters": '[{"field": "id", "value": 1}, {"field": "name", "value": "name"}]'},
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == [
        {"field": "id", "value": 1, "operator": "="},
        {"field": "name", "value": "name", "operator": "="},
    ]
    response = app.get("/x")
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == []


def test_test_get_advanced_filters_validation_error(
    db_sync_session: "Session",
    app_with_filters: Callable[["Session"], TestClient],
) -> None:
    app = app_with_filters(db_sync_session)
    response = app.get("/x", params={"filters": '{"value": 1}'})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.json()
    response = app.get(
        "/x",
        params={"filters": '[{"field": "id"}]'},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.json()


def test_get_advanced_filter_dicts(
    db_sync_session: "Session",
    app_with_filters: Callable[["Session"], TestClient],
) -> None:
    app = app_with_filters(db_sync_session)
    response = app.get("/y", params={"filters": '{"field": "id", "value": 1, "operator": ">="}'})
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == [{"field": "id", "value": 1, "operator": ">="}]
    response = app.get(
        "/y",
        params={
            "filters": (
                '[{"field": "id", "value": 1, "operator": ">="},'
                '{"field": "name", "value": "name", "operator": "="}]'
            ),
        },
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == [
        {"field": "id", "value": 1, "operator": ">="},
        {"field": "name", "value": "name", "operator": "="},
    ]


def test_advanced_converter_depends(
    db_sync_session: "Session",
    app_with_filters: Callable[["Session"], TestClient],
    mymodel_sync_factory: SyncFactoryFunctionProtocol[MyModel],
) -> None:
    instance = mymodel_sync_factory(db_sync_session)
    app = app_with_filters(db_sync_session)
    response = app.get(
        "/z",
        params={"filters": f'{{"field": "id", "value": {instance.id}, "operator": "="}}'},
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    response_list = response.json()
    assert isinstance(response_list, list)
    assert len(response_list) == 1  # type: ignore reportUnknownArgumentType
    assert 'id' in response_list[0]
    assert response_list[0]['id'] == instance.id


def test_get_simple_filters(
    db_sync_session: "Session",
    app_with_filters: Callable[["Session"], TestClient],
) -> None:
    app = app_with_filters(db_sync_session)
    response = app.get(
        "/simple",
        params={"filters": '{"id": 25, "name": "name"}'},
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == [{"id": 25, "name": "name"}]
    response = app.get(
        "/simple",
        params={"filters": '[{"id": 25, "name": "name"}, {"id": 26, "name": "other_name"}]'},
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == [{"id": 25, "name": "name"}, {"id": 26, "name": "other_name"}]


def test_get_simple_filters_validation_error(
    db_sync_session: "Session",
    app_with_filters: Callable[["Session"], TestClient],
) -> None:
    app = app_with_filters(db_sync_session)
    response = app.get(
        "/simple",
        params={"filters": '[12, 25, 26]'},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.json()
    response = app.get(
        "/simple",
        params={"filters": '"string"'},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.json()
    response = app.get(
        "/simple",
        params={"filters": '25'},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.json()


def test_get_django_filters(
    db_sync_session: "Session",
    app_with_filters: Callable[["Session"], TestClient],
) -> None:
    app = app_with_filters(db_sync_session)
    response = app.get(
        "/django",
        params={"filters": '{"id": 25, "name": "name"}'},
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == [{"id": 25, "name": "name"}]
    response = app.get(
        "/django",
        params={"filters": '[{"id": 25, "name": "name"}, {"id": 26, "name": "other_name"}]'},
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == [{"id": 25, "name": "name"}, {"id": 26, "name": "other_name"}]


def test_get_django_filters_validation_error(
    db_sync_session: "Session",
    app_with_filters: Callable[["Session"], TestClient],
) -> None:
    app = app_with_filters(db_sync_session)
    response = app.get(
        "/django",
        params={"filters": '[12, 25, 26]'},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.json()
    response = app.get(
        "/django",
        params={"filters": '"string"'},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.json()
    response = app.get(
        "/django",
        params={"filters": '25'},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.json()


def test_simple_converter_depends(
    db_sync_session: "Session",
    app_with_filters: Callable[["Session"], TestClient],
    mymodel_sync_factory: SyncFactoryFunctionProtocol[MyModel],
) -> None:
    instance = mymodel_sync_factory(db_sync_session)
    app = app_with_filters(db_sync_session)
    response = app.get(
        "/simple-query",
        params={"filters": f'{{"id": {instance.id}}}'},
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    response_list = response.json()
    assert isinstance(response_list, list)
    assert len(response_list) == 1  # type: ignore reportUnknownArgumentType
    assert 'id' in response_list[0]
    assert response_list[0]['id'] == instance.id


def test_django_converter_depends(
    db_sync_session: "Session",
    app_with_filters: Callable[["Session"], TestClient],
    mymodel_sync_factory: SyncFactoryFunctionProtocol[MyModel],
) -> None:
    instance = mymodel_sync_factory(db_sync_session)
    other_instance = mymodel_sync_factory(db_sync_session)
    ids = {instance.id, other_instance.id}
    app = app_with_filters(db_sync_session)
    response = app.get(
        "/django-query",
        params={"filters": f'{{"id": {instance.id}}}'},
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    response_list = response.json()
    assert isinstance(response_list, list)
    assert len(response_list) == 1  # type: ignore reportUnknownArgumentType
    assert 'id' in response_list[0]
    assert response_list[0]['id'] == instance.id
    response = app.get(
        "/django-query",
        params={"filters": f'{{"id__in": [{instance.id},{other_instance.id}]}}'},
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    response_list = response.json()
    assert isinstance(response_list, list)
    assert len(response_list) == 2  # type: ignore reportUnknownArgumentType  # noqa: PLR2004
    for ele in response_list:  # type: ignore reportUnknownArgumentType
        assert 'id' in ele
        assert ele['id'] in ids


def test_convert_key_value_filters_is_none() -> None:
    assert _convert_key_value_filters(None) == []
