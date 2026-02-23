import random
from typing import List, Tuple, Set, Generator


class MazeGenerator:
    """
    Handles the generation and resolution of mazes
    """
    def __init__(self, width: int, height: int) -> None:
        """Initialize the maze generator with dimensions and empty grids."""
        self.width = width
        self.height = height
        self.grid: List[List[int]] = []
        self.visited: List[List[bool]] = []
        self.path: List[Tuple[int, int]] = []
        self.pattern: Set[Tuple[int, int]] = set()

        for y in range(height):
            new_line: List[int] = []

            for x in range(width):
                new_line.append(15)
            self.grid.append(new_line)

        for y in range(height):
            line_visited: List[bool] = []
            for x in range(width):
                line_visited.append(False)
            self.visited.append(line_visited)

    def neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """
        Find unvisited neighbors for the generation process
        (Recursive Backtracker).
        """
        possible: List[Tuple[int, int]] = []

        # North : (x, y - 1)
        # South : (x, y + 1)
        # East : (x + 1, y)
        # West : (x - 1, y)

        # Check North (y - 1)
        if y - 1 >= 0:
            if self.visited[y - 1][x] is False:
                possible.append((x, y - 1))

        # Check South (y + 1)
        if y + 1 < self.height:
            if self.visited[y + 1][x] is False:
                possible.append((x, y + 1))

        # Check East (x + 1)
        if x + 1 < self.width:
            if self.visited[y][x + 1] is False:
                possible.append((x + 1, y))

        # Check West (x - 1)
        if x - 1 >= 0:
            if self.visited[y][x - 1] is False:
                possible.append((x - 1, y))

        return possible

    def dig_path(self, current_x: int, current_y: int,
                 next_x: int, next_y: int) -> None:
        """
        Remove walls between the current cell and the next chosen cell.
        Updates the binary bitmask of both cells.
        """

        move_x = next_x - current_x
        move_y = next_y - current_y

        # Move to north
        if move_y == -1:
            self.grid[current_y][current_x] &= ~1  # Break north wall
            self.grid[next_y][next_x] &= ~4  # Break south wall at next pos

        # Move to south
        elif move_y == 1:
            self.grid[current_y][current_x] &= ~4  # Break south wall
            self.grid[next_y][next_x] &= ~1  # Break north wall at next pos

        # Move to east
        elif move_x == 1:
            self.grid[current_y][current_x] &= ~2  # Break east wall at current
            self.grid[next_y][next_x] &= ~8  # Break west wall at next position

        # Move to west
        elif move_x == -1:
            self.grid[current_y][current_x] &= ~8  # Break west wall at current
            self.grid[next_y][next_x] &= ~2  # Break east wall at next position

    def generate_maze_steps(
        self,
        entry: Tuple[int, int],
        exit: Tuple[int, int],
        perfect: bool
    ) -> Generator[List[List[int]], None, None]:
        """
        Generate a maze using the Recursive Backtracker algorithm.
        With a generator to allow animation during rendering.
        """
        # Add the starting point to the visited area
        self.grid = []
        for y in range(self.height):
            new_line = []
            for x in range(self.width):
                new_line.append(15)
            self.grid.append(new_line)

        self.visited = []
        for y in range(self.height):
            line_visited = []
            for x in range(self.width):
                line_visited.append(False)
            self.visited.append(line_visited)

        self.path = []

        self.draw42(entry, exit)
        start_x, start_y = entry
        self.visited[start_y][start_x] = True
        self.path.append((start_x, start_y))

        while len(self.path) > 0:
            # Get the current pos
            # [-1] is the lastpositional arg
            curr_x, curr_y = self.path[-1]

            # Check that we did'nt visited the neighbors already
            possibles = self.neighbors(curr_x, curr_y)

            # One possibilitie exist at least
            if len(possibles) > 0:
                next_x, next_y = random.choice(possibles)

                self.dig_path(curr_x, curr_y, next_x, next_y)

                # Next is now visited
                self.visited[next_y][next_x] = True

                # Add next to the path
                self.path.append((next_x, next_y))

                yield self.grid
            else:
                # No possibilities we go back
                # As the current is visited the loop will choose
                # another poss
                self.path.pop()

        # If the maze must not be perfect we break some wall
        if not perfect:
            self.imperfect()

    def generate_maze(self, entry: Tuple[int, int], exit: Tuple[int, int],
                      perfect: bool) -> None:
        # Algo Recursive Backtracker
        # Add the starting point to the visited area
        self.grid = []
        for y in range(self.height):
            new_line = []
            for x in range(self.width):
                new_line.append(15)
            self.grid.append(new_line)

        self.visited = []
        for y in range(self.height):
            line_visited = []
            for x in range(self.width):
                line_visited.append(False)
            self.visited.append(line_visited)

        self.path = []

        self.draw42(entry, exit)
        start_x, start_y = entry
        self.visited[start_y][start_x] = True
        self.path.append((start_x, start_y))

        while len(self.path) > 0:
            # Get the current pos
            # [-1] is the lastpositional arg
            curr_x, curr_y = self.path[-1]

            # Check that we did'nt visited the neighbors already
            possibles = self.neighbors(curr_x, curr_y)

            # One possibilitie exist at least
            if len(possibles) > 0:
                next_x, next_y = random.choice(possibles)

                self.dig_path(curr_x, curr_y, next_x, next_y)

                # Next is now visited
                self.visited[next_y][next_x] = True

                # Add next to the path
                self.path.append((next_x, next_y))
            else:
                # No possibilities we go back
                # As the current is visited the loop will choose another poss
                self.path.pop()

        # If the maze must not be perfect we break some wall
        if not perfect:
            self.imperfect()

    def path_to_cardinal(self, path: List[Tuple[int, int]]) -> str:
        """
        Convert a list of coordinates into a cardinal direction string
        (N, S, E, W).
        """
        if not path or len(path) < 2:
            return ""

        directions = ""
        for i in range(len(path) - 1):
            curr_x, curr_y = path[i]
            next_x, next_y = path[i + 1]

            if next_y < curr_y:
                directions += "N"
            elif next_x > curr_x:
                directions += "E"
            elif next_y > curr_y:
                directions += "S"
            elif next_x < curr_x:
                directions += "W"
        return directions

    def save_maze(self, filename: str, path: List[Tuple[int, int]],
                  entry: Tuple[int, int], exit: Tuple[int, int]) -> None:
        """
        Save the maze grid and solution to a text file.
        """
        try:
            with open(filename, "w") as f:
                for row in self.grid:
                    line_text = ""
                    for cell in row:
                        # Convert to hexadecimal (:X)
                        hexa_char = f"{cell:X}"

                        line_text = line_text + hexa_char

                    # Line finished we add it and pass to the next row
                    f.write(line_text + "\n")
                path_str = self.path_to_cardinal(path)

                f.write(f"\n{entry[0]},{entry[1]}\n")
                f.write(f"{exit[0]},{exit[1]}\n")
                f.write(path_str + "\n")
        except Exception as e:
            print(f"Writing error : {e}")

    def have_wall(self, x: int, y: int, direction: int) -> bool:
        """Check if a wall exists at (x, y) in the specified direction."""
        return (self.grid[y][x] & direction) != 0

    def draw42(self, entry: Tuple[int, int], exit: Tuple[int, int]) -> None:
        """
        Draw a '42' pattern of walls in the center of the maze.
        Checks if the maze is large enough and if entry/exit overlap.
        """

        self.pattern = set()
        if self.height < 9 or self.width < 9:
            print("Maze too small for the 42 pattern.")
            return

        cx = self.width // 2
        cy = self.height // 2

        pattern = [
            # 4
            (-3, -2), (-3, -1), (-3, 0),
            (-2, 0),
            (-1, 0), (-1, 1), (-1, 2),

            # 2
            (1, -2), (2, -2), (3, -2),
            (3, -1),
            (3, 0), (2, 0), (1, 0),
            (1, 1),
            (1, 2), (2, 2), (3, 2)
        ]

        walls = []
        for dx, dy in pattern:
            wx = cx + dx
            wy = cy + dy
            walls.append((wx, wy))
            self.pattern.add((wx, wy))

        # don't draw 42 if entry or exit is inside the 42
        if entry in walls or exit in walls:
            print("Warning: 42 pattern overlaps with Entry/Exit. "
                  "Skipping pattern.")
            self.pattern = set()
            return

        for wx, wy in walls:
            # Put a block at coordinates
            self.grid[wy][wx] = 15

            self.visited[wy][wx] = True

    def imperfect(self) -> None:
        """Randomly remove internal walls to create loops in the maze."""

        # Arbitrary limit to wall breaking
        if self.width <= 2 or self.height <= 2:
            print("Maze too small to be imperfect")
            return
        limit = (self.width * self.height) // 20
        count = 0
        max_attempts = limit * 10
        attempts = 0

        east_wall = 2
        south_wall = 4
        west_wall = 8
        north_wall = 1

        while count < limit and attempts < max_attempts:
            attempts += 1
            random_x = random.randint(1, self.width - 2)
            random_y = random.randint(1, self.height - 2)
            choice = random.randint(0, 1)

            # Break east wall
            if choice == 0:
                if ((random_x, random_y) not in self.pattern and
                        (random_x + 1, random_y) not in self.pattern):

                    # Check this wall exist
                    if self.have_wall(random_x, random_y, east_wall):
                        self.grid[random_y][random_x] &= ~east_wall
                        self.grid[random_y][random_x + 1] &= ~west_wall
                        count += 1

            # Break south wall
            else:
                if ((random_x, random_y) not in self.pattern and
                        (random_x, random_y + 1) not in self.pattern):

                    if self.have_wall(random_x, random_y, south_wall):
                        self.grid[random_y][random_x] &= ~south_wall
                        self.grid[random_y + 1][random_x] &= ~north_wall
                        count += 1

    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """
        Find accessible neighbors (respecting walls)
        for the solving process (BFS).
        """
        possible: List[Tuple[int, int]] = []

        value = self.grid[y][x]

        # North
        if y > 0 and (value & 1) == 0:
            possible.append((x, y - 1))

        # South
        if y < self.height - 1 and (value & 4) == 0:
            possible.append((x, y + 1))

        # East
        if x < self.width - 1 and (value & 2) == 0:
            possible.append((x + 1, y))

        # West
        if x > 0 and (value & 8) == 0:
            possible.append((x - 1, y))

        return possible

    def solve_maze(self, start: Tuple[int, int],
                   end: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Find the shortest path using Breadth-First Search (BFS).
        """

        map: List[List[int]] = []
        for y in range(self.height):
            line: List[int] = []
            for x in range(self.width):
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

            neighbors = self.get_neighbors(cx, cy)
            for x, y in neighbors:
                # -1 == not visited
                if map[y][x] == -1:
                    map[y][x] = map[cy][cx] + 1
                    queue.append((x, y))
        if not resolved:
            print("No solution found")
            return []

        # We found the exit, now we need to find the shortest path

        # Start from the end
        path = [end]
        cx, cy = end

        dist = map[cy][cx]

        while dist > 0:
            neighbors = self.get_neighbors(cx, cy)
            found = False
            for x, y in neighbors:
                if map[y][x] == dist - 1:
                    cx, cy = x, y
                    dist -= 1
                    path.append((x, y))
                    found = True
                    break

            if not found:
                break

        # We inverse the path
        return path[::-1]

    def solve_maze_steps(self, start: Tuple[int, int],
                         end: Tuple[int, int]
                         ) -> Generator[List[Tuple[int, int]], None, None]:
        """
        Find the shortest path using Breadth-First Search (BFS).
        """

        map: List[List[int]] = []
        for y in range(self.height):
            line: List[int] = []
            for x in range(self.width):
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

            neighbors = self.get_neighbors(cx, cy)
            for x, y in neighbors:
                # -1 == not visited
                if map[y][x] == -1:
                    map[y][x] = map[cy][cx] + 1
                    queue.append((x, y))
        if not resolved:
            print("No solution found")
            return

        # We found the exit, now we need to find the shortest path

        # Start from the end
        path = [end]
        cx, cy = end

        dist = map[cy][cx]

        while dist > 0:
            neighbors = self.get_neighbors(cx, cy)
            found = False
            for x, y in neighbors:
                if map[y][x] == dist - 1:
                    cx, cy = x, y
                    dist -= 1
                    path.append((x, y))
                    found = True
                    break

            if not found:
                break

        # We inverse the path
        final_path = path[::-1]

        for i in range(1, len(final_path) + 1):
            yield final_path[:i]
