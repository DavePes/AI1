#!/usr/bin/env python3
from game.controllers import PacManControllerBase
from game.pacman import Game, DM, Direction
from typing import List
import sys
from os.path import dirname

# hack for importing from parent package
sys.path.append(dirname(dirname(dirname(__file__))))
from search_templates import *
from ucs import ucs


class PacProblem(Problem):
    def __init__(self, game: Game) -> None:
        self.game: Game = game

    def initial_state(self) -> int:
        return self.game._pac_loc

    def actions(self, state: int) -> List[int]:
        valid_actions = []
        for action in range(4):
            if self.game.get_neighbor(state, action) != -1:
                valid_actions.append(action)
        return valid_actions

    def result(self, state: int, action: int) -> int:
        return self.game.get_neighbor(state, action)

    def is_goal(self, state: int) -> bool:

        active_pills = self.game.get_active_pills_nodes()
        active_power_pills = self.game.get_active_power_pills_nodes()
        
        if state in active_pills or state in active_power_pills:
            return True
            
        # Kontrola jedlých duchů v blízkosti
        for ghost_idx in range(0, 4):
            if self.game.get_edible_time(ghost_idx) > 0:
                ghost_loc = self.game.get_ghost_loc(ghost_idx)
                #print(f"ghost ({ghost_idx}) is in distance: {self.game.get_path_distance(state, ghost_loc)}")
                if self.game.get_path_distance(state, ghost_loc) < 3:
                    return True
                    
        return False

    def cost(self, state: int, action: int) -> float:
        next_state = self.game.get_neighbor(state, action)
        base_cost = 1.0
        total_cost = base_cost
        
        # Získáme všechny aktivní cíle
        active_pills = self.game.get_active_pills_nodes()
        active_power_pills = self.game.get_active_power_pills_nodes()
        
        # Zohlednění vzdálenosti k nejbližší tečce/power pill
        if active_pills or active_power_pills:
            targets = active_pills + active_power_pills
            current_to_target = self.game.get_path_distance(state, 
                self.game.get_target(state, targets, True, DM.PATH))
            next_to_target = self.game.get_path_distance(next_state, 
                self.game.get_target(next_state, targets, True, DM.PATH))
            
            # Pokud se vzdalujeme od cíle, zvýšíme cenu
            if next_to_target > current_to_target:
                total_cost *= 1.5

        # Vyhodnocení nebezpečí od duchů
        ghost_danger = 0
        ghost_opportunity = 0
        closest_ghost_distance = float('inf')
        
        for ghost_idx in range(0,4):
            ghost_loc = self.game.get_ghost_loc(ghost_idx)
            curr_dist = self.game.get_path_distance(state, ghost_loc)
            next_dist = self.game.get_path_distance(next_state, ghost_loc)
            closest_ghost_distance = min(closest_ghost_distance, next_dist)
            
            edible_time = self.game.get_edible_time(ghost_idx)
            
            if edible_time > 0:  # Jedlý duch
                # Čím blíž jsme k jedlému duchovi a čím víc času zbývá, tím lepší
                if next_dist < curr_dist:
                    ghost_opportunity += (edible_time / 20.0) * (1.0 / max(next_dist, 1))
            else:  # Nejedlý duch
                if next_dist < curr_dist:  # Přibližujeme se k nebezpečnému duchovi
                    ghost_danger += 1.0 / max(next_dist, 0.1)  # Inverzní vzdálenost jako míra nebezpečí
        
        # Aplikace nebezpečí od duchů
        if ghost_danger > 0:
            if closest_ghost_distance < 3:
                total_cost += 100.0  # Kriticky nebezpečná situace
            elif closest_ghost_distance < 5:
                total_cost += 20.0   # Nebezpečná situace
            else:
                total_cost += ghost_danger * 5.0  # Vzdálenější nebezpečí
        
        # Snížení ceny pro příležitosti (jedlí duchové)
        if ghost_opportunity > 0:
            # Pokud jsme velmi blízko jedlému duchovi, uděláme tuto cestu velmi atraktivní
            if closest_ghost_distance <= 2:
                total_cost = 0.1
            else:
                total_cost *= max(0.2, 1.0 - ghost_opportunity)
        
        # Power pill strategie
        if next_state in active_power_pills:
            nearby_ghosts = sum(1 for ghost_idx in range(0,4)
                              if self.game.get_path_distance(ghost_loc, next_state) < 8)
            if nearby_ghosts >= 2:
                # Power pill je výhodná, když je poblíž více duchů
                total_cost *= 0.1
            else:
                # Jinak možná chceme počkat na lepší příležitost
                total_cost *= 2.0
                
        return total_cost


class Agent_Using_UCS(PacManControllerBase):
    def tick(self, game: Game) -> None:
        prob = PacProblem(game)
        sol = ucs(prob)
        
        
        if sol is None or not sol.actions:
            # Pokud není nalezena cesta, zkusíme náhodný validní směr
            valid_moves = []
            for action in range(4):
                if game.get_neighbor(game._pac_loc, action) != -1:
                    valid_moves.append(action)
            if valid_moves:
                self.pacman.set(valid_moves[0])  # Použijeme první validní tah
        else:
            self.pacman.set(sol.actions[0])  # Použijeme první akci z nalezené cesty
