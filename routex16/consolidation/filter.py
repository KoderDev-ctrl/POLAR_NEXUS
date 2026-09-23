from typing import List, Dict, Any
from polar_nexus.routex16.consolidation.similarity import discrete_frechet_distance, DUPLICATE_ROUTE_THRESHOLD_KM

class RouteConsolidator:
    """
    Consolidates candidate routes by applying Pareto filtering (non-dominated sorting),
    duplicate detection (via Fréchet distance), and diversity filtering.
    """
    def __init__(self, duplicate_threshold_km: float = DUPLICATE_ROUTE_THRESHOLD_KM):
        self.duplicate_threshold_km = duplicate_threshold_km

    def consolidate_routes(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Feasible candidates -> Non-dominated / Pareto filtering -> Duplicate detection -> Diversity filtering -> Final feasible routes
        """
        if not candidates:
            return []

        # 1. Pareto Filtering (Non-dominated sorting)
        # Objectives: estimated_time, estimated_fuel, total_route_risk
        # We find the Pareto fronts, and we'll process them front by front
        fronts = self._fast_non_dominated_sort(candidates)
        
        # 2. Duplicate & Diversity filtering
        # We iterate through candidates in order of Pareto rank.
        # If a candidate is too similar (Fréchet distance < threshold) to an already selected candidate, it is discarded.
        final_routes = []
        for front in fronts:
            for cand in front:
                if not self._is_duplicate(cand, final_routes):
                    final_routes.append(cand)

        return final_routes

    def _fast_non_dominated_sort(self, candidates: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """
        Sorts candidates into Pareto fronts. Lower front index = better (dominates more).
        """
        domination_counts = {id(c): 0 for c in candidates}
        dominated_lists = {id(c): [] for c in candidates}
        fronts = [[]]

        for p in candidates:
            for q in candidates:
                if id(p) == id(q):
                    continue
                if self._dominates(p, q):
                    dominated_lists[id(p)].append(q)
                elif self._dominates(q, p):
                    domination_counts[id(p)] += 1
            if domination_counts[id(p)] == 0:
                p['_pareto_rank'] = 0
                fronts[0].append(p)

        i = 0
        while len(fronts[i]) > 0:
            next_front = []
            for p in fronts[i]:
                for q in dominated_lists[id(p)]:
                    domination_counts[id(q)] -= 1
                    if domination_counts[id(q)] == 0:
                        q['_pareto_rank'] = i + 1
                        next_front.append(q)
            i += 1
            if len(next_front) > 0:
                fronts.append(next_front)
            else:
                break
                
        return fronts

    def _dominates(self, p: Dict[str, Any], q: Dict[str, Any]) -> bool:
        """
        Returns True if p dominates q.
        Minimizing time, fuel, and risk.
        """
        p_obj = (p.get('estimated_time', 0.0), p.get('estimated_fuel', 0.0), p.get('total_route_risk', 0.0))
        q_obj = (q.get('estimated_time', 0.0), q.get('estimated_fuel', 0.0), q.get('total_route_risk', 0.0))
        
        better_in_any = False
        for po, qo in zip(p_obj, q_obj):
            if po > qo:
                return False
            if po < qo:
                better_in_any = True
        return better_in_any

    def _is_duplicate(self, candidate: Dict[str, Any], selected: List[Dict[str, Any]]) -> bool:
        """
        Checks if candidate is a geometric duplicate of any selected route using Fréchet distance.
        """
        cand_waypoints = candidate.get('waypoints', [])
        if not cand_waypoints:
            return True # Consider empty invalid

        for sel in selected:
            sel_waypoints = sel.get('waypoints', [])
            if not sel_waypoints:
                continue
            
            try:
                dist = discrete_frechet_distance(cand_waypoints, sel_waypoints)
                if dist < self.duplicate_threshold_km:
                    return True
            except Exception:
                # Fallback if distance calc fails
                pass
                
        return False
