#!/usr/bin/env python3
from game.controllers import PacManControllerBase
from game.pacman import Game, DM
from typing import List
# from game.pac_gui import PacView
import sys
from os.path import dirname
from collections import deque

# hack for importing from parent package
sys.path.append(dirname(dirname(dirname(__file__))))
from search_templates import *
from ucs import ucs

# hint: class PacManProblem(Problem)...
#       ... Ucs.search(problem)
class PacManProblem(Problem):
    def __init__(self, game: Game) -> None:
        self.game: Game = game

    def initial_state(self) -> int:
        return self.game.pac_loc

    def actions(self, state: int) -> List[int]:
        possible_pacman_actions = []
        for action in range(4):
            if self.game.get_neighbor(state, action) != -1:
                possible_pacman_actions.append(action)
        return possible_pacman_actions

    def result(self, state: int, action: int) -> int:
        return self.game.get_neighbor(state,action)

    def is_goal(self, state: int) -> bool:
        if state in self.game.get_active_pills_nodes() or state in self.game.get_active_power_pills_nodes():
            return True
        return False

    def cost(self, state: int, action: int) -> float:
        closest_ghost_distance = float('inf')
        next_state = self.result(state, action)
        for ghost_loc in self.game.ghost_locs:
            curr_dist = self.game.get_path_distance(state, ghost_loc)
            next_dist = self.game.get_path_distance(next_state, ghost_loc)
            if (next_dist == -1):
                next_dist = 500
                curr_dist = 500
            closest_ghost_distance_next = min(closest_ghost_distance,next_dist)
            closest_ghost_distance_curr = min(closest_ghost_distance,curr_dist)
            if (abs(closest_ghost_distance_next - closest_ghost_distance_curr) > 1):
                print('brk')
            print(abs(closest_ghost_distance_next - closest_ghost_distance_curr))
            print("curr vv")
            print(closest_ghost_distance_curr)
            print(closest_ghost_distance_next)
        if closest_ghost_distance_next < 5:
            ("jst breakpoint")
        if closest_ghost_distance_next < 5 and closest_ghost_distance_next < closest_ghost_distance_curr:
            print("POZOR BLIZKO")
            return 100  # High cost to avoid monsters
        if closest_ghost_distance < 10 and closest_ghost_distance_next < closest_ghost_distance_curr:
            print('DOCELA BLIZKO')
            return 15 
        elif next_state in self.game.get_active_pills_nodes():
            return 0.05  # Low cost to collect pills
        else:
            return 1  # Normal cost


class MyAgent(PacManControllerBase):
    def __init__(
        self, human: bool = False, seed: int = 0, verbose: bool = False
    ) -> None:
        super().__init__(human, seed, verbose)

        # You can initialize your own class variables here.

    def tick(self, game: Game) -> None:
        # Your implementation goes here.
        prob = PacManProblem(game)
        sol = ucs(prob)
        if sol is None or not sol.actions:
            pass
        else:
            self.pacman.set(sol.actions[0])
        # Dummy implementation: move in a random direction.
        # You won't live long this way
        #directions = game.get_possible_pacman_dirs(False)
       # self.pacman.set(self.random.choice(directions))
