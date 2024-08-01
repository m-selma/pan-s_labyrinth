import sys

###
class Node(): 
    def __init__(self, state, parent, action): # init: a constructor, is automatically invoked when a new instance of the class is created; initializes the attributes of the class with the values provided when creating an instance
        self.state = state
        self.parent = parent
        self.action = action

###
class StackFrontier(): # defines a StackFrontier class, which is designed to manage a collection of Node objects in a stack-like structure (last in, first out)
    def __init__(self):
        self.frontier = [] # initializes an empty list called frontier. This list will be used to store Node objects.
    
    def add(self, node):
        self.frontier.append(node) # takes a node as an argument and appends it to the frontier list. This adds a new node to the top of the stack

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier) # takes a state as an argument and checks if any node in the frontier list has this state. It returns True if such a node is found and False otherwise.
                                                                  # This is achieved using a generator expression that iterates through all nodes in the frontier and checks if node.state matches the given state.
    
    def empty(self):
        return len(self.frontier) == 0 # checks if the frontier list is empty

    def remove(self): # removing and returning the last added node, in LIFO fashion
        if self.empty():
            raise Exception("empty frontier")
        else: 
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1] # updates the frontier list to exclude the last node
            return node # returns the last node that was removed from the frontier 

###
class QueueFrontier(StackFrontier): # this class is inheriting from the StackFrontier class, meaning it does everything the same except how it's removing a node from the frontier from the beginning of the list, this time first in first out 
    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node

###
class Maze():
    def __init__(self, filename):
        # read file and set height and width of maze
        with open(filename) as f: 
            contents = f.read()

        # validate start and goal
        if contents.count("A") != 1:
            raise Exception("maze must have exactly one starting point")
        if contents.count("B") != 1:
            raise Exception("maze must have exactly one goal")
        
        # Determine height and width of maze
        contents = contents.splitlines() # splits a string into a list of lines.
        self.height = len(contents) # number of lines 
        self.width = max(len(line) for line in contents) # computes max length among all lines

        # Keep track of walls
        self.walls = [] # this list will eventually contain sublists that represent each row of the grid, indicating which cells are walls and which are not
        for i in range(self.height): # outer for loop iterates over the range of self.height, processing each row of the grid
            row = [] # For each row (i), an empty list row is initialized to keep track of which cells in that row are walls.
            for j in range(self.width): # The inner for loop iterates over the range of self.width, processing each column in the current row.
                try:
                    if contents[i][j] == "S":
                        self.start = (i, j)
                        row.append(False) # If the character at contents[i][j] is "A", it marks the start point. self.start is set to the tuple (i, j) indicating the coordinates of the start point. The corresponding cell is marked as not a wall by appending False to the row list.
                    elif contents[i][j] == "E":
                        self.goal = (i, j)
                        row.append(False)
                    elif contents[i][j] == " ":
                        row.append(False)
                    else:
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.walls.append(row) # After processing all columns in a row, the row list is appended to self.walls.

        self.solution = None


    def print(self):
        solution = self.solution[1] if self.solution is not None else None
        print()
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col: # meaning it's not zero, False, or an empty value
                    print("#", end="") # prints "â–ˆ" without a newline (because of end=""')
                elif (i, j) == self.start:
                    print("S", end="")
                elif (i, j) == self.goal:
                    print("E", end="")
                elif solution is not None and (i, j) in solution:
                    print("*", end="")
                else:
                    print(" ", end="")
            print() # After finishing each row of the grid, it prints a newline to move to the next row.
        print() # extra blank line after the grid


    def neighbors(self, state):
        row, col = state
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1))
        ]

        result = []
        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]: # This if condition checks if the new position (r, c) is within the valid boundaries of the grid and if it is not blocked by a wall.
                result.append((action, (r, c))) # If the new position (r, c) is valid and open, the code appends the (action, (r, c)) tuple to the result list. This tuple represents a valid move.
        return result

### the maze solver ###
    def solve(self):
        """Finds a solution to maze, if one exists."""

        # Keep track of number of states explored
        self.num_explored = 0

        # Initialize frontier to just the starting position
        start = Node(state=self.start, parent=None, action=None)
        frontier = StackFrontier()
        frontier.add(start)

        # Initialize an empty explored set
        self.explored = set()

        # Keep looping until solution found
        while True:

            # If nothing left in frontier, then no path
            if frontier.empty():
                raise Exception("no solution")

            # Choose a node from the frontier
            node = frontier.remove() # returns the last node added
            self.num_explored += 1

            # If node is the goal, then we have a solution
            if node.state == self.goal:
                actions = []
                cells = []

                # follow parent nodes to find solution
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return

            # Mark node as explored
            self.explored.add(node.state)

            # Add neighbors to frontier
            for action, state in self.neighbors(node.state): # for each neighbor, checks if the state is already in the frontier and in the explored set? If not, go ahead and add a child node
                if not frontier.contains_state(state) and state not in self.explored:
                    child = Node(state=state, parent=node, action=action)
                    frontier.add(child)

### generates a graphical representation of the maze and its solution 
    def output_image(self, filename, show_solution=True, show_explored=False):
        from PIL import Image, ImageDraw
        cell_size = 50
        cell_border = 2

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.width * cell_size, self.height * cell_size),
            "black"
        )
        draw = ImageDraw.Draw(img)

        solution = self.solution[1] if self.solution is not None else None
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):

                # Walls
                if col:
                    fill = (40, 40, 40)

                # Start
                elif (i, j) == self.start:
                    fill = (255, 0, 0)

                # Goal
                elif (i, j) == self.goal:
                    fill = (0, 171, 28)

                # Solution
                elif solution is not None and show_solution and (i, j) in solution:
                    fill = (220, 235, 113)

                # Explored
                elif solution is not None and show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85)

                # Empty cell
                else:
                    fill = (237, 240, 252)

                # Draw cell
                draw.rectangle(
                    ([(j * cell_size + cell_border, i * cell_size + cell_border),
                      ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)]),
                    fill=fill
                )

        img.save(filename)


if len(sys.argv) != 2:
    sys.exit("Usage: python maze.py maze.txt")

m = Maze(sys.argv[1])
print("Maze:")
m.print()
print("Solving...")
m.solve()
print("States Explored:", m.num_explored)
print("Solution:")
m.print()
m.output_image("maze.png", show_explored=True)
