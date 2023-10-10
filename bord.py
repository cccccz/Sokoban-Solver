from typing import List

# Constants for puzzle elements
WALL = '#'
STORAGE_LOC = '.'
CRATE = '?'
CRATE_ON_STORAGE = '*'  # A crate is on a storage point.
AUTOMATON = 'a'
AUTOMATON_ON_STORAGE = 'A'  # An automaton is on a storage point.

class PuzzleGrid:
    """
    Represents the game grid.
    """

    def __init__(self, label: str, grid_width: int, grid_height: int, automata: object, crates: object, storage_pts: object,
                 barriers: object) -> object:
        self.label = label
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.crates = crates
        self.automata = automata
        self.storage_pts = storage_pts
        self.barriers = barriers

    def __hash__(self):
        return hash(self.__repr__())

    def visualize(self):
        print(self.__repr__())

    def __repr__(self):
        grid_rep = []
        for y in range(self.grid_height):
            line = []
            for x in range(self.grid_width):
                line.append(' ')
            grid_rep.append(line)

        for storage in self.storage_pts:
            grid_rep[storage[1]][storage[0]] = STORAGE_LOC

        for barrier in self.barriers:
            grid_rep[barrier[1]][barrier[0]] = WALL

        for idx, automaton in enumerate(self.automata):
            char = AUTOMATON_ON_STORAGE if automaton in self.storage_pts else AUTOMATON
            grid_rep[automaton[1]][automaton[0]] = chr(ord(char) + idx)

        for crate in self.crates:
            char = CRATE_ON_STORAGE if crate in self.storage_pts else CRATE
            grid_rep[crate[1]][crate[0]] = char

        return '\n'.join([''.join(line) for line in grid_rep])

    def __eq__(self, other_instance):
        if isinstance(other_instance, PuzzleGrid):
            return self.__repr__() == other_instance.__repr__()
        return False

class GameState:
    """
    Wraps a PuzzleGrid with additional current state information.
    """

    def __init__(self, puzzle: PuzzleGrid, heuristic_func, f_score: int, tree_depth: int, parent_state=None):
        self.puzzle = puzzle
        self.parent_state = parent_state
        self.heuristic_func = heuristic_func
        self.f_score = f_score
        self.tree_depth = tree_depth
        self.identifier = hash(puzzle)

    def __lt__(self, other_instance):
        return self.f_score < other_instance.f_score

    def __repr__(self):
        return str(self.puzzle)

def base_heuristic(puzzle: PuzzleGrid):
    """
    Returns a base heuristic value for any given state.
    """
    return 0

def load_from_file(file_path: str) -> PuzzleGrid:
    """
    Load the puzzle configuration from a file.
    """
    with open(file_path, "r") as file:
        lines = file.readlines()
        label, grid_width, grid_height = lines[0].strip(), int(lines[1]), int(lines[2])
        grid = PuzzleGrid(label, grid_width, grid_height, [], [], [], [])
        
        for idx, line in enumerate(lines[3:]):
            for col, char in enumerate(line):
                coord = (col, idx)
                if char == WALL:
                    grid.barriers.append(coord)
                elif char == CRATE_ON_STORAGE:
                    grid.crates.append(coord)
                    grid.storage_pts.append(coord)
                elif char == CRATE:
                    grid.crates.append(coord)
                elif char == STORAGE_LOC:
                    grid.storage_pts.append(coord)
                elif char.isalpha():
                    grid.automata.append(coord)
                    if char.isupper():
                        grid.storage_pts.append(coord)

    return grid
