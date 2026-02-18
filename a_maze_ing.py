import sys
import os
import time
from dataclasses import dataclass
from typing import Tuple, Optional, List, Dict, Any
from mazegen.generator import MazeGenerator
import random


@dataclass
class Config:
    """Struct for maze configuration"""
    width: int
    height: int
    entry: Tuple[int, int]
    exit: Tuple[int, int]
    perfect: bool
    output_file: str
    seed: Optional[str] = None
    animation_wg: Optional[bool] = False


def parse_config(file_name: str) -> Config:
    """
    Read config file and return a dict with config.
    Handle file error
    """
    if not os.path.isfile(file_name):
        print(f"Error: Configuration file '{file_name}' not found.",
              file=sys.stderr)
        sys.exit(1)

    data: Dict[str, str] = {}

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


def convert(data: Dict[str, str]) -> Config:
    """
    Validate raw dictionary data and convert it into a typed Config object.
    """
    mandatory = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "PERFECT", "OUTPUT_FILE"]

    for key in mandatory:
        if key not in data:
            print(f"Error : Missing key '{key}' in config file",
                  file=sys.stderr)
            sys.exit(1)

    try:
        width = int(data["WIDTH"])
        height = int(data["HEIGHT"])

        if width <= 0 or height <= 0:
            print("Error: Dimensions (WIDTH, HEIGHT) must be greater than 0.",
                  file=sys.stderr)
            sys.exit(1)

        entry_parts = data["ENTRY"].split(",")
        entry_x = int(entry_parts[0])
        entry_y = int(entry_parts[1])
        entry = (entry_x, entry_y)

        exit_parts = data["EXIT"].split(",")
        exit_x = int(exit_parts[0])
        exit_y = int(exit_parts[1])
        exit_coord = (exit_x, exit_y)

        if (entry_x < 0 or entry_x >= width or
                entry_y < 0 or entry_y >= height):
            print(f"Error: Entry {entry} is outside the maze boundaries.",
                  file=sys.stderr)
            sys.exit(1)

        if (exit_x < 0 or exit_x >= width or
                exit_y < 0 or exit_y >= height):
            print(f"Error: Exit {exit_coord} is outside the maze boundaries.",
                  file=sys.stderr)
            sys.exit(1)

        if entry == exit_coord:
            print("Error: entry and exit cannot be at the same coordinate.",
                  file=sys.stderr)
            sys.exit(1)

        perfect = data["PERFECT"].lower() == "true"
        output_file = data["OUTPUT_FILE"]
        seed = data.get("SEED")
        animation_wg = data.get("ANIMATION_WG")
        if animation_wg is not None:
            animation_wg = animation_wg.lower() == "true"
        return Config(width, height, entry, exit_coord,
                      perfect, output_file, seed, animation_wg)

    except Exception as e:
        print(f"Error: {type(e).__name__} - {e}")
        sys.exit(1)


def render_maze(grid: List[List[int]], width: int, height: int,
                entry: Tuple[int, int], exit: Tuple[int, int],
                seed_value: str, rotate: bool,
                path: Optional[List[Tuple[int, int]]] = None) -> None:
    """
    Render the maze in the terminal using ASCII characters and ANSI colors.
    """

    if not rotate:
        RESET = "\033[00m"
        BG_WALL = "\033[45m"       # Magenta
        BG_EMPTY = "\033[107m"      # White
        BG_PATH = "\033[42m"       # Green
        BG_ENTRY = "\033[104m"      # Blue
        BG_EXIT = "\033[41m"       # Red
        BG_42 = "\033[48;5;93m"  # Purple

        BLK_WALL = f"{BG_WALL}  {RESET}"
        BLK_EMPTY = f"{BG_EMPTY}  {RESET}"
        BLK_PATH = f"{BG_PATH}  {RESET}"
        BLK_ENTRY = f"{BG_ENTRY}  {RESET}"
        BLK_EXIT = f"{BG_EXIT}  {RESET}"
        BLK_42 = f"{BG_42}  {RESET}"
    else:
        RESET = "\033[00m"
        BG_WALL = "\033[40m"
        BG_EMPTY = "\033[100m"
        BG_PATH = "\033[42m"
        BG_ENTRY = "\033[104m"
        BG_EXIT = "\033[43m"
        BG_42 = "\033[41m"

        BLK_WALL = f"{BG_WALL}  {RESET}"
        BLK_EMPTY = f"{BG_EMPTY}  {RESET}"
        BLK_PATH = f"{BG_PATH}  {RESET}"
        BLK_ENTRY = f"{BG_ENTRY}  {RESET}"
        BLK_EXIT = f"{BG_EXIT}  {RESET}"
        BLK_42 = f"{BG_42}  {RESET}"

    path_set = set(path) if path else set()
    if path:
        path_set.add(entry)
        path_set.add(exit)

    print(f"\nDimensions: {width}x{height}, seed: {seed_value}")
    # Up border
    print(BLK_WALL + (BLK_WALL * 2) * width)

    for y in range(height):
        line_body: Any = BLK_WALL
        line_bottom: Any = BLK_WALL

        for x in range(width):
            val = grid[y][x]
            is_42 = (val == 15)

            # Central Bloc
            if (x, y) == entry:
                center_color = BLK_ENTRY
            elif (x, y) == exit:
                center_color = BLK_EXIT
            elif (x, y) in path_set:
                center_color = BLK_PATH
            elif is_42:
                center_color = BLK_42
            else:
                center_color = BLK_EMPTY

            line_body += center_color

            # Right
            if (val & 2) != 0:
                if is_42:
                    line_body += BLK_42  # If 42 purple
                else:
                    line_body += BLK_WALL
            else:  # Open wall
                # If in path green
                if (x, y) in path_set and (x + 1, y) in path_set:
                    line_body += BLK_PATH
                else:
                    line_body += BLK_EMPTY

            # South
            if (val & 4) != 0:
                if is_42:
                    line_bottom += BLK_42
                else:
                    line_bottom += BLK_WALL
            else:
                if (x, y) in path_set and (x, y + 1) in path_set:
                    line_bottom += BLK_PATH
                else:
                    line_bottom += BLK_EMPTY

            if is_42:
                line_bottom += BLK_42
            else:
                line_bottom += BLK_WALL

        print(line_body)
        print(line_bottom)


def main() -> None:

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
    rotate = False
    if config.seed is not None:
        seed_value = (config.seed)
    else:
        seed_value = str(random.randint(0, 10000000000))
    random.seed(seed_value)
    maze = MazeGenerator(config.width, config.height)
    if (config.animation_wg is True):
        for _ in maze.generate_maze_steps(config.entry, config.exit, config.perfect):
            render_maze(maze.grid, config.width, config.height,
                    config.entry, config.exit, seed_value,
                    rotate)
            print("\033[H\033[J", end="")
            time.sleep(0.01)
    else:
        maze.generate_maze(config.entry, config.exit, config.perfect)

    print(f"Saving to {config.output_file}...")
    path = maze.solve_maze(config.width, config.height,
                           config.entry, config.exit)

    maze.save_maze(config.output_file, path, config.entry, config.exit)

    # print(f"DONE! Solution found with {len(path)} steps.")
    render_maze(maze.grid, config.width, config.height,
                config.entry, config.exit, seed_value,
                rotate, path if show_path else None)

    while True:

        print("======== A-Maze-ing ========")
        print("1. Re-generate a new maze")
        print("2. Show/Hide path from entry to exit")
        print("3. Rotate maze colors")
        print("4. Quit")
        try:
            choice = (input("Choice (1-4): "))
        except Exception:
            print("Error: invalid input.")
            continue

        if choice == "1":
            if config.seed is not None:
                random.seed(config.seed)
            else:
                seed_value = str(random.randint(0, 10000000000))
                random.seed(seed_value)
                if (config.animation_wg is True):
                    for _ in maze.generate_maze_steps(config.entry, config.exit, config.perfect):
                        render_maze(maze.grid, config.width, config.height,
                                config.entry, config.exit, seed_value,
                                rotate)
                        print("\033[H\033[J", end="")
                        time.sleep(0.01)
                else:
                    maze.generate_maze(config.entry, config.exit, config.perfect)
            print(f"Saving to {config.output_file}...")
            path = maze.solve_maze(config.width, config.height,
                                config.entry, config.exit)
            render_maze(maze.grid, config.width, config.height,
                        config.entry, config.exit, seed_value,
                        rotate, path if show_path else None)

            maze.save_maze(config.output_file, path, config.entry, config.exit)

        if choice == "2":
            if show_path:
                show_path = False
            elif not show_path:
                show_path = True
            render_maze(maze.grid, config.width, config.height,
                        config.entry, config.exit, seed_value,
                        rotate, path if show_path else None)

        if choice == "3":
            if rotate:
                rotate = False
            elif not rotate:
                rotate = True
            render_maze(maze.grid, config.width, config.height,
                        config.entry, config.exit, seed_value,
                        rotate, path if show_path else None)

        if choice == "4":
            return


if __name__ == "__main__":
    main()
