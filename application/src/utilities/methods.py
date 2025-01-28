import time
import functools 
import pandas as pd

def timer(func):
    """Print the runtime of the decorated function"""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()  # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()  # 2
        run_time = end_time - start_time  # 3
        print(" ====> Duration {:.2f} secs: {}".format(run_time, func.__doc__))
        return value

    return wrapper_timer 

# @timer
def count_plz_occurrences(df_lstat2, sort_col=("PLZ")):
    """Counts loading stations per PLZ"""
    # Group by PLZ and count occurrences, keeping geometry
    result_df = df_lstat2.groupby(sort_col).agg(
        Number=('KW', 'count'),
        geometry=('geometry', 'first')
    ).reset_index()
    
    return result_df