import sys 
import os
from dataclasses import dataclass
from typing import Tuple
from mazegen.generator import MazeGenerator
from mlx import Mlx
import random
import time

@dataclass
class Config:
    """Struct for maze configuration"""
    width: int
    height: int
    entry: Tuple[int, int]
    exit: Tuple[int, int]
    perfect: bool
    output_file: str
    seed: str = None

def parse_config(file_name: str) -> Config:
    """
    Read config file and return a dict with config.
    Handle file error
    """
    if not os.path.isfile(file_name):
        print(f"Error: Configuration file '{file_name}' not found.",file=sys.stderr)
        sys.exit(1)

    data = {}

    try:
        with open(file_name, 'r') as config:
            for line in config:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                if "=" not in line:
                    print(f"Error: Bad format in config file. Line '{line}' "
                          "is invalid.", file=sys.stderr)
                    sys.exit(1)

                key, value = line.split("=", 1)
                data[key.strip()] = value.strip()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    return convert(data)


def convert(data: dict)-> Config:
    mandatory = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "PERFECT", "OUTPUT_FILE"]

    for key in mandatory:
        if key not in data:
            print(f"Error : Missing key '{key}' in config file", file=sys.stderr)
            sys.exit(1)

    try:
        width = int(data["WIDTH"])
        height = int(data["HEIGHT"])

        if width <= 0 or height <= 0:
            print("Error: Dimensions (WIDTH, HEIGHT) must be greater than 0.", file=sys.stderr)
            sys.exit(1)

        entry_parts = data["ENTRY"].split(",")
        entry_x = int(entry_parts[0])
        entry_y = int(entry_parts[1])
        entry = (entry_x, entry_y)

        exit_parts = data["EXIT"].split(",")
        exit_x = int(exit_parts[0])
        exit_y = int(exit_parts[1])
        exit_coord = (exit_x, exit_y)

        if entry_x < 0 or entry_x >= width or entry_y < 0 or entry_y >= height:
            print(f"Error: Entry {entry} is outside the maze boundaries.", file=sys.stderr)
            sys.exit(1)

        if exit_x < 0 or exit_x >= width or exit_y < 0 or exit_y >= height:
            print(f"Error: Exit {exit_coord} is outside the maze boundaries.", file=sys.stderr)
            sys.exit(1)

        if entry == exit_coord:
            print("Error: entry and exit cannot be at the same coordinate.", file=sys.stderr)
            sys.exit(1)
    
        perfect = data["PERFECT"].lower() == "true"
        output_file = data["OUTPUT_FILE"]
        seed = data.get("SEED")
        return Config(width, height, entry, exit_coord, perfect, output_file, seed)

    except Exception as e:
        print(f"Error: {type(e).__name__} - {e}")
        sys.exit(1)



def solve_maze(grid, width, height, start, end):

    map = []
    for y in range(height):
        line = []
        for x in range(width):
            line.append(-1)
        map.append(line)

    start_x, start_y = start
    map[start_y][start_x] = 0
    queue = [start]
    resolved = False

    while len(queue) > 0:

        cx, cy = queue.pop(0)

        if (cx, cy) == end:
            resolved = True
            break

        neighbors = get_neighbors(grid, width, height, cx, cy)
        for x, y in neighbors:
            # -1 == not visited
            if map[y][x] == -1:
                map[y][x] = map[cy][cx] + 1
                queue.append((x, y))
    if not resolved:
        print("No solution found")
        sys.exit(1)

    # We found the exit, now we need to find the shortest path

    # Start from the end 
    path = [end]
    cx, cy = end

    dist = map[cy][cx]

    while dist > 0:
        neighbors = get_neighbors(grid, width, height, cx, cy)

        for x, y in neighbors:
                if map[y][x] == dist - 1:
                    cx, cy = x, y
                    dist -= 1
                    path.append((x, y))
                    break

    # We inverse the path 
    return path[::-1]

def get_neighbors(grid, width, height, x, y):
    possible = []
    
    value = grid[y][x]

    # North
    if y > 0 and (value & 1) == 0:
        possible.append((x, y - 1))

    # South
    if y < height - 1 and (value & 4) == 0:
        possible.append((x, y + 1))

    # East
    if x < width - 1 and (value & 2) == 0:
        possible.append((x + 1, y))

    # West
    if x > 0 and (value & 8) == 0:
        possible.append((x - 1, y))

    return possible


def path_to_cardinal(path):
    if not path or len(path) < 2:
        return ""
    
    directions = ""
    for i in range(len(path) - 1):
        curr_x, curr_y = path[i]
        next_x, next_y = path[i+1]
        
        if next_y < curr_y: directions += "N"
        elif next_x > curr_x: directions += "E"
        elif next_y > curr_y: directions += "S"
        elif next_x < curr_x: directions += "W"
        
    return directions

def render_maze(grid, width, height, entry, exit, seed_value, path=None):
    """
    Rendu "Pixel Perfect" : Pas de bavures, départ/arrivée bien isolés.
    """
    RESET = "\033[00m"
    BG_WALL  = "\033[45m"
    BG_EMPTY =  "\033[107m"
    BG_PATH  = "\033[42m"
    BG_ENTRY = "\033[104m"
    BG_EXIT  = "\033[41m"
    BG_42    = "\033[100m"

    BLK_WALL  = f"{BG_WALL}  {RESET}"
    BLK_EMPTY = f"{BG_EMPTY}  {RESET}"
    BLK_PATH  = f"{BG_PATH}  {RESET}"
    
    # Optimisation : On transforme la liste en set pour des recherches instantanées
    path_set = set(path) if path else set()
    
    # On s'assure que Start et End sont considérés comme "faisant partie du chemin"
    # pour que les liaisons se fassent bien
    if path:
        path_set.add(entry)
        path_set.add(exit)

    print(f"\nDimensions: {width}x{height}, seed: {seed_value}")
    
    # Bordure du haut
    print(BLK_WALL + (BLK_WALL * 2) * width)

    for y in range(height):
        line_body = BLK_WALL
        line_bottom = BLK_WALL

        for x in range(width):
            val = grid[y][x]
            
            # 1. COULEUR DU BLOC CENTRAL
            if (x, y) == entry:
                # On force le bloc Entry en vert
                center_color = f"{BG_ENTRY}  {RESET}"
            elif (x, y) == exit:
                center_color = f"{BG_EXIT}  {RESET}"
            elif (x, y) in path_set:
                center_color = BLK_PATH
            elif val == 15:
                center_color = f"{BG_42}  {RESET}"
            else:
                center_color = BLK_EMPTY

            line_body += center_color

            # 2. LIAISON EST (Droite)
            if (val & 2) != 0: # Mur fermé
                line_body += BLK_WALL
            else: # Mur ouvert
                # INTELLIGENCE ICI : On ne met du bleu que si les DEUX sont sur le chemin
                if (x, y) in path_set and (x + 1, y) in path_set:
                    line_body += BLK_PATH
                else:
                    line_body += BLK_EMPTY

            # 3. LIAISON SUD (Bas)
            if (val & 4) != 0: # Mur fermé
                line_bottom += BLK_WALL
            else: # Mur ouvert
                # INTELLIGENCE ICI : Idem, on vérifie le voisin du bas
                if (x, y) in path_set and (x, y + 1) in path_set:
                    line_bottom += BLK_PATH
                else:
                    line_bottom += BLK_EMPTY

            # Coin (toujours un mur pour la structure)
            line_bottom += BLK_WALL

        print(line_body)
        print(line_bottom)




def main():

    if len(sys.argv) == 2:
        try:
            config = parse_config(sys.argv[1])
        except Exception as e:
            print(f"An error as occured : {e}")
            sys.exit(1)
    else:
        print("Usage: python3 a_maze_ing.py config.txt")
        sys.exit(1)

    show_path = True 
    if config.seed is not None:
        seed_value = (config.seed)
    else:
        seed_value = str(random.randint(0, 10000000000))
    random.seed(seed_value)
    maze = MazeGenerator(config.width, config.height)
    start_x = config.entry[0]
    start_y = config.entry[1]
    maze.generate_maze(config.entry, config.exit, config.perfect)
    print(f"Saving to {config.output_file}...")
    path = solve_maze(maze.grid, config.width, config.height, config.entry, config.exit)
    cardinal = path_to_cardinal(path)
    maze.save_maze(config.output_file, cardinal)
    
    # print(f"DONE! Solution found with {len(path)} steps.")
    render_maze(maze.grid, config.width, config.height, config.entry, config.exit, seed_value, path if show_path else None)

    while True:

        print("======== A-Maze-ing ========" )
        print("1. Re-generate a new maze")
        print("2. Show/Hide path from entry to exit")
        print("3. Quit")
        try:  
            choice = int(input("Choice (1-3): "))
        except Exception as e:
            print (f"Error: invalid input.")
            continue

        if choice == 1:
            if config.seed is not None:
                random.seed(config.seed)
            else:
                seed_value = str(random.randint(0, 10000000000))
                random.seed(seed_value)
            maze.generate_maze(config.entry, config.exit, config.perfect)
            path = solve_maze(maze.grid, config.width, config.height, config.entry, config.exit)
            render_maze(maze.grid, config.width, config.height, config.entry, config.exit, seed_value, path if show_path else None)
            print(f"Saving to {config.output_file}...\n")
            maze.save_maze(config.output_file)
       
        if choice == 2:
            if show_path == True:
                show_path = False
            elif show_path == False:
                show_path = True
            render_maze(maze.grid, config.width, config.height, config.entry, config.exit, seed_value, path if show_path else None)

        if choice == 3:
            return



if __name__ == "__main__":
    main()
