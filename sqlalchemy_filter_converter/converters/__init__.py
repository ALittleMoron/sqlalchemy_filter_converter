"""Converter package.

Contains base converter and 3 implementations:

1) simple filter - filter with key-value format. (``key - field`` equals to ``value``)
2) advanced filter - key-value filter with additional operator (what to do with value for given
key).
3) django filter - django-sqlalchemy filter adapter.
"""

from .advanced import AdvancedFilterConverter as AdvancedFilterConverter
from .base import BaseFilterConverter as BaseFilterConverter
from .django import DjangoLikeFilterConverter as DjangoLikeFilterConverter
from .simple import SimpleFilterConverter as SimpleFilterConverter
