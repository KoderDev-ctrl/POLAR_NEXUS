import numpy as np
from typing import List, Tuple, Any

class WalkForwardCV:
    """
    Implements a walk-forward cross-validation protocol for time-series ML models
    to prevent data leakage (Item 21).
    """
    def __init__(self, train_window_size: int, test_window_size: int, step_size: int = 1):
        self.train_window_size = train_window_size
        self.test_window_size = test_window_size
        self.step_size = step_size

    def split(self, data: List[Any]) -> List[Tuple[List[Any], List[Any]]]:
        """
        Splits data into a list of (train_fold, test_fold) tuples.
        """
        n = len(data)
        if n < self.train_window_size + self.test_window_size:
            raise ValueError("Data too short for even one fold.")

        folds = []
        start = 0
        while start + self.train_window_size + self.test_window_size <= n:
            train_end = start + self.train_window_size
            test_end = train_end + self.test_window_size

            train_fold = data[start:train_end]
            test_fold = data[train_end:test_end]

            folds.append((train_fold, test_fold))
            
            start += self.step_size

        return folds
