To run, make sure the .txt files and the maze_runner.py file are in the same directory. 
From your terminal, execute < python maze_runner.py maze_example.txt >. 
To generate a nice graphical representation of your maze + solution, run < open maze.png >.
You can switch from a depth-first search (DFS: last in, first out) breadth-first search (BFS: first in, first out) by changing the < frontier = StackFrontier() > to < frontier = Queue Frontier() > parameter in the solve() function on line 124. 
