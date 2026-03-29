import functools
import logging

# Basic logger setup (can improve later)
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

def logging_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            logging.info(f"Calling {func.__name__}")
            logging.info(f"Args: {args[1:]}, Kwargs: {kwargs}")  # skip self

            result = func(*args, **kwargs)

            logging.info(f"{func.__name__} returned: {result}")
            return result

        except Exception as e:
            logging.error(f"Exception in {func.__name__}: {str(e)}")
            raise
        
    return wrapper