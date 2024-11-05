from search_templates import Problem, Solution
from typing import Optional
import heapq
from itertools import count

def ucs(prob: Problem) -> Optional[Solution]:
    """Return Solution of the problem solved by Uniform Cost Search (UCS)."""
    explored = set()
    frontier = []
    counter = count()  # Unique sequence count
    heapq.heappush(frontier, (0, next(counter), prob.initial_state(), []))  # (cost, count, state, path)

    while frontier:
        cost, _, state, path = heapq.heappop(frontier)

        if state in explored:
            continue

        explored.add(state)

        if prob.is_goal(state):
            return Solution(path, state, cost)

        for action in prob.actions(state):
            child_state = prob.result(state, action)
            child_cost = cost + prob.cost(state, action)
            if child_state not in explored:
                heapq.heappush(frontier, (child_cost, next(counter), child_state, path + [action]))

    return None
