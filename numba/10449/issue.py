import numba
import functools

cache_histogramms = {}

def perf(name=None):
    def actual_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            histo_name = name or func.__name__
            if name not in cache_histogramms:
                cache_histogramms[histo_name] = _meter.create_counter(
                    name=name,
                    description=f"Duration {name} in seconds.",
                    unit="s",
                )

            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            duration = time.perf_counter() - start_time
            cache_histogramms[histo_name].add(duration)

            return result

        return wrapper

    return actual_decorator

@perf("repo_generate_agent_matches")
@numba.jit()
def some_function():
      print("some_function")

some_function()
