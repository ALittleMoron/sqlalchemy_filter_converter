
# SQLAlchemy filter converter

![coverage](./coverage.svg)

## For what?

I made this package to use filters from query parameters in my applications.

## Install

To install the package you need you run the following commands.

For pip:

```bash
pip install "sqlalchemy_filter_converter"
```

For poetry:

```bash
poetry add sqlalchemy_filter_converter
```

For PDM:

```bash
pdm add sqlalchemy_filter_converter
```

## Filter Types

Converters for SQLAlchemy filters. Now available 3 converters:

1. Simple filter converter (key-value with equals operator).
2. Advanced filter converter (key-value with custom operators).
3. Django filter converter (Django filters adapter with double underscore lookups).

Filters must be provided in a dict or list or dicts and will be applied sequentially.

### Simple filters

Simple filters are simle. There are `key` - `value` dicts, which converts to SQLAlchemy
filters with `==` operator.

You can use one dict with all filters, or list of dicts. There is no difference.

```python
from sqlalchemy_filter_converter import SimpleFilterConverter

filter_spec = [
    {'field_name_1': 123, 'field_name_2': 'value'},
    {'other_name_1': 'other_value', 'other_name_2': 123},
    # ...
]
```

No other specific usages presents. it is simple.

### Advanced filters

Advanced filters continues the idea of simple-filter, but add operator key.

```python
{
    "field": "my_field",
    "value": 25,
    "operator": ">",
}
```

or

```python
[
    {
        "field": "my_id_field",
        "value": [1,2,3,4,5],
        "operator": "contains",
    },
    {
        "field": "my_bool_field",
        "value": False,
        "operator": "is_not",
    },
]
```

This is the list of operators that can be used:

- `=`
- `>`
- `<`
- `>`'
- `<=`
- `is`
- `is_not`
- `between`
- `contains`

### Django filters

Django filters implements django ORM adapter for filters. You can use filters like
`my_field__iexact=25` or `my_dt_field__date__ge=datetime.date(2023, 3, 12)`. See django
documentation for more information.

Now implements all field filters, except nester relationships.

This is the list of operators that can be used:

- `exact`
- `iexact`
- `contains`
- `icontains`
- `in`
- `gt`
- `gte`
- `lt`
- `lte`
- `startswith`
- `istartswith`
- `endswith`
- `iendswith`
- `range`
- `date`
- `year`
- `iso_year`
- `month`
- `day`
- `week`
- `week_day`
- `iso_week_day`
- `quarter`
- `time`
- `hour`
- `minute`
- `second`
- `isnull`
- `regex`
- `iregex`
