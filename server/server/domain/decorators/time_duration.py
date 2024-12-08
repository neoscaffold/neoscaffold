from time import perf_counter


# This is a decorator function that will print the runtime of the decorated function.
def time_duration(label):
    def inner(func):
        """Print the runtime of the decorated function."""

        def wrap_func(*args, **kwargs):
            """Wrap the function"""
            t1 = perf_counter()
            result = func(*args, **kwargs)
            t2 = perf_counter()
            print(f"{label} {(t2 - t1) * 1000:.4f}ms")
            return result

        return wrap_func

    return inner
