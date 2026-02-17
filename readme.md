
__This project has been created as part of the 42 curriculum by nbarbosa and nbilyj.__

# A-Maze-ing

A-Maze-ing is a maze generator and solver written in Python. This project explores graph theory, procedural generation, and the creation of reusable Python packages. It allows for the generation of perfect or imperfect mazes, solving them via a shortest-path algorithm, and exporting the results in both text and visual formats.

## Description_

The program reads a configuration file, generates a maze based on specific constraints (dimensions, start/end points, loops), and produces two main outputs:

    Text File: Contains the hexadecimal representation of the maze and the cardinal solution (N, S, E, W).

    Visualization: A terminal render of the maze.

## Installation & Usage

### Makefile

A Makefile is included to automate common tasks:

    make install: Installs dependencies via pip.

    make run: Runs the main script with the default configuration.

    make lint: Checks code quality (Flake8 and strict MyPy).

    make clean: Removes temporary files and caches.

### Manual Execution

To run the generator with a specific config file:
```Bash
python3 a_maze_ing.py config.txt
```
### Configuration

The configuration file (config.txt) defines the maze parameters using a KEY=VALUE format.  
Lines starting with # are ignored.  

Key	Description	Example	Required  
WIDTH	Maze width (cells):						WIDTH=20  
HEIGHT	Maze height (cells):					HEIGHT=15  
ENTRY	Start coordinates (x,y):				ENTRY=0,0  
EXIT	End coordinates (x,y):					EXIT=19,14  
PERFECT	True for unique path, False for loops:	PERFECT=True  
OUTPUT_FILE	Output text filename:				OUTPUT_FILE=maze.txt  
SEED Random generation seed: 					SEED=123456    
Algorithms
Generation: Recursive Backtracker (DFS)

I chose the Recursive Backtracker algorithm.

    Aesthetics: Produces long, winding corridors with a low "river factor," making it harder for humans to solve.

    Connectivity: Mathematically guarantees that every cell is accessible (Perfect Maze).

    Implementation: Efficiently implemented using a standard stack structure.

Solver: Breadth-First Search (BFS)

I used BFS for the solver.

    Reasoning: Unlike DFS, which just finds a path, BFS guarantees finding the shortest path in an unweighted grid, which is a requirement for the optimal solution output.

Code Reusability

The core generation logic is encapsulated in the mazegen package located at the root. This module is standalone and designed to be imported into other projects. It can be built (wheel/tar.gz) using standard tools.

## Instructions

Usage Example:
Python

from mazegen.generator import MazeGenerator

# 1. Instantiate
maze = MazeGenerator(width=20, height=20)

# 2. Generate (Start at 0,0, End at 19,19, Perfect maze)
maze.generate_maze(entry=(0, 0), exit=(19, 19), perfect=True)

# 3. Access structure
print(maze.grid) 

# 4. Solve
path = maze.solve_maze(20, 20, (0, 0), (19, 19))

Features

    "42" Pattern: A dedicated algorithm embeds a solid "42" wall structure in the center of the maze (if dimensions allow).

    Custom Terminal Render: Colorized ASCII output handling walls, borders, and paths.

    Interactive Menu: Options to regenerate, toggle solution visibility, or rotate colors.

Project Info

    Author: nbarbosa, nbilyj

    QA Tools: Flake8, MyPy (strict).

Development Phases:

    Data structure & Config parsing.

    MazeGenerator (Backtracker) & Solver (BFS).

    "42" pattern integration & Hex output compliance.

    Refactoring into mazegen package & PEP8 cleanup.

## Resources

References:

    Mazes for Programmers by Jamis Buck.



AI Usage:


    Debugging complex MyPy strict typing errors.

    Mathematical optimization for image rendering (pixel coordinate calculations).

    Clarifying distinctions between generation neighbors and solution neighbors.

    Generating ASCII assets.

Note: The core algorithmic logic was implemented manually.