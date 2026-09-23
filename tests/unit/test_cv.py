import unittest
from polar_nexus.cryox.models.validation import WalkForwardCV

class TestWalkForwardCV(unittest.TestCase):
    def setUp(self):
        self.data = list(range(10)) # [0, 1, 2, ..., 9]

    # TEST 1 - Normal valid input
    def test_normal_valid_input(self):
        cv = WalkForwardCV(train_window_size=3, test_window_size=2, step_size=1)
        folds = cv.split(self.data)
        
        # Expected:
        # F1: Train [0,1,2], Test [3,4]
        # F2: Train [1,2,3], Test [4,5]
        # F3: Train [2,3,4], Test [5,6]
        # F4: Train [3,4,5], Test [6,7]
        # F5: Train [4,5,6], Test [7,8]
        # F6: Train [5,6,7], Test [8,9]
        self.assertEqual(len(folds), 6)
        self.assertEqual(folds[0], ([0,1,2], [3,4]))
        self.assertEqual(folds[-1], ([5,6,7], [8,9]))

    # TEST 2 - Different valid input (larger step size)
    def test_different_valid_input(self):
        cv = WalkForwardCV(train_window_size=3, test_window_size=2, step_size=2)
        folds = cv.split(self.data)
        
        # F1: Train [0,1,2], Test [3,4]
        # F2: Train [2,3,4], Test [5,6]
        # F3: Train [4,5,6], Test [7,8]
        self.assertEqual(len(folds), 3)
        self.assertEqual(folds[1], ([2,3,4], [5,6]))

    # TEST 3 - Boundary condition
    def test_boundary_condition(self):
        cv = WalkForwardCV(train_window_size=5, test_window_size=5, step_size=1)
        folds = cv.split(self.data)
        
        # Exactly one fold fits
        self.assertEqual(len(folds), 1)
        self.assertEqual(folds[0], ([0,1,2,3,4], [5,6,7,8,9]))

    # TEST 4 - Adversarial input
    def test_invalid_adversarial_input(self):
        cv = WalkForwardCV(train_window_size=8, test_window_size=3) # Sum = 11 > len(data)
        with self.assertRaises(ValueError):
            cv.split(self.data)
            
        cv2 = WalkForwardCV(train_window_size=5, test_window_size=5)
        with self.assertRaises(ValueError):
            cv2.split([]) # Empty data

    # TEST 5 - Edge case / failure condition (Negative / zero inputs handled safely? Well, Python slices handle it, but it's logically invalid)
    def test_edge_case_failure(self):
        cv = WalkForwardCV(train_window_size=0, test_window_size=2, step_size=1)
        # Assuming training size must logically be > 0 in a real scenario, but based on code it returns empty list for train.
        folds = cv.split(self.data)
        self.assertEqual(folds[0][0], [])
        self.assertEqual(folds[0][1], [0,1])

if __name__ == "__main__":
    unittest.main()
