import os
import unittest
import numpy as np
import yaml
from polar_nexus.cryox.models.uncertainty import DeepEnsembleWrapper

class MockStochasticModel:
    def __init__(self, seed=None):
        pass
    def predict(self, x):
        # returns input + random noise. 
        # DeepEnsembleWrapper sets np.random.seed before calling predict
        return x + np.random.normal(0, 1.0, size=x.shape)

class MockDeterministicModel:
    def __init__(self):
        pass
    def predict(self, x):
        return x * 2.0

class TestDeepEnsembleWrapper(unittest.TestCase):

    def setUp(self):
        # Create a temporary seeds file for testing
        self.test_seeds_path = "test_seeds.yaml"
        with open(self.test_seeds_path, "w") as f:
            yaml.dump({"models": {"deep_ensemble": {"seeds": [10, 20, 30, 40, 50]}}}, f)

    def tearDown(self):
        if os.path.exists(self.test_seeds_path):
            os.remove(self.test_seeds_path)

    # TEST 1 - Normal valid input
    def test_normal_valid_input(self):
        wrapper = DeepEnsembleWrapper(MockStochasticModel, config_path=self.test_seeds_path)
        self.assertEqual(len(wrapper.models), 5)
        
        inputs = np.ones((10, 10))
        mean, var = wrapper.predict(inputs)
        
        self.assertEqual(mean.shape, (10, 10))
        self.assertEqual(var.shape, (10, 10))
        # Variance should be non-zero because of stochastic noise
        self.assertTrue(np.all(var > 0))

    # TEST 2 - Different valid input
    def test_different_valid_input(self):
        # Deterministic model should have 0 variance
        wrapper = DeepEnsembleWrapper(MockDeterministicModel, config_path=self.test_seeds_path)
        inputs = np.ones((5, 5))
        mean, var = wrapper.predict(inputs)
        self.assertTrue(np.all(mean == 2.0))
        self.assertTrue(np.all(var == 0.0))

    # TEST 3 - Boundary condition
    def test_boundary_condition(self):
        # Just 1 element array
        wrapper = DeepEnsembleWrapper(MockStochasticModel, config_path=self.test_seeds_path)
        inputs = np.array([5.0])
        mean, var = wrapper.predict(inputs)
        self.assertEqual(mean.shape, (1,))
        self.assertEqual(var.shape, (1,))

    # TEST 4 - Invalid/adversarial input
    def test_invalid_adversarial_input(self):
        # Bad config missing keys
        bad_config = "bad_seeds.yaml"
        with open(bad_config, "w") as f:
            yaml.dump({"models": {}}, f)
        
        with self.assertRaises(ValueError) as ctx:
            DeepEnsembleWrapper(MockStochasticModel, config_path=bad_config)
        self.assertTrue("missing" in str(ctx.exception))
        os.remove(bad_config)
        
        # Wrong number of seeds (e.g. 3 instead of 5)
        wrong_seeds = "wrong_seeds.yaml"
        with open(wrong_seeds, "w") as f:
            yaml.dump({"models": {"deep_ensemble": {"seeds": [10, 20, 30]}}}, f)
            
        with self.assertRaises(ValueError) as ctx:
            DeepEnsembleWrapper(MockStochasticModel, config_path=wrong_seeds)
        self.assertTrue("exactly N=5" in str(ctx.exception))
        os.remove(wrong_seeds)

    # TEST 5 - Edge case / failure condition
    def test_edge_case_failure(self):
        # Config file does not exist
        with self.assertRaises(FileNotFoundError):
            DeepEnsembleWrapper(MockStochasticModel, config_path="does_not_exist.yaml")

if __name__ == "__main__":
    unittest.main()
