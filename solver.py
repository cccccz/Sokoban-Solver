from typing import List
import heapq
from heapq import heappush, heappop
import time
import argparse
import math

from board import *

def check_goal(game_state):
    for item in str(game_state.board):
        if item == '.' or item.isupper():
            return False
    return True

def trace_route(game_state):
    current_state = game_state
    route = []
    while current_state:
        route.append(current_state)
        current_state = current_state.parent
    return list(reversed(route))

def find_next_states(game_state):
    curr_board = game_state.board
    moves = [(-1,0),(0,-1),(1,0),(0,1)]
    next_states = []

    for idx, bot in enumerate(curr_board.robots):
        for move in moves:
            next_pos = (bot[0]+move[0], bot[1]+move[1])
            if next_pos in curr_board.obstacles or next_pos in curr_board.robots:
                continue
            
            updated_robots = curr_board.robots[:]
            box_positions = curr_board.boxes[:]
            if next_pos in box_positions:
                for bidx, box in enumerate(box_positions):
                    next_box_pos = (next_pos[0]+move[0], next_pos[1]+move[1])
                    if next_pos == box and next_box_pos not in curr_board.obstacles and next_box_pos not in updated_robots and next_box_pos not in box_positions:
                        box_positions[bidx] = tuple(map(sum, zip(box, move)))
                        updated_robots[idx] = next_pos
                        updated_board = Board(curr_board.name, curr_board.width, curr_board.height, updated_robots, box_positions, curr_board.storage, curr_board.obstacles)
                        next_game_state = State(updated_board, game_state.hfn, game_state.f + 1, game_state.depth + 1, game_state)
                        next_states.append(next_game_state)
            else:
                updated_robots[idx] = next_pos
                updated_board = Board(curr_board.name, curr_board.width, curr_board.height, updated_robots, box_positions, curr_board.storage, curr_board.obstacles)
                next_game_state = State(updated_board, game_state.hfn, game_state.f + 1, game_state.depth + 1, game_state)
                next_states.append(next_game_state)

    return next_states

def depth_first_search(initial_board):
    root_state = State(initial_board, heuristic_simple, 0, 0, None)
    stack = [root_state]
    seen = set()

    while stack:
        curr_state = stack.pop()
        if str(curr_state) in seen:
            continue
        seen.add(str(curr_state))
        if check_goal(curr_state):
            return (trace_route(curr_state), curr_state.f)
        stack.extend(find_next_states(curr_state))
    return [], -1

def optimal_search(initial_board, heuristic_func):
    root_state = State(initial_board, heuristic_func, 0, 0, None)
    init_cost = heuristic_func(initial_board)
    priority_queue = [(init_cost, root_state)]
    seen = set()

    while priority_queue:
        _, curr_state = heapq.heappop(priority_queue)
        if check_goal(curr_state):
            return (trace_route(curr_state), curr_state.f)
        if str(curr_state) in seen:
            continue
        seen.add(str(curr_state))
        for next_state in find_next_states(curr_state):
            if str(next_state) not in seen:
                heapq.heappush(priority_queue, (next_state.f + heuristic_func(next_state.board), next_state))
    return [], -1

def heuristic_simple(playboard):
    total_distance = 0
    for crate in playboard.boxes:
        min_dist = math.inf
        for spot in playboard.storage:
            distance = abs(spot[0]-crate[0]) + abs(spot[1]-crate[1])
            if distance < min_dist:
                min_dist = distance
        total_distance += min_dist
    return total_distance

def heuristic_complex(playboard):
    total_distance = 0
    barriers = playboard.obstacles
    for crate in playboard.boxes:
        potential_barriers = [(crate[0], crate[1]+1), (crate[0], crate[1]-1), (crate[0]-1, crate[1]), (crate[0]+1, crate[1])]
        if crate not in playboard.storage and any(b in barriers for b in potential_barriers):
            return math.inf
        min_dist = math.inf
        for spot in playboard.storage:
            distance = abs(spot[0]-crate[0]) + abs(spot[1]-crate[1])
            if distance < min_dist:
                min_dist = distance
        total_distance += min_dist
    return total_distance