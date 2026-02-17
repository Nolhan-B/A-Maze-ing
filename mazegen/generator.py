
import random

class MazeGenerator:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = []
        self.visited = []
        self.path = []
        self.pattern = set()

        for y in range(height):
            new_line = []
            
            for x in range(width):
                new_line.append(15) 
            self.grid.append(new_line)

        for y in range(height):
            line_visited = []
            for x in range(width):
                line_visited.append(False)
            self.visited.append(line_visited)

    def neighbors(self, x, y)-> list:
        possible = []

        # North : (x, y - 1)
        # South : (x, y + 1)
        # East : (x + 1, y)
        # West : (x - 1, y)

        # Check North (y - 1)
        if y - 1 >= 0: 
            if self.visited[y - 1][x] == False:
                possible.append((x, y - 1))

        # Check South (y + 1)
        if y + 1 < self.height:
            if self.visited[y + 1][x] == False:
                possible.append((x, y + 1))

        # Check East (x + 1)
        if x + 1 < self.width:
            if self.visited[y][x + 1] == False:
                possible.append((x + 1, y))

        # Check West (x - 1)
        if x - 1 >= 0:
            if self.visited[y][x - 1] == False:
                possible.append((x - 1, y))

        return possible

    def dig_path(self, current_x, current_y, next_x, next_y)-> None:
        move_x = next_x - current_x
        move_y = next_y - current_y

        # Move to north
        if move_y == -1:
            self.grid[current_y][current_x] &= ~1  # Break north wall at current 
            self.grid[next_y][next_x] &= ~4  # Break south wall at next position

        # Move to south
        elif move_y == 1:
            self.grid[current_y][current_x] &= ~4  # Break south wall at current
            self.grid[next_y][next_x] &= ~1  # Break north wall at next position

        # Move to east
        elif move_x == 1:
            self.grid[current_y][current_x] &= ~2 # Break east wall at current
            self.grid[next_y][next_x] &= ~8 # Break west wall at next position

        # Move to west
        elif move_x == -1:
            self.grid[current_y][current_x] &= ~8 # Break west wall at current
            self.grid[next_y][next_x] &= ~2 # Break east wall at next position

    def generate_maze(self, entry, exit, perfect):
        # Algo Recursive Backtracker
        # Add the starting point to the visited area
        self.grid = []
        for y in range(self.height):
            new_line = []
            for x in range(self.width):
                new_line.append(15)
            self.grid.append(new_line)

        # On remet tous les visités à False
        self.visited = []
        for y in range(self.height):
            line_visited = []
            for x in range(self.width):
                line_visited.append(False)
            self.visited.append(line_visited)
            
        self.path = [] # On vide le chemin


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
                # As the current is visited the loop will choose another possibilities
                self.path.pop()

        # If the maze must not be perfect we break some wall
        if not perfect:
            self.imperfect()

    def save_maze(self, filename):

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
        except Exception as e:
            print(f"Writing error : {e}")


    def have_wall(self, x, y, direction):
        return (self.grid[y][x] & direction) != 0

    def draw42(self, entry, exit):

        self.pattern = set()
        if self.height < 16 or self.width < 16:
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
            print("Warning: 42 pattern overlaps with Entry/Exit. Skipping pattern.")
            self.pattern = set()
            return

        for wx, wy in walls:
            # Put a block at coordinates
            self.grid[wy][wx] = 15
    
            self.visited[wy][wx] = True


    def imperfect(self):

        # Arbitrary limit to wall breaking
        limit = (self.width * self.height) // 20
        count = 0

        east_wall = 2
        south_wall = 4
        west_wall = 8
        north_wall = 1

        while count < limit:
            random_x = random.randint(1, self.width - 2)
            random_y = random.randint(1, self.height - 2)
            choice = random.randint(0, 1)

            # Break east wall
            if choice == 0:
                if (random_x, random_y) not in self.pattern and (random_x + 1, random_y) not in self.pattern:

                    # Check this wall exist
                    if self.have_wall(random_x, random_y, east_wall):
                        self.grid[random_y][random_x] &= ~east_wall
                        self.grid[random_y][random_x + 1] &= ~west_wall
                        count += 1

            # Break south wall
            else:
                if (random_x, random_y) not in self.pattern and (random_x, random_y + 1) not in self.pattern:
                    
                    if self.have_wall(random_x, random_y, south_wall):
                        self.grid[random_y][random_x] &= ~south_wall
                        self.grid[random_y + 1][random_x] &= ~north_wall
                        count += 1
