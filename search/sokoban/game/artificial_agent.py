#!/usr/bin/env python3
from game.board import Board, EDirection
from game.action import Action, Move
import time
from typing import List, Union


class ArtificialAgent:
    """
    Agent interface for solving sokoban game.

    Implements core agent methods for interacting with sokoban game:
      - new_game
      - observe
      - act

    Logic should be implemented in subclass
    in think method which is called by act.
    """

    def __init__(self, optimal: bool = False, verbose: bool = False) -> None:
        # solution should be optimal
        self.optimal: bool = optimal
        # verbose output - can be used for logging
        self.verbose: bool = verbose

        self._actions: List[Union[EDirection, Action]] = None
        self._board: Board = None  # readonly
        self._think_time: float = None  # seconds

    def new_game(self) -> None:
        """Agent got into a new level."""
        self._board = None
        self._actions = None
        self._think_time = 0

    def observe(self, board: Board) -> None:
        """Agent receives current state of the board."""
        self._board = board
        cpy = board.clone()
        start = time.perf_counter()
        self._actions = self.think(cpy)
        self._think_time += time.perf_counter() - start

        # for popping from list
        self._actions.reverse()

    def act(self) -> Action:
        """Agent is queried what to do next."""
        if self._actions:
            action = self._actions.pop()
            if self.verbose:
                print("EXECUTING: {}".format(action))
            if isinstance(action, EDirection):
                action = Move.or_push(self._board, action)
            return action
        else:
            return None

    def think(self, board: Board) -> List[Union[EDirection, Action]]:
        raise NotImplementedError
