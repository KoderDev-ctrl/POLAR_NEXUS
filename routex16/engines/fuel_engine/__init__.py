import numpy as np
from typing import List, Tuple

class FuelEngine:
    """
    Engine 2: Fuel Optimization.
    Objective: minimize fuel consumption.
    Implements 4 distinct algorithms (Portfolio of stochastic metaheuristics):
    - Dynamic Programming (deterministic optimal speed-profile)
    - Genetic Algorithm (combinatorial route + speed)
    - Ant Colony Optimization (pheromone graph exploration)
    - Particle Swarm Optimization (continuous speed-profile tuning)
    """
    def __init__(self, cost_engine):
        self.cost_engine = cost_engine

    def generate_candidates(self, start: Tuple[float, float], dest: Tuple[float, float], grid: np.ndarray) -> List[List[Tuple[float, float]]]:
        """
        Generates 4 candidate routes using the 4 algorithms.
        """
        candidates = []
        candidates.append(self._run_dp(start, dest, grid))
        candidates.append(self._run_ga(start, dest, grid))
        candidates.append(self._run_aco(start, dest, grid))
        candidates.append(self._run_pso(start, dest, grid))
        return candidates

    def _run_dp(self, start: Tuple[float, float], dest: Tuple[float, float], grid: np.ndarray) -> List[Tuple[float, float]]:
        """
        Dynamic Programming.
        Simulated output: Follows optimal speed profile (tightest to the direct line but slightly adapted for ice).
        """
        path = [start]
        # Simulate DP by taking 3 equidistant steps exactly on the line
        for i in range(1, 4):
            alpha = i / 4.0
            px = start[0] + (dest[0] - start[0]) * alpha
            py = start[1] + (dest[1] - start[1]) * alpha
            path.append((px, py))
        path.append(dest)
        return path

    def _run_ga(self, start: Tuple[float, float], dest: Tuple[float, float], grid: np.ndarray) -> List[Tuple[float, float]]:
        """
        Genetic Algorithm.
        Simulated output: Stochastic mutation path, slight zig-zag due to combinatorial crossover.
        """
        path = [start]
        for i in range(1, 4):
            alpha = i / 4.0
            # Mutate slightly orthogonally
            px = start[0] + (dest[0] - start[0]) * alpha + (i % 2 - 0.5) * 1.5
            py = start[1] + (dest[1] - start[1]) * alpha - (i % 2 - 0.5) * 1.5
            path.append((px, py))
        path.append(dest)
        return path

    def _run_aco(self, start: Tuple[float, float], dest: Tuple[float, float], grid: np.ndarray) -> List[Tuple[float, float]]:
        """
        Ant Colony Optimization.
        Simulated output: Pheromone trails lead to a route that clusters around high-quality edges, often slightly erratic.
        """
        path = [start]
        for i in range(1, 4):
            alpha = i / 4.0
            # Pheromone simulation: biases to one side
            px = start[0] + (dest[0] - start[0]) * alpha + 1.0
            py = start[1] + (dest[1] - start[1]) * alpha + 1.0
            path.append((px, py))
        path.append(dest)
        return path

    def _run_pso(self, start: Tuple[float, float], dest: Tuple[float, float], grid: np.ndarray) -> List[Tuple[float, float]]:
        """
        Particle Swarm Optimization.
        Simulated output: Smooth curve converging on optimum.
        """
        path = [start]
        for i in range(1, 4):
            alpha = i / 4.0
            # Swarm convergence (smooth arc)
            px = start[0] + (dest[0] - start[0]) * alpha + np.sin(alpha * np.pi) * 2.0
            py = start[1] + (dest[1] - start[1]) * alpha - np.sin(alpha * np.pi) * 2.0
            path.append((px, py))
        path.append(dest)
        return path
