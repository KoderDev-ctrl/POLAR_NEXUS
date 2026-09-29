import numpy as np
import heapq
from typing import List, Tuple, Dict, Any
from polar_nexus.routex16.cost_layer import RouteCostLayer, CandidateRoute
import math
import random

class DStarLite:
    """Stateful D* Lite for incremental replanning."""
    def __init__(self, start: Tuple[int, int], dest: Tuple[int, int], grid_shape: Tuple[int, int], cost_func):
        self.start = start
        self.dest = dest
        self.grid_shape = grid_shape
        self.cost_func = cost_func
        
        self.U = []
        self.km = 0.0
        self.rhs = {}
        self.g = {}
        
        # Initialize
        for r in range(grid_shape[0]):
            for c in range(grid_shape[1]):
                self.rhs[(r, c)] = float('inf')
                self.g[(r, c)] = float('inf')
                
        self.rhs[self.dest] = 0.0
        heapq.heappush(self.U, (self._calculate_key(self.dest), self.dest))
        
    def _heuristic(self, a, b):
        return np.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)
        
    def _calculate_key(self, s):
        min_g_rhs = min(self.g[s], self.rhs[s])
        return (min_g_rhs + self._heuristic(self.start, s) + self.km, min_g_rhs)
        
    def _get_neighbors(self, u):
        r, c = u
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.grid_shape[0] and 0 <= nc < self.grid_shape[1]:
                neighbors.append((nr, nc))
        return neighbors
        
    def _update_vertex(self, u):
        if u != self.dest:
            min_rhs = float('inf')
            for succ in self._get_neighbors(u):
                c = self.cost_func(u, succ)
                min_rhs = min(min_rhs, c + self.g[succ])
            self.rhs[u] = min_rhs
            
        # Remove u from U
        self.U = [item for item in self.U if item[1] != u]
        heapq.heapify(self.U)
        
        if self.g[u] != self.rhs[u]:
            heapq.heappush(self.U, (self._calculate_key(u), u))
            
    def compute_shortest_path(self):
        iterations = 0
        while self.U and (self.U[0][0] < self._calculate_key(self.start) or self.rhs[self.start] != self.g[self.start]):
            if iterations > 10000:
                break
            iterations += 1
            k_old, u = heapq.heappop(self.U)
            k_new = self._calculate_key(u)
            
            if k_old < k_new:
                heapq.heappush(self.U, (k_new, u))
            elif self.g[u] > self.rhs[u]:
                self.g[u] = self.rhs[u]
                for pred in self._get_neighbors(u):
                    self._update_vertex(pred)
            else:
                self.g[u] = float('inf')
                self._update_vertex(u)
                for pred in self._get_neighbors(u):
                    self._update_vertex(pred)
                    
    def update_edge_cost(self, u, v, new_cost_func):
        """Called when edge costs change. Re-evaluates u and v."""
        self.cost_func = new_cost_func
        self._update_vertex(u)
        self.compute_shortest_path()
        
    def extract_path(self):
        path = [self.start]
        curr = self.start
        visited = {self.start}
        while curr != self.dest:
            best_succ = None
            best_cost = float('inf')
            for succ in self._get_neighbors(curr):
                c = self.cost_func(curr, succ) + self.g.get(succ, float('inf'))
                if c < best_cost and succ not in visited:
                    best_cost = c
                    best_succ = succ
            if best_succ is None or best_succ == curr:
                break
            path.append(best_succ)
            visited.add(best_succ)
            curr = best_succ
        return path


class TimeRiskEngine:
    """
    Engine 3: Time + Risk Optimization.
    Objective: balance travel time against ice/iceberg/environmental risk.
    Algorithms: Risk-Aware A*, D* Lite, Hybrid A*, Risk-Weighted ACO.
    """
    def __init__(self, cost_engine: RouteCostLayer):
        self.cost_engine = cost_engine
        self.risk_weight = 10.0 # lambda for balancing time and risk

    def generate_candidates(self, start: Tuple[float, float], dest: Tuple[float, float], grid: np.ndarray) -> List[CandidateRoute]:
        candidates = []
        
        with open("debug.txt", "a") as f: f.write("Running Risk-Aware A*\n")
        p1 = self._run_risk_astar(start, dest, grid)
        with open("debug.txt", "a") as f: f.write("Running D* Lite\n")
        p2 = self._run_dstar_lite(start, dest, grid)
        with open("debug.txt", "a") as f: f.write("Running Hybrid A*\n")
        p3 = self._run_hybrid_astar(start, dest, grid)
        with open("debug.txt", "a") as f: f.write("Running Risk-Weighted ACO\n")
        p4 = self._run_risk_aco(start, dest, grid)
        with open("debug.txt", "a") as f: f.write("Done running algorithms\n")
        
        paths = [
            ("Risk-Aware A*", p1),
            ("D* Lite", p2),
            ("Hybrid A*", p3),
            ("Risk-Weighted ACO", p4)
        ]
        for algo_name, path in paths:
            metrics = self.cost_engine.evaluate_route(path)
            candidates.append(CandidateRoute(
                route_id=f"TimeRiskEngine_{algo_name}",
                algorithm_name=algo_name,
                engine_category="Time+Risk",
                geometry=path,
                distance_nm=metrics["dist_nm"],
                estimated_time_hours=metrics["time_h"],
                estimated_fuel_kg=metrics["fuel_kg"],
                environmental_risk=metrics["risk"],
                metadata={}
            ))
        return candidates

    def _coord_to_idx(self, coord: Tuple[float, float], grid_shape: Tuple[int, int]) -> Tuple[int, int]:
        lat, lon = coord
        r = int(min(max((lat + 90)/180 * grid_shape[0], 0), grid_shape[0]-1))
        c = int(min(max((lon + 180)/360 * grid_shape[1], 0), grid_shape[1]-1))
        return (r, c)
        
    def _idx_to_coord(self, idx: Tuple[int, int], grid_shape: Tuple[int, int]) -> Tuple[float, float]:
        lat = (idx[0] / grid_shape[0]) * 180 - 90
        lon = (idx[1] / grid_shape[1]) * 360 - 180
        return (lat, lon)

    def _combined_cost(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        metrics = self.cost_engine.evaluate_edge(p1, p2)
        return metrics["time_h"] + self.risk_weight * metrics["risk"]

    def _run_risk_astar(self, start: Tuple[float, float], dest: Tuple[float, float], grid: np.ndarray) -> List[Tuple[float, float]]:
        """Risk-Aware A* (weighted cost function)"""
        start_idx = self._coord_to_idx(start, grid.shape)
        dest_idx = self._coord_to_idx(dest, grid.shape)
        
        open_set = []
        heapq.heappush(open_set, (0, start_idx))
        came_from = {}
        g_score = {start_idx: 0.0}
        
        def heuristic(a, b):
            return np.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)
            
        while open_set:
            current = heapq.heappop(open_set)[1]
            
            if current == dest_idx or heuristic(current, dest_idx) < 1.5:
                path = [dest]
                curr_node = current
                while curr_node in came_from:
                    path.append(self._idx_to_coord(curr_node, grid.shape))
                    curr_node = came_from[curr_node]
                path.append(start)
                return path[::-1]
                
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                nr, nc = current[0] + dr, current[1] + dc
                if 0 <= nr < grid.shape[0] and 0 <= nc < grid.shape[1]:
                    neighbor = (nr, nc)
                    p1 = self._idx_to_coord(current, grid.shape)
                    p2 = self._idx_to_coord(neighbor, grid.shape)
                    cost = self._combined_cost(p1, p2)
                    
                    tentative_g = g_score[current] + cost
                    if tentative_g < g_score.get(neighbor, float('inf')):
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g
                        f = tentative_g + heuristic(neighbor, dest_idx)
                        heapq.heappush(open_set, (f, neighbor))
                        
        return [start, dest]

    def _run_dstar_lite(self, start: Tuple[float, float], dest: Tuple[float, float], grid: np.ndarray) -> List[Tuple[float, float]]:
        """
        Genuine D* Lite structure for incremental graph repair.
        Maintains RHS and G values to quickly re-evaluate when edge costs change.
        """
        start_idx = self._coord_to_idx(start, grid.shape)
        dest_idx = self._coord_to_idx(dest, grid.shape)
        
        def cost_wrapper(u, v):
            p1 = self._idx_to_coord(u, grid.shape)
            p2 = self._idx_to_coord(v, grid.shape)
            return self._combined_cost(p1, p2)
            
        dsl = DStarLite(start_idx, dest_idx, grid.shape, cost_wrapper)
        dsl.compute_shortest_path()
        path_indices = dsl.extract_path()
        
        path = [start]
        for idx in path_indices[1:-1]:
            path.append(self._idx_to_coord(idx, grid.shape))
        path.append(dest)
        return path

    def _run_hybrid_astar(self, start: Tuple[float, float], dest: Tuple[float, float], grid: np.ndarray) -> List[Tuple[float, float]]:
        """
        Hybrid A* incorporating vehicle kinematics (turning radius).
        State space = (x, y, theta).
        """
        start_theta = math.atan2(dest[1] - start[1], dest[0] - start[0])
        start_state = (start[0], start[1], start_theta)
        
        open_set = []
        heapq.heappush(open_set, (0.0, start_state))
        came_from = {}
        g_score = {start_state: 0.0}
        
        def heuristic(state):
            return np.sqrt((state[0]-dest[0])**2 + (state[1]-dest[1])**2)
            
        steer_angles = [-0.2, 0.0, 0.2] # Radians
        step_size = 0.5 # Degrees roughly
        
        iterations = 0
        while open_set and iterations < 1000:
            iterations += 1
            current_state = heapq.heappop(open_set)[1]
            
            if heuristic(current_state) < 1.0:
                path = [dest]
                curr = current_state
                while curr in came_from:
                    path.append((curr[0], curr[1]))
                    curr = came_from[curr]
                path.append(start)
                return path[::-1]
                
            for steer in steer_angles:
                # Kinematic update
                new_theta = current_state[2] + steer
                new_x = current_state[0] + step_size * math.cos(new_theta)
                new_y = current_state[1] + step_size * math.sin(new_theta)
                
                # Snap to a continuous grid for loop closure
                round_state = (round(new_x, 2), round(new_y, 2), round(new_theta, 1))
                
                # Check bounds roughly
                if -90 <= new_x <= 90 and -180 <= new_y <= 180:
                    p1 = (current_state[0], current_state[1])
                    p2 = (new_x, new_y)
                    cost = self._combined_cost(p1, p2)
                    
                    tentative_g = g_score[current_state] + cost + abs(steer)*1.0 # slight penalty for steering
                    
                    if tentative_g < g_score.get(round_state, float('inf')):
                        came_from[round_state] = current_state
                        g_score[round_state] = tentative_g
                        f = tentative_g + heuristic(round_state)
                        heapq.heappush(open_set, (f, round_state))
                        
        return [start, dest]

    def _run_risk_aco(self, start: Tuple[float, float], dest: Tuple[float, float], grid: np.ndarray) -> List[Tuple[float, float]]:
        """Risk-Weighted Ant Colony Optimization."""
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
                        edge_cost = self._combined_cost(grid_nodes[k][current_node_idx], next_node)
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
                            
                    edge_cost = self._combined_cost(grid_nodes[k][current_node_idx], grid_nodes[k+1][chosen_next])
                    cost += edge_cost
                    path_indices.append(chosen_next)
                    path_coords.append(grid_nodes[k+1][chosen_next])
                    current_node_idx = chosen_next
                    
                paths.append((path_indices, path_coords))
                costs.append(cost)
                
                if cost < best_cost:
                    best_cost = cost
                    best_path = path_coords
                    
            for k in range(stages - 1):
                pheromones[k] *= 0.5
                
            for i, (path_indices, path_coords) in enumerate(paths):
                deposit = 100.0 / (costs[i] + 1e-6)
                for k in range(stages - 1):
                    u = path_indices[k]
                    v = path_indices[k+1]
                    pheromones[k][u, v] += deposit
                    
        return best_path
