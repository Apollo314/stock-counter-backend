from _thread import RLock
from typing import Any, Callable, Type 
import warnings

from django.core.cache import cache
from functools import cached_property

_NOT_FOUND = object()


def generate_cache_name(cls: Type, property: str, pk: str | int) -> str:
    prefix = f"{cls.__module__}.{cls.__name__}"
    return f"{prefix}:{property}:{pk}"


class PersistentCachedProperty:
    def __init__(self, func: Callable, timeout: int = 300):
        self.func = func
        self.timeout = timeout
        self.attrname = None
        self.__doc__ = func.__doc__
        self.lock = RLock()

    @property
    def cache_name(self):
        cls = self.instance.__class__
        return generate_cache_name(cls=cls, property=self.attrname, pk=self.instance.pk)

    def set_dcache(self, value: Any):
        try:
            self.instance.__dict__[self.attrname] = value
        except TypeError:
            msg = (
                f"The '__dict__' attribute on {type(self.instance).__name__!r} instance "
                f"does not support item assignment for caching {self.attrname!r} property."
            )
            raise TypeError(msg) from None

    def __set_name__(self, owner, name):
        if self.attrname is None:
            self.attrname = name
        elif name != self.attrname:
            raise TypeError(
                "Cannot assign the same cached_property to two different names "
                f"({self.attrname!r} and {name!r})."
            )

    def __set__(self, instance, value):
        self.instance = instance
        if value is None:
            try:
                cache.delete(self.cache_name)
                del instance.__dict__[self.attrname]
            except KeyError:
                pass
        else:
            cache.set(self.cache_name, value, timeout=self.timeout)
            instance.__dict__[self.attrname] = value

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        else:
            self.instance = instance
        if self.attrname is None:
            raise TypeError(
                "Cannot use cached_property instance without calling __set_name__ on it."
            )
        try:
            dcache = instance.__dict__
        except AttributeError:  # not all objects have __dict__ (e.g. class defines slots)
            msg = (
                f"No '__dict__' attribute on {type(instance).__name__!r} "
                f"instance to cache {self.attrname!r} property."
            )
            raise TypeError(msg) from None
        val = dcache.get(self.attrname, _NOT_FOUND)
        if val is _NOT_FOUND:
            with self.lock:
                # check if another thread filled cache while we awaited lock
                val = dcache.get(self.attrname, _NOT_FOUND)
                if val is _NOT_FOUND:
                    val = cache.get(self.cache_name, _NOT_FOUND)
                if val is _NOT_FOUND:
                    val = self.func(instance)
                    cache.set(self.cache_name, val, timeout=self.timeout)
                if val is not _NOT_FOUND:
                    self.set_dcache(val)
        return val


def persistent_cached_property(func: Callable = None, *, timeout: int = 300):
    if func and callable(func):
        # return cached_property(func)
        return PersistentCachedProperty(func)
    else:

        def decorator(f):
            # return cached_property(f)
            return PersistentCachedProperty(f, timeout=timeout)

        return decorator
