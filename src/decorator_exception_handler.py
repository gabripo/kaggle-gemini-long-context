# auxiliary Python decorator to execute a function again, if its execution fails
import time


def retry_on_failure(wait_time, max_retries=5):
    def decorator_retry(func):
        def wrapper_retry(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries < max_retries:
                        print(
                            f"Function failed with error: {e}. Retrying in {wait_time} seconds... (Attempt {retries}/{max_retries})"
                        )
                        time.sleep(wait_time)
                    else:
                        print(f"Function failed after {max_retries} attempts.")
                        raise e

        return wrapper_retry

    return decorator_retry


if __name__ == "__main__":

    @retry_on_failure(wait_time=0.1)
    def err_fun(a=5):
        return a / 0

    err_fun()
