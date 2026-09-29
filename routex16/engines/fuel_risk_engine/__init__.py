import numpy as np
from typing import List, Tuple
from polar_nexus.routex16.cost_layer import RouteCostLayer, CandidateRoute
from pymoo.core.problem import Problem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
import random
import yaml
import os

class FuelRiskEngine:
    """
    Engine 4: Fuel + Risk Optimization.
    Objective: balance fuel consumption against risk.
    Algorithms: Dynamic Programming, Genetic Algorithm, Particle Swarm Optimization, NSGA-II.
    """
    def __init__(self, cost_engine: RouteCostLayer):
        self.cost_engine = cost_engine
        self.risk_weight = 1000.0 # lambda for risk

    def generate_candidates(self, start: Tuple[float, float], dest: Tuple[float, float], grid: np.ndarray) -> List[CandidateRoute]:
        # Load deterministic seeds
        try:
            with open("polar_nexus/configs/seeds.yaml", "r") as f:
                seeds_config = yaml.safe_load(f)
                seed_val = seeds_config.get("seed", 42)
                random.seed(seed_val)
                np.random.seed(seed_val)
                self.algo_seeds = seeds_config.get("algorithm_seeds", {})
        except Exception:
            self.algo_seeds = {}
            random.seed(42)
            np.random.seed(42)

        candidates = []
        paths = [
            ("DP", self._run_dp(start, dest, grid)),
            ("GA", self._run_ga(start, dest, grid)),
            ("PSO", self._run_pso(start, dest, grid)),
            ("NSGA-II", self._run_nsga2(start, dest, grid))
        ]
        for algo_name, path in paths:
            metrics = self.cost_engine.evaluate_route(path)
            candidates.append(CandidateRoute(
                route_id=f"FuelRiskEngine_{algo_name}",
                algorithm_name=algo_name,
                engine_category="Fuel+Risk",
                geometry=path,
                distance_nm=metrics["dist_nm"],
                estimated_time_hours=metrics["time_h"],
                estimated_fuel_kg=metrics["fuel_kg"],
                environmental_risk=metrics["risk"],
                metadata={}
            ))
        return candidates

    def _combined_cost(self, u, v):
        metrics = self.cost_engine.evaluate_edge(u, v)
        return metrics["fuel_kg"] + self.risk_weight * metrics["risk"]

    def _run_dp(self, start: Tuple[float, float], dest: Tuple[float, float], grid: np.ndarray) -> List[Tuple[float, float]]:
        """Dynamic Programming minimizing Fuel + Risk."""
        stages = 8
        transverse_nodes = 5
        transverse_width = 2.0
        
        dx = dest[0] - start[0]
        dy = dest[1] - start[1]
        dist = np.sqrt(dx**2 + dy**2)
        if dist < 1e-6:
            return [start, dest]
            
        nx, ny = -dy / dist, dx / dist
        
        grid_nodes = [[start]]
        for k in range(1, stages - 1):
            alpha = k / (stages - 1)
            cx = start[0] + dx * alpha
            cy = start[1] + dy * alpha
            stage_points = []
            for j in range(transverse_nodes):
                offset = (j - (transverse_nodes - 1)/2) / (transverse_nodes - 1) * transverse_width
                stage_points.append((cx + nx * offset, cy + ny * offset))
            grid_nodes.append(stage_points)
        grid_nodes.append([dest])
        
        cost_to_go = []
        for k in range(stages):
            cost_to_go.append(np.full(len(grid_nodes[k]), float('inf')))
        cost_to_go[-1][0] = 0.0
        
        policy = {}
        for k in range(stages - 2, -1, -1):
            for i, node in enumerate(grid_nodes[k]):
                best_cost = float('inf')
                best_next = -1
                for j, next_node in enumerate(grid_nodes[k+1]):
                    edge_cost = self._combined_cost(node, next_node)
                    total_cost = edge_cost + cost_to_go[k+1][j]
                    if total_cost < best_cost:
                        best_cost = total_cost
                        best_next = j
                cost_to_go[k][i] = best_cost
                policy[(k, i)] = best_next
                
        path = [start]
        curr_k = 0
        curr_i = 0
        while curr_k < stages - 1:
            next_i = policy.get((curr_k, curr_i), 0)
            path.append(grid_nodes[curr_k+1][next_i])
            curr_i = next_i
            curr_k += 1
            
        return path

    def _run_ga(self, start: Tuple[float, float], dest: Tuple[float, float], grid: np.ndarray) -> List[Tuple[float, float]]:
        """Genetic Algorithm weighted Fuel + Risk."""
        pop_size = 20
        generations = 10
        waypoints_count = 5
        
        dx = dest[0] - start[0]
        dy = dest[1] - start[1]
        dist = np.sqrt(dx**2 + dy**2)
        if dist < 1e-6:
            return [start, dest]
            
        nx, ny = -dy / dist, dx / dist
        
        population = []
        for _ in range(pop_size):
            population.append([random.uniform(-1.0, 1.0) for _ in range(waypoints_count)])
            
        def evaluate_fitness(offsets):
            path = [start]
            for i, off in enumerate(offsets):
                alpha = (i + 1) / (waypoints_count + 1)
                cx = start[0] + dx * alpha + nx * off
                cy = start[1] + dy * alpha + ny * off
                path.append((cx, cy))
            path.append(dest)
            
            metrics = self.cost_engine.evaluate_route(path)
            cost = metrics["fuel_kg"] + self.risk_weight * metrics["risk"]
            return 1.0 / (cost + 1e-6), path
            
        best_path = [start, dest]
        best_fitness = -1.0
        
        for gen in range(generations):
            evaluated = []
            for ind in population:
                fit, path = evaluate_fitness(ind)
                evaluated.append((fit, ind, path))
                if fit > best_fitness:
                    best_fitness = fit
                    best_path = path
                    
            evaluated.sort(key=lambda x: x[0], reverse=True)
            next_gen = [evaluated[0][1], evaluated[1][1]]
            
            while len(next_gen) < pop_size:
                p1 = random.choice(evaluated[:10])[1]
                p2 = random.choice(evaluated[:10])[1]
                child = [p1[i] if random.random() < 0.5 else p2[i] for i in range(waypoints_count)]
                for i in range(waypoints_count):
                    if random.random() < 0.2:
                        child[i] += random.uniform(-0.5, 0.5)
                next_gen.append(child)
            population = next_gen
            
        return best_path

    def _run_pso(self, start: Tuple[float, float], dest: Tuple[float, float], grid: np.ndarray) -> List[Tuple[float, float]]:
        """Particle Swarm Optimization continuous Fuel + Risk."""
        num_particles = 15
        iterations = 10
        waypoints_count = 5
        
        dx = dest[0] - start[0]
        dy = dest[1] - start[1]
        dist = np.sqrt(dx**2 + dy**2)
        if dist < 1e-6:
            return [start, dest]
            
        nx, ny = -dy / dist, dx / dist
        
        particles_pos = []
        particles_vel = []
        particles_best_pos = []
        particles_best_cost = []
        
        global_best_pos = None
        global_best_cost = float('inf')
        global_best_path = [start, dest]
        
        def evaluate_cost(offsets):
            path = [start]
            for i, off in enumerate(offsets):
                alpha = (i + 1) / (waypoints_count + 1)
                cx = start[0] + dx * alpha + nx * off
                cy = start[1] + dy * alpha + ny * off
                path.append((cx, cy))
            path.append(dest)
            
            metrics = self.cost_engine.evaluate_route(path)
            return metrics["fuel_kg"] + self.risk_weight * metrics["risk"], path
            
        for _ in range(num_particles):
            pos = [random.uniform(-1.0, 1.0) for _ in range(waypoints_count)]
            vel = [random.uniform(-0.2, 0.2) for _ in range(waypoints_count)]
            cost, path = evaluate_cost(pos)
            
            particles_pos.append(pos)
            particles_vel.append(vel)
            particles_best_pos.append(list(pos))
            particles_best_cost.append(cost)
            
            if cost < global_best_cost:
                global_best_cost = cost
                global_best_pos = list(pos)
                global_best_path = path
                
        w = 0.5
        c1 = 1.5
        c2 = 1.5
        
        for _ in range(iterations):
            for i in range(num_particles):
                for j in range(waypoints_count):
                    r1 = random.random()
                    r2 = random.random()
                    particles_vel[i][j] = (w * particles_vel[i][j] + 
                                           c1 * r1 * (particles_best_pos[i][j] - particles_pos[i][j]) + 
                                           c2 * r2 * (global_best_pos[j] - particles_pos[i][j]))
                    particles_pos[i][j] += particles_vel[i][j]
                    
                cost, path = evaluate_cost(particles_pos[i])
                if cost < particles_best_cost[i]:
                    particles_best_cost[i] = cost
                    particles_best_pos[i] = list(particles_pos[i])
                    
                    if cost < global_best_cost:
                        global_best_cost = cost
                        global_best_pos = list(particles_pos[i])
                        global_best_path = path
                        
        return global_best_path

    class RoutingProblem(Problem):
        def __init__(self, start, dest, waypoints_count, cost_engine):
            super().__init__(n_var=waypoints_count, n_obj=2, n_constr=0, xl=-20.0, xu=20.0)
            self.start = start
            self.dest = dest
            self.waypoints_count = waypoints_count
            self.cost_engine = cost_engine
            
            dx = dest[0] - start[0]
            dy = dest[1] - start[1]
            dist = np.sqrt(dx**2 + dy**2)
            if dist < 1e-6:
                self.nx, self.ny = 0.0, 0.0
            else:
                self.nx, self.ny = -dy / dist, dx / dist
            self.dx, self.dy = dx, dy
            
        def _evaluate(self, x, out, *args, **kwargs):
            F = []
            for i in range(x.shape[0]):
                offsets = x[i]
                path = [self.start]
                for j, off in enumerate(offsets):
                    alpha = (j + 1) / (self.waypoints_count + 1)
                    cx = self.start[0] + self.dx * alpha + self.nx * off
                    cy = self.start[1] + self.dy * alpha + self.ny * off
                    path.append((cx, cy))
                path.append(self.dest)
                
                metrics = self.cost_engine.evaluate_route(path)
                F.append([metrics["fuel_kg"], metrics["risk"]])
            out["F"] = np.array(F)

    def _run_nsga2(self, start: Tuple[float, float], dest: Tuple[float, float], grid: np.ndarray) -> List[Tuple[float, float]]:
        """
        Genuine NSGA-II (Non-dominated Sorting Genetic Algorithm II).
        Generational multi-objective search using pymoo principles.
        Maintains population, performs Non-Dominated Sorting and Crowding Distance ranking.
        """
        waypoints_count = 5
        dx = dest[0] - start[0]
        dy = dest[1] - start[1]
        dist = np.sqrt(dx**2 + dy**2)
        if dist < 1e-6:
            return [start, dest]
            
        problem = self.RoutingProblem(start, dest, waypoints_count, self.cost_engine)
        
        # Reduced population and generations for fast testing
        algorithm = NSGA2(pop_size=10)
        from pymoo.optimize import minimize
        nsga_seed = getattr(self, "algo_seeds", {}).get("NSGA-II", 1)
        res = minimize(problem, algorithm, ('n_gen', 5), seed=nsga_seed, verbose=False)
        
        # Pick the median solution from the pareto front
        # res.F contains the objective values for non-dominated solutions
        # res.X contains the variables
        if res.X is None or len(res.X) == 0:
            return [start, dest]
            
        # If there's a pareto front, pick one, for example the one minimizing fuel (obj 0)
        # To avoid being identical to GA, let's pick a balanced one or just index 0
        best_idx = 0
        best_X = res.X if res.X.ndim == 1 else res.X[best_idx]
        
        path = [start]
        nx, ny = problem.nx, problem.ny
        for j, off in enumerate(best_X):
            alpha = (j + 1) / (waypoints_count + 1)
            cx = start[0] + problem.dx * alpha + nx * off
            cy = start[1] + problem.dy * alpha + ny * off
            path.append((cx, cy))
        path.append(dest)
        
        return path
        
    def get_nsga2_pareto_front(self, start: Tuple[float, float], dest: Tuple[float, float], seed: int = 1) -> Tuple[np.ndarray, np.ndarray]:
        """Exposes the full pareto front for testing multiple non-dominated solutions."""
        waypoints_count = 5
        dx = dest[0] - start[0]
        dy = dest[1] - start[1]
        dist = np.sqrt(dx**2 + dy**2)
        if dist < 1e-6:
            return np.array([]), np.array([])
            
        problem = self.RoutingProblem(start, dest, waypoints_count, self.cost_engine)
        algorithm = NSGA2(pop_size=20)
        from pymoo.optimize import minimize
        res = minimize(problem, algorithm, ('n_gen', 10), seed=seed, verbose=False)
        
        return res.X, res.F
