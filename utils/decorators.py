import os
from time import sleep

from django.db import connection
from django.db import reset_queries


def check_db_queries(logger=None):
    def decorator(func):
        def wrapper(*func_args, **func_kwargs):
            reset_queries()
            result = func(*func_args, **func_kwargs)
            num = f"\x1b[6;30;42m{len(connection.queries)} queries\x1b[0m"
            if logger:
                logger.info(num)
                logger.info(connection.queries)
            else:
                print(num)  # noqa: T201
                print(connection.queries)  # noqa: T201
            return result

        return wrapper

    return decorator


def delay_return(delay=5):
    if os.environ["DJANGO_SETTINGS_MODULE"] == "config.settings.test":
        delay = 0

    def decorator(func):
        def wrapper(*func_args, **func_kwargs):
            result = func(*func_args, **func_kwargs)
            sleep(delay)
            return result

        return wrapper

    return decorator
