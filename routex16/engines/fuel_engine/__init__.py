import numpy as np
import yaml
from typing import List, Tuple
from polar_nexus.routex16.cost_layer import RouteCostLayer, CandidateRoute

class FuelEngine:
    """
    Engine 2: Fuel Optimization.
    Objective: minimize fuel consumption.
    Algorithms: Dynamic Programming, Genetic Algorithm, Ant Colony Optimization, Particle Swarm Optimization.
    """
    def __init__(self, cost_engine: RouteCostLayer):
        self.cost_engine = cost_engine

    def generate_candidates(self, start: Tuple[float, float], dest: Tuple[float, float], grid: np.ndarray) -> List[CandidateRoute]:
        # Load deterministic seeds
        import random
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
            ("ACO", self._run_aco(start, dest, grid)),
            ("PSO", self._run_pso(start, dest, grid))
        ]
        for algo_name, path in paths:
            metrics = self.cost_engine.evaluate_route(path)
            candidates.append(CandidateRoute(
                route_id=f"FuelEngine_{algo_name}",
                algorithm_name=algo_name,
                engine_category="Fuel",
                geometry=path,
                distance_nm=metrics["dist_nm"],
                estimated_time_hours=metrics["time_h"],
                estimated_fuel_kg=metrics["fuel_kg"],
                environmental_risk=metrics["risk"],
                metadata={}
            ))
        return candidates

    def _run_dp(self, start: Tuple[float, float], dest: Tuple[float, float], grid: np.ndarray) -> List[Tuple[float, float]]:
        """Genuine Dynamic Programming (Stage-wise)."""
        stages = 10
        transverse_nodes = 5
        transverse_width = 2.0 # Total width spread
        
        # Build stage nodes
        # Stage 0 is just start
        # Stage 'stages-1' is just dest
        # Intermediate stages are transverse lines perpendicular to the main vector
        
        dx = dest[0] - start[0]
        dy = dest[1] - start[1]
        dist = np.sqrt(dx**2 + dy**2)
        
        if dist < 1e-6:
            return [start, dest]
            
        nx = -dy / dist
        ny = dx / dist
        
        grid_nodes = []
        grid_nodes.append([start])
        
        for k in range(1, stages - 1):
            alpha = k / (stages - 1)
            cx = start[0] + dx * alpha
            cy = start[1] + dy * alpha
            
            stage_points = []
            for j in range(transverse_nodes):
                offset = (j - (transverse_nodes - 1)/2) / (transverse_nodes - 1) * transverse_width
                px = cx + nx * offset
                py = cy + ny * offset
                stage_points.append((px, py))
            grid_nodes.append(stage_points)
            
        grid_nodes.append([dest])
        
        # DP tables
        # dp_cost[k][j] = min cost to reach node j at stage k
        # dp_prev[k][j] = index of best previous node at stage k-1
        
        dp_cost = [[float('inf')] * len(stage) for stage in grid_nodes]
        dp_prev = [[-1] * len(stage) for stage in grid_nodes]
        
        dp_cost[0][0] = 0.0
        
        for k in range(1, stages):
            for j, current_node in enumerate(grid_nodes[k]):
                best_cost = float('inf')
                best_prev = -1
                for i, prev_node in enumerate(grid_nodes[k-1]):
                    edge_metrics = self.cost_engine.evaluate_edge(prev_node, current_node)
                    transition_cost = edge_metrics["fuel_kg"]
                    
                    cost = dp_cost[k-1][i] + transition_cost
                    if cost < best_cost:
                        best_cost = cost
                        best_prev = i
                        
                dp_cost[k][j] = best_cost
                dp_prev[k][j] = best_prev
                
        # Backtrack
        path = []
        curr_j = 0
        for k in range(stages - 1, -1, -1):
            path.append(grid_nodes[k][curr_j])
            curr_j = dp_prev[k][curr_j]
            
        return path[::-1]

    def _run_ga(self, start: Tuple[float, float], dest: Tuple[float, float], grid: np.ndarray) -> List[Tuple[float, float]]:
        """Genuine Genetic Algorithm (Combinatorial Route)."""
        import random
        pop_size = 20
        generations = 10
        waypoints_count = 5
        
        dx = dest[0] - start[0]
        dy = dest[1] - start[1]
        dist = np.sqrt(dx**2 + dy**2)
        if dist < 1e-6:
            return [start, dest]
            
        nx, ny = -dy / dist, dx / dist
        
        # Population: array of offsets for the intermediate waypoints
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
            
            cost = self.cost_engine.evaluate_route(path)["fuel_kg"]
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
            next_gen = [evaluated[0][1], evaluated[1][1]] # Elitism
            
            while len(next_gen) < pop_size:
                p1 = random.choice(evaluated[:10])[1]
                p2 = random.choice(evaluated[:10])[1]
                # Crossover
                child = [p1[i] if random.random() < 0.5 else p2[i] for i in range(waypoints_count)]
                # Mutation
                for i in range(waypoints_count):
                    if random.random() < 0.2:
                        child[i] += random.uniform(-0.5, 0.5)
                next_gen.append(child)
            population = next_gen
            
        return best_path

    def _run_aco(self, start: Tuple[float, float], dest: Tuple[float, float], grid: np.ndarray) -> List[Tuple[float, float]]:
        """Genuine Ant Colony Optimization."""
        import random
        ants = 10
        iterations = 5
        stages = 8
        transverse_nodes = 5
        transverse_width = 2.0
        
        dx = dest[0] - start[0]
        dy = dest[1] - start[1]
        dist = np.sqrt(dx**2 + dy**2)
        if dist < 1e-6:
            return [start, dest]
            
        nx, ny = -dy / dist, dx / dist
        
        # Build grid
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
        
        # Pheromones initialized to 1.0
        pheromones = []
        for k in range(stages - 1):
            pheromones.append(np.ones((len(grid_nodes[k]), len(grid_nodes[k+1]))))
            
        best_path = [start, dest]
        best_cost = float('inf')
        
        for it in range(iterations):
            paths = []
            costs = []
            
            for ant in range(ants):
                current_node_idx = 0
                path_indices = [0]
                path_coords = [start]
                cost = 0.0
                
                for k in range(stages - 1):
                    probs = []
                    for next_idx, next_node in enumerate(grid_nodes[k+1]):
                        edge_cost = self.cost_engine.evaluate_edge(grid_nodes[k][current_node_idx], next_node)["fuel_kg"]
                        # heuristic = 1 / cost
                        eta = 1.0 / (edge_cost + 1e-6)
                        tau = pheromones[k][current_node_idx, next_idx]
                        probs.append(tau * eta**2)
                        
                    probs_sum = sum(probs)
                    if probs_sum == 0:
                        probs = [1.0/len(probs)] * len(probs)
                    else:
                        probs = [p / probs_sum for p in probs]
                        
                    r = random.random()
                    cumulative = 0.0
                    chosen_next = 0
                    for i, p in enumerate(probs):
                        cumulative += p
                        if r <= cumulative:
                            chosen_next = i
                            break
                            
                    edge_cost = self.cost_engine.evaluate_edge(grid_nodes[k][current_node_idx], grid_nodes[k+1][chosen_next])["fuel_kg"]
                    cost += edge_cost
                    path_indices.append(chosen_next)
                    path_coords.append(grid_nodes[k+1][chosen_next])
                    current_node_idx = chosen_next
                    
                paths.append((path_indices, path_coords))
                costs.append(cost)
                
                if cost < best_cost:
                    best_cost = cost
                    best_path = path_coords
                    
            # Evaporation
            for k in range(stages - 1):
                pheromones[k] *= 0.5
                
            # Deposit
            for i, (path_indices, path_coords) in enumerate(paths):
                deposit = 100.0 / (costs[i] + 1e-6)
                for k in range(stages - 1):
                    u = path_indices[k]
                    v = path_indices[k+1]
                    pheromones[k][u, v] += deposit
                    
        return best_path

    def _run_pso(self, start: Tuple[float, float], dest: Tuple[float, float], grid: np.ndarray) -> List[Tuple[float, float]]:
        """Genuine Particle Swarm Optimization."""
        import random
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
            
            return self.cost_engine.evaluate_route(path)["fuel_kg"], path
            
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
