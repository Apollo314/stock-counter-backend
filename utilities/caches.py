from typing import Callable

from django.core.cache import cache


class PersistentCachedProperty:
    """
    Decorator that converts a method with a single self argument into a
    property cached on cache backend.
    set property to None to delete the cache.

    A cached property can be made out of an existing method:
    (e.g. ``url = persistent_cached_property(get_absolute_url)``).
    """

    def cache_name(self, instance):
        cls = instance.__class__
        prefix = f"{cls.__module__}.{cls.__name__}"
        return f"{prefix}:{self.name}:{instance.pk}"

    def set_instance_cache(self, instance, value):
        """will be deleted with instance. not using caching backend."""
        instance.__dict__[self.name] = value

    def set_cache(self, instance, value):
        """
        will persist even if instance is deleted on cache backend
        depending on timeout setting
        """
        cache.set(self.cache_name(instance), value, timeout=self.timeout)

    def __set__(self, instance, value):
        if value is None:
            cache.delete(self.cache_name(instance))
            del instance.__dict__[self.name]
        else:
            self.set_cache(instance, value)
            self.set_instance_cache(instance, value)

    @staticmethod
    def func(instance):
        ...

    def __init__(self, func, timeout=None):
        self.real_func = func
        self.timeout = timeout
        self.__doc__ = getattr(func, "__doc__")
        self._cache_name = None

    def __set_name__(self, owner, name):
        self.name = name
        self.func = self.real_func

    def __get__(self, instance, cls=None):
        """
        Try to get cache from cache backend, if not possible, call the function
        and put the return value in both cache backend and instance.__dict__ so
        that subsequent attribute access on the instance returns the cached value
        from either cache backend or if called from the same instance from the
        instance.__dict__ instead of calling persistent_cached_property.__get__().
        """
        if instance is None:
            return self
        cache_name = self.cache_name(instance)
        if cached_value := cache.get(cache_name):
            self.set_instance_cache(instance, cached_value)
            return cached_value
        else:
            value = self.func(instance)
            self.set_instance_cache(instance, value)
            self.set_cache(instance, value)
            return value


def persistent_cached_property(func: Callable = None, *, timeout: int = None):
    if func and callable(func):
        return PersistentCachedProperty(func)
    else:

        def decorator(f):
            return PersistentCachedProperty(f, timeout=timeout)

        return decorator
