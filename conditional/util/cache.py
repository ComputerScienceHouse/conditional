from functools import lru_cache

cached_functions = []


def service_cache(*args, **kwargs):
    def decorator(func):
        func = lru_cache(*args, **kwargs)(func)
        cached_functions.append(func)
        return func

    return decorator


def clear_all_cached_functions():
    for func in cached_functions:
        func.cache_clear()
