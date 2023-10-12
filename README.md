# Hua_Rong_Dao_PuzzleSolver
This is a puzzle solver written in Python that takes in an input file representing a hao rong dao puzzle and solves it comparatively using either depth-first search (dfs) or A* search algorithm. The output is a series of steps to solve the puzzle. A* method can typically solve all puzzles within seconds. 

The puzzle board is four spaces wide and five spaces tall. We consider the variants of this puzzle with ten pieces. There are four kinds of pieces:

One 2x2 piece.
Five 1x2 pieces. Each 1x2 piece can be horizontal or vertical.
Four 1x1 pieces.
Once we place the ten pieces on the board, two empty spaces should remain.

Look at the most classic initial configuration of this puzzle below. In this configuration, one 1x2 piece is horizontal, and the other four 1x2 pieces are vertical.

![image](https://github.com/danielrafiqueUtoronto/Hua_Rong_Dao_PuzzleSolver/assets/79722816/e1a85d21-8141-48d5-b8c0-edd734bf9178)


The goal is to move the pieces until the 2x2 piece is above the bottom opening (i.e. helping Cao Cao escape through the Hua Rong Dao/Pass). You may move each piece horizontally or vertically only into an available space. You are not allowed to rotate any piece or move it diagonally.

To Run this code use the following inputs:

python3 hrd.py --algo astar --inputfile <input file> --outputfile <output file>    
python3 hrd.py --algo dfs --inputfile <input file> --outputfile <output file>

Sample input files are provided for testing and should produce the provided solution files. 
