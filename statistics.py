from time import time
from collections import namedtuple

TotalResult = namedtuple('TotalResult', 'source threads number time')


class Stats:
    """Class is responsible for statistics"""
    def __init__(self):
        """Initialize by zeros all the counters"""
        self.downloaded_files = 0
        self.downloaded_bytes = 0
        self.download_errors = 0
        self.cats_count = 0
        self.dogs_count = 0
        self.total_result = None

    def __repr__(self):
        """Representation of all statistics.

        :return: Enumeration of statistics with useful for users format."""
        total_img = self.cats_count + self.dogs_count
        return "Statistics: \n" \
               f"Downloaded files: {self.downloaded_files}\n" \
               f"Downloaded bytes: {self.downloaded_bytes}\n" \
               f"Download errors: {self.download_errors}\n" \
               f"Total images: {total_img}\n" \
               f"Cats percentage: {self.cats_count / total_img * 100 if total_img != 0 else 0.0:.2f}%\n" \
               f"Dogs percentage: {self.dogs_count / total_img * 100 if total_img != 0 else 0.0:.2f}%\n" \
               f"Total execution time with {self.total_result.source} source, {self.total_result.threads} threads " \
               f"and {self.total_result.number} elements is {self.total_result.time} seconds\n" \
               f"{'-' * 26}"

    def download_stats(self):
        """Decorator for counting of successes, bytes and errors."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                """Count results of downloading and print information about it if it has been successful."""
                try:
                    result = func(*args, **kwargs)
                except Exception:
                    self.download_errors += 1
                    result = ('', 0)
                else:
                    self.downloaded_files += 1
                    self.downloaded_bytes += result[1]
                    print(f'File {result[0]} has been downloaded with {result[1]} bytes.')
                return result
            return wrapper
        return decorator

    def classify_stats(self):
        """Decorator for counting cats and dogs."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                """Depending on the result increase count of cats or dogs."""
                result = func(*args, **kwargs)
                if bool(result):
                    self.cats_count += 1
                else:
                    self.dogs_count += 1
                return result
            return wrapper
        return decorator

    def total_time_stats(self):
        """Decorator for measuring of the total time of programme's working."""
        def decorator(func):
            def wrapper(source: str, threads: int, number: int):
                """Measure time and save it to total_time variable.

                :param source: source file with url list
                :param threads: number of threads
                :param number: number of elements to take from source
                """
                start_time = time()
                result = func(source, threads, number)
                self.total_result = TotalResult(source, threads, number, time() - start_time)
                return result
            return wrapper
        return decorator
