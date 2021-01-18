import numpy as np

def map(value, min, max, min_target, max_target):
    """
    :return: maps value from range [min. max] to
             range [min_target, max_target]
    """
    return ((value - min) * (max_target - min_target) /
            (max - min) + min_target)


def sign(x):
    if x >= 0:
        return 1
    else:
        return -1

