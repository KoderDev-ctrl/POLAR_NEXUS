import os
import yaml
import numpy as np
from typing import Dict, Any, Type, Tuple

class DeepEnsembleWrapper:
    """
    Deep-ensemble uncertainty wrapper.
    Creates N=5 seeded instances per configs/seeds.yaml.
    """
    def __init__(self, model_class: Type, model_kwargs: Dict[str, Any] = None, config_path: str = None):
        if model_kwargs is None:
            model_kwargs = {}
            
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "..", "..", "configs", "seeds.yaml")
            
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Seeds config not found at {config_path}")
            
        with open(config_path, "r") as f:
            seeds_config = yaml.safe_load(f)
            
        try:
            self.seeds = seeds_config["models"]["deep_ensemble"]["seeds"]
        except KeyError:
            raise ValueError("Config file missing ['models']['deep_ensemble']['seeds'] key.")
            
        if len(self.seeds) != 5:
            # We enforce N=5 as per strict architectural spec
            raise ValueError(f"Deep ensemble must have exactly N=5 seeds, found {len(self.seeds)}")
            
        self.models = []
        for seed in self.seeds:
            # Genuine PyTorch/NumPy seeded instantiation
            import torch
            torch.manual_seed(seed)
            np.random.seed(seed)
            
            kwargs = dict(model_kwargs)
            kwargs['seed'] = seed
            try:
                model_instance = model_class(**kwargs)
            except TypeError:
                # If the model doesn't accept 'seed' explicitly in constructor
                model_instance = model_class(**model_kwargs)
                
            self.models.append(model_instance)

    def predict(self, *args, **kwargs) -> Tuple[np.ndarray, np.ndarray]:
        """
        Runs prediction on all 5 ensemble members.
        Returns:
            Tuple of (mean_prediction, variance_prediction)
        """
        predictions = []
        for i, model in enumerate(self.models):
            # Seed before each predict to ensure deterministic stochastic behavior if the stub relies on np.random
            np.random.seed(self.seeds[i])
            pred = model.predict(*args, **kwargs)
            predictions.append(pred)
            
        stacked_preds = np.stack(predictions, axis=0) # shape (5, ...)
        
        mean_pred = np.mean(stacked_preds, axis=0)
        var_pred = np.var(stacked_preds, axis=0)
        
        return mean_pred, var_pred
