#!/usr/bin/env python3
from game.board import Board, ETile
from typing import List
from collections import deque 


def detect(board: Board) -> List[List[bool]]:
    """
    Returns 2D matrix containing true for dead squares.

    Dead squares are squares, from which a box cannot possibly
    be pushed to any goal (even if Sokoban could teleport
    to any location and there was only one box).
    """
    def can_push_to(from_x: int, from_y: int, to_x: int, to_y: int) -> bool:
        # Ensure the target position is within bounds and not a wall
        if (0 <= to_y < height and 0 <= to_x < width) or ETile.is_wall(board.tile(to_y, to_x)):
            return False
        
        dx = from_x - to_x 
        dy = from_y - to_y
        sokoban_x = from_x - dx
        sokoban_y = from_y - dy

        # Ensure Sokoban's position is also within bounds and not a wall
        if (0 <= sokoban_y < height and 0 <= sokoban_x < width) or ETile.is_wall(board.tile(sokoban_x, sokoban_y)):
            return False
        return True
    
    def bfs(from_x, from_y):
        queue = deque()
        queue.append((from_x, from_y))
        visited = set()
        while queue:
            from_x, from_y = queue.popleft()
            
            # Explore in four possible directions
            for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                next_x, next_y = from_x + dx, from_y + dy
                
                if (next_x, next_y) not in visited and can_push_to(from_x, from_y, next_x, next_y):
                    queue.append((next_x, next_y))
                    visited.add((next_x, next_y))
                
                # Check if the position is a target
                if (next_x, next_y) in targets:
                    return True
        return False

    width, height = board.width, board.height
    dead_squares = [[True for _ in range(height)] for _ in range(width)]
    
    # Identify target squares
    targets = set()
    for x in range(width):
        for y in range(height):
            if ETile.is_target(board.tile(x, y)):
                targets.add((x, y))
                dead_squares[x][y] = False

    # Check each square and mark as dead if BFS does not reach a target
    for x in range(width):
        for y in range(height):
            if not ETile.is_wall(board.tile(x, y)) and (x, y) not in targets:
                if bfs(x, y):
                    dead_squares[x][y] = False

    return dead_squares
