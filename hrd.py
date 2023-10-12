from copy import deepcopy
import copy
from heapq import heappush, heappop
import heapq
import time
import argparse
import sys
import os

#====================================================================================

char_goal = '1'
char_single = '2'

class Piece:
    """
    This represents a piece on the Hua Rong Dao puzzle.
    """

    def __init__(self, is_goal, is_single, coord_x, coord_y, orientation):
        """
        :param is_goal: True if the piece is the goal piece and False otherwise.
        :type is_goal: bool
        :param is_single: True if this piece is a 1x1 piece and False otherwise.
        :type is_single: bool
        :param coord_x: The x coordinate of the top left corner of the piece.
        :type coord_x: int
        :param coord_y: The y coordinate of the top left corner of the piece.
        :type coord_y: int
        :param orientation: The orientation of the piece (one of 'h' or 'v') 
            if the piece is a 1x2 piece. Otherwise, this is None
        :type orientation: str
        """

        self.is_goal = is_goal
        self.is_single = is_single
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.orientation = orientation

    def __repr__(self):
        return '{} {} {} {} {}'.format(self.is_goal, self.is_single, \
            self.coord_x, self.coord_y, self.orientation)
    
    #getters
    def get_is_goal(self): return self.is_goal
    def get_is_single(self): return self.is_single
    def get_coord_x(self): return self.coord_x
    def get_coord_y(self): return self.coord_y
    def get_orientation(self): return self.orientation
    
    #setters
    #only really need to set x and y coordinates of moved pieces
    def set_coords(self, x, y):
        self.coord_x = x
        self.coord_y = y
       

class Board:
    """
    Board class for setting up the playing board.
    """

    def __init__(self, pieces):
        """
        :param pieces: The list of Pieces
        :type pieces: List[Piece]
        """

        self.width = 4
        self.height = 5

        self.pieces = pieces

        # self.grid is a 2-d (size * size) array automatically generated
        # using the information on the pieces when a board is being created.
        # A grid contains the symbol for representing the pieces on the board.
        self.grid = []
        self.__construct_grid()

        
    def __construct_grid(self):
        """
        Called in __init__ to set up a 2-d grid based on the piece location information.

        """

        for i in range(self.height):
            line = []
            for j in range(self.width):
                line.append('.')
            self.grid.append(line)

        for piece in self.pieces:
            if piece.is_goal:
                self.grid[piece.coord_y][piece.coord_x] = char_goal
                self.grid[piece.coord_y][piece.coord_x + 1] = char_goal
                self.grid[piece.coord_y + 1][piece.coord_x] = char_goal
                self.grid[piece.coord_y + 1][piece.coord_x + 1] = char_goal
            elif piece.is_single:
                self.grid[piece.coord_y][piece.coord_x] = char_single
            else:
                if piece.orientation == 'h':
                    self.grid[piece.coord_y][piece.coord_x] = '<'
                    self.grid[piece.coord_y][piece.coord_x + 1] = '>'
                elif piece.orientation == 'v':
                    self.grid[piece.coord_y][piece.coord_x] = '^'
                    self.grid[piece.coord_y + 1][piece.coord_x] = 'v'

    def display(self, file):
        """
        Print out the current board.

        """
        for i, line in enumerate(self.grid):
            for ch in line:
                #print(ch, end='')
                file.write(f"{ch}")
            #print()
            file.write('\n')
            
    def print_piece_attribute(self, x_coordinate, y_coordinate):
        """
        prints the attributes of a piece given the top left coordinates of piece we want
        Args:
            x_coordinate (_type_): x_coordinate of top left piece
            y_coordinate (_type_):y_coordinate of top left peice

        Returns:
            _type_: list of attributes of the piece
        """
        for piece in self.pieces:
            if piece.coord_x == x_coordinate and piece.coord_y == y_coordinate:
                return piece
        
    def find_empty_pieces(self):
        """
        returns x and y coordinates of each of the 2 empty spaces. 
        
        """   
        spaces = []
        for i in range(5):
            for j in range(4):
                if (self.grid[i][j] == '.'):
                  spaces.append([j,i])
                         
        #print(len(self.grid))
        return spaces
            
    #helper function to check movable pieces to left of both spaces
    def check_left(self, movable_list, spaces):
        #check left of first space
        for i in range(2):
            if spaces[i][0] != 0: #if x coordinate of spaces is NOT on left puzzle edge
                #char_piece = self.grid[spaces[i][0]-1][spaces[i][1]] #could be '>', '2', '1', '^', 'v' 
                char_piece = self.grid[spaces[i][1]][spaces[i][0]-1]
                #print(char_piece)
                #if the left char piece is '>' then you know  piece is <> horizontal so top left coordinate is 2 to left of space
                if char_piece == '>':
                    top_left = [spaces[i][0]-2, spaces[i][1], "space_right", i]
                    movable_list.append(top_left)
                    
                #if left char piece is '2' then you know the coordinates
                elif char_piece == '2':
                    top_left = [spaces[i][0]-1, spaces[i][1], "space_right", i]
                    movable_list.append(top_left)
        
        #if its a vertical piece you need both spaces to be stacked and ajacent (if its a valid movable piece don't have to check 'v')
        #same with goal piece, its only movable on a left check if space 1 is on top of space 2 and is right of goal block
        if spaces[0][0] != 0 and spaces[1][0]!= 0:
            #char_piece = self.grid[spaces[0][0]-1][spaces[0][1]]
            char_piece = self.grid[spaces[0][1]][spaces[0][0]-1]
            if  char_piece == '^' and (spaces[0][0] == spaces[1][0] and spaces[0][1] == spaces[1][1]-1):
                top_left = [spaces[0][0]-1, spaces[0][1], "space_right", 0]
                movable_list.append(top_left)
                          
            if char_piece == '1' and self.grid[spaces[1][1]][spaces[1][0]-1]=='1': 
                top_left = [spaces[0][0]-2, spaces[0][1], "space_right", 0]
                movable_list.append(top_left)
                
         
        return movable_list
    
    #helper function to check movable pieces to right of both spaces
    def check_right(self, movable_list, spaces):
        #check right of space
        for i in range(2):
            if spaces[i][0] != 3: #if x coordinate of space 1 is NOT on right puzzle edge
                #char_piece = self.grid[spaces[i][0]+1][spaces[i][1]] #could be '<', '2', '1', '^', 'v' 
                char_piece = self.grid[spaces[i][1]][spaces[i][0]+1]
                #if right char piece is '2' or '<' then you know you are already right of the top left of the piece
                if char_piece == '2' or char_piece == '<':
                    top_left = [spaces[i][0]+1, spaces[i][1], "space_left", i]
                    movable_list.append(top_left)
        
        #for vertical or goal piece to be movable space 1 must be left of block AND space 2 must be under space 1
        if spaces[0][0] != 3 and spaces[1][0]!=3:
            char_piece = self.grid[spaces[0][1]][spaces[0][0]+1]
            if  char_piece == '^' and (spaces[0][0] == spaces[1][0] and spaces[0][1] == spaces[1][1]-1):
                top_left = [spaces[0][0]+1, spaces[0][1], "space_left", 0]
                movable_list.append(top_left)
            
            elif char_piece == '1' and self.grid[spaces[1][1]][spaces[1][0]+1]=='1':
                top_left = [spaces[0][0]+1, spaces[0][1], "space_left", 0]
                movable_list.append(top_left) 
        
        return movable_list
    
    #helper function to check movable pieces above a space
    def check_up(self, movable_list, spaces):
        for i in range(2):
            if spaces[i][1] !=0: #only look up if y_coord of spaces are NOT on row 1
                char_piece = self.grid[spaces[i][1]-1][spaces[i][0]]
                if char_piece == '2':
                    top_left = [spaces[i][0], spaces[i][1]-1, "space_below", i]
                    movable_list.append(top_left)
                elif char_piece == 'v':
                    top_left = [spaces[i][0], spaces[i][1]-2, "space_below", i]
                    movable_list.append(top_left)
        
        if spaces[0][1] !=0 and spaces[1][1]!=0:
            char_piece = self.grid[spaces[0][1]-1][spaces[0][0]]
            if char_piece == '<' and (spaces[0][0] == spaces[1][0]-1) and (self.grid[spaces[1][1]-1][spaces[1][0]] == '>') and (spaces[0][1]==spaces[1][1]) :
                top_left = [spaces[0][0], spaces[0][1]-1, "space_below" ,0]
                movable_list.append(top_left)
        
            elif char_piece == '1' and self.grid[spaces[1][1]-1][spaces[1][0]] == '1':
                top_left = [spaces[0][0], spaces[0][1]-2, "space_below", 0]
                movable_list.append(top_left)
                
        return movable_list
    
    #helper function to check movable pieces below a space
    def check_down(self, movable_list, spaces):
        for i in range(2):
            if spaces[i][1] !=4: #only look down if y_coord of spaces are NOT on row 4
                char_piece = self.grid[spaces[i][1]+1][spaces[i][0]]
                if char_piece == '2' or char_piece =='^':
                    top_left = [spaces[i][0], spaces[i][1]+1, "space_above", i]
                    movable_list.append(top_left)
        
        
        if spaces[0][1] !=4 and spaces[1][1]!=4:
            char_piece = self.grid[spaces[0][1]+1][spaces[0][0]]
            if (char_piece == '<') and (spaces[0][0] == spaces[1][0]-1) and (self.grid[spaces[1][1]+1][spaces[1][0]] == '>') and (spaces[0][1]==spaces[1][1]):
                top_left = [spaces[0][0], spaces[0][1]+1, "space_above", 0]
                movable_list.append(top_left)
        
            elif (char_piece == '1') and (self.grid[spaces[1][1]+1][spaces[1][0]] == '1'):
                top_left = [spaces[0][0], spaces[0][1]+1, "space_above", 0]
                movable_list.append(top_left)
                
        return movable_list
    
    
    def check_movable(self):
        """return a list of the movable pieces
        """
        # a piece is only movable if it neighbors an empty spot depending on the piece type
        #single piece only need to check if any 4 surrounding coordinates are empty
        #first fine empty coordinates
        spaces = self.find_empty_pieces()
        movable_list = list()
        self.check_left(movable_list, spaces)
        self.check_right(movable_list, spaces)
        self.check_up(movable_list, spaces)
        self.check_down(movable_list, spaces)
        #movable_list = self.remove_duplicates(movable_list)
        #print(movable_list)
        
        return movable_list, spaces          
         

class State:
    """
    State class wrapping a Board with some extra current state information.
    Note that State and Board are different. Board has the locations of the pieces. 
    State has a Board and some extra information that is relevant to the search: 
    heuristic function, f value, current depth and parent.
    """

    def __init__(self, board, f, depth, g, parent=None):
        """
        :param board: The board of the state.
        :type board: Board
        :param f: The f value of current state.
        :type f: int
        :param depth: The depth of current state in the search tree.
        :type depth: int
        :param parent: The parent of current state.
        :type parent: Optional[State]
        """
        self.board = board
        self.f = f
        self.depth = depth
        self.parent = parent
        self.g = g
        self.id = hash(board)  # The id for breaking ties.
    
    def __lt__(self, other):
        
        if self.f == other.f:
            return self.id < self.id

        return self.f < other.f
    
    def set_f(self, f): self.f = f    
    
    def heuristic(self, board):
        """
        function that takes a state and returns a state's heuristic value (h value) with manhattan distance
        distance of 2x2 piece and bottom opening. using top left corner
        """
        #xy coordinates of goal top left corner = [1,3]
        self.hval = 0 #place holder
        for i in board.pieces:
            if i.is_goal == True:
                self.hval = 0
                self.hval+= abs(i.coord_x - 1) #x distance from goal state
                self.hval+= abs(i.coord_y - 3) #y distance from goal state
        
        return self.hval
         
def goal_test(board):
    """
    function that takes a state and returns true if state is goal
    """
    for i in board.pieces:
        if i.is_goal == True and (i.coord_x == 1 and i.coord_y == 3):
            return True
            
    return False
    
def find_piece(pieces, movable_pieces, movable_piece_num):
    piece_id = 0
    for piece in pieces:
        #print(piece.coord_x, piece.coord_y)
        if piece.coord_x == movable_pieces[movable_piece_num][0] and piece.coord_y == movable_pieces[movable_piece_num][1]:
            return piece_id
        
        piece_id+=1
        
    return piece_id
        
def possible_moves(pieces, moavable_pieces,spaces):
    """This helper method takes in a movable piece and
    returns a list of "moves"/board configs for that piece. at most
    it would return 2 posibles moves for a piece

    Args:
        piece (piece): movable piece
    """
    #spaces = board.find_empty_pieces()
    successor_boards = list()
    
    for i in range(len(moavable_pieces)):
        piece_num = find_piece(pieces, moavable_pieces, i)
        pieces_copy = copy.deepcopy(pieces)
        #moving goal pieces
                
        if pieces_copy[piece_num].is_goal== True: #if movable piece is '1'
            
            #if goal piece is to the right of spaces
            if moavable_pieces[i][2] == "space_right":
                #set piece coordinates to space coords and return a board
                pieces_copy[piece_num].set_coords(spaces[0][0]-1, spaces[0][1])
                #generate a board
                new_board = Board(pieces_copy)
                successor_boards.append(new_board)
            #if goal piece is to the right of spaces
            elif moavable_pieces[i][2] == "space_left" or moavable_pieces[i][2] == "space_above":
                pieces_copy[piece_num].set_coords(spaces[0][0], spaces[0][1])
                new_board = Board(pieces_copy)
                successor_boards.append(new_board)
                
            elif moavable_pieces[i][2] == "space_below":
                pieces_copy[piece_num].set_coords(spaces[0][0], spaces[0][1]-1)
                new_board = Board(pieces_copy)
                successor_boards.append(new_board)
        
        #moving vertical pieces
        if pieces_copy[piece_num].orientation == 'v':
            if moavable_pieces[i][2] == "space_right" or moavable_pieces[i][2] == "space_left" :
                pieces_copy[piece_num].set_coords(spaces[0][0], spaces[0][1])
                new_board = Board(pieces_copy)
                successor_boards.append(new_board)
            
            elif moavable_pieces[i][2] == "space_above" and moavable_pieces[i][3]==0:
                pieces_copy[piece_num].set_coords(spaces[0][0], spaces[0][1])#CHANGED
                new_board = Board(pieces_copy)
                successor_boards.append(new_board)
            
            elif moavable_pieces[i][2] == "space_above" and moavable_pieces[i][3]==1:
                pieces_copy[piece_num].set_coords(spaces[1][0], spaces[1][1])#CHANGED
                new_board = Board(pieces_copy)
                successor_boards.append(new_board)
            
            elif moavable_pieces[i][2] == "space_below" and moavable_pieces[i][3] == 0:
                pieces_copy[piece_num].set_coords(spaces[0][0], spaces[0][1]-1)
                #print(spaces[0][1]+1)
                new_board = Board(pieces_copy)
                successor_boards.append(new_board)
                
            elif moavable_pieces[i][2] == "space_below" and moavable_pieces[i][3] == 1:
                pieces_copy[piece_num].set_coords(spaces[1][0], spaces[1][1]-1)
                new_board = Board(pieces_copy)
                successor_boards.append(new_board)
        
        #moving horizontal pieces
        if pieces_copy[piece_num].orientation == 'h':
            for k in range(2):
                if moavable_pieces[i][2] == "space_right" and moavable_pieces[i][3] == k:
                    pieces_copy[piece_num].set_coords(spaces[k][0]-1, spaces[k][1])
                    new_board = Board(pieces_copy)
                    successor_boards.append(new_board)
        
            for k in range(2):
                if moavable_pieces[i][2] == "space_left" and moavable_pieces[i][3] == k:
                    pieces_copy[piece_num].set_coords(spaces[k][0], spaces[k][1])
                    new_board = Board(pieces_copy)
                    successor_boards.append(new_board)
        
            if moavable_pieces[i][2] == "space_above" or moavable_pieces[i][2] == "space_below":
                pieces_copy[piece_num].set_coords(spaces[0][0], spaces[0][1])
                new_board = Board(pieces_copy)
                successor_boards.append(new_board)
            
        #moving single pieces
        if pieces_copy[piece_num].is_single:
            for k in range(2):
                if (moavable_pieces[i][2] == "space_right" or moavable_pieces[i][2] == "space_left" or moavable_pieces[i][2] == "space_above" or moavable_pieces[i][2] == "space_below" ) and moavable_pieces[i][3] == k:
                    pieces_copy[piece_num].set_coords(spaces[k][0], spaces[k][1])
                    new_board = Board(pieces_copy)
                    successor_boards.append(new_board)
            
    return successor_boards
            
def generate_successors(parent_state):
    """
    function that takes a state and returns a list of its successor states
    likely most complex function in program break down into several helper functions
    """
    #f cost is hval + however many states/moves you make which is incremented +=1 each time we pick a state
    movable_pieces, spaces = parent_state.board.check_movable() #TO DO RETURN THE 2 SPACE CORRDINATES
    #generate a list of all boards based on avaiable moves 
    successor_boards = possible_moves(parent_state.board.pieces, movable_pieces, spaces)
    if len(spaces) > 2:
        print(spaces)
        parent_state.board.display()
        print("")
        parent_state.parent.board.display()
        print(movable_pieces)
        sys.exit()
    
    #now create a list of state instinaces based on the sucessor boards 
    sucessor_states = list()
    
    for sus_board in successor_boards:
        sucessor = State(sus_board, parent_state.f+1, parent_state.depth+1 ,parent_state.g+1 , parent_state)
        h_val = sucessor.heuristic(sucessor.board)
        g_val = parent_state.g +1
        sucessor.set_f(h_val+ g_val)
        sucessor_states.append(sucessor)
        
    return sucessor_states
    
def get_solution(goal_state):
    """given a goal state, trace back parent states to get a solution and display/return sequence from initial to goal state

    Args:
        goal_state (State): the final state in which goal state is true after producing series of sucessors
    """
    solution = list() #list of solution states
    solution.append(goal_state)
    parent_state = goal_state.parent
    while parent_state!=None:
        solution.append(parent_state)
        parent_state = parent_state.parent
        
    return solution
     
def dfs(initial_state):
    """this function takes an initial state and returns the first solution found by DFS
    with multi path pruning
    """
    frontier = list()
    explored = set()
    
    frontier.append(initial_state)
    #expanded = 0
    while frontier!=0:
        #print(expanded)
        curr_state = frontier[-1] #select last in
        curr_explored = False
        frontier.pop(-1)
        curr_fields = frozenset((piece.is_goal, piece.is_single, piece.coord_x, piece.coord_y, piece.orientation) for piece in set(curr_state.board.pieces))
        
        if curr_fields in explored:
            curr_explored = True
        
        if curr_explored == False:
            explored.add(curr_fields)
            #expanded+=1
            if goal_test(curr_state.board) == True:
                return curr_state
            #curr_state.board.display()
            sucessors = generate_successors(curr_state) #expand current state and generate its successors
            #frontier.pop(-1) #remove last explanded state from frontier
            for sucessor in sucessors:
                frontier.append(sucessor)
                    
    return "no solution"       

def a_star(initial_state):
    frontier = list()
    explored = set()
    
    heapq.heappush(frontier, initial_state)
    
    #num_expanded = 0
    while frontier!=0:
        
        #num_expanded+=1
        #print(["num expanded:", num_expanded])
        curr_state = heapq.heappop(frontier)
        curr_explored = False
        #print(['f val', curr_state.f])
        curr_fields = frozenset((piece.is_goal, piece.is_single, piece.coord_x, piece.coord_y, piece.orientation) for piece in set(curr_state.board.pieces))
    
        if curr_fields in explored:
            curr_explored = True
        
        if curr_explored == False:
            explored.add(curr_fields)
            if goal_test(curr_state.board) == True:
                return curr_state
            
            sucessors = generate_successors(curr_state) #expand current state and generate its successors
            
            for sucessor in sucessors:
                heapq.heappush(frontier, sucessor)

def read_from_file(filename):
    """
    Load initial board from a given file.

    :param filename: The name of the given file.
    :type filename: str
    :return: A loaded board
    :rtype: Board
    """

    puzzle_file = open(filename, "r")

    line_index = 0
    pieces = []
    g_found = False

    for line in puzzle_file:

        for x, ch in enumerate(line):

            if ch == '^': # found vertical piece
                pieces.append(Piece(False, False, x, line_index, 'v'))
            elif ch == '<': # found horizontal piece
                pieces.append(Piece(False, False, x, line_index, 'h'))
            elif ch == char_single:
                pieces.append(Piece(False, True, x, line_index, None))
            elif ch == char_goal:
                if g_found == False:
                    pieces.append(Piece(True, False, x, line_index, None))
                    g_found = True
        line_index += 1

    puzzle_file.close()
    board = Board(pieces)
    #board.display()
    
    return board

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inputfile",
        type=str,
        required=True,
        help="The input file that contains the puzzle."
    )
    
    parser.add_argument(
        "--outputfile",
        type=str,
        required=True,
        help="The output file that contains the solution."
    )
    
    parser.add_argument(
        "--algo",
        type=str,
        required=True,
        choices=['astar', 'dfs'],
        help="The searching algorithm."
    )
    
    args = parser.parse_args()

    # read the board from the file
    board = read_from_file(args.inputfile)
    choice = args.algo
    outputfile = open(args.outputfile, "a")
    
    #init state constants: board read, depth = 0, parent = None, f value needs to be calculated given a board
    initial_state = State(board,0, 0, 0, None)
    
    dfs_goal = dfs(initial_state)
    astar_goal = a_star(initial_state)
    
    if choice == "astar":
        sol = get_solution(astar_goal)
        for i in reversed(sol):
            i.board.display(outputfile)
            outputfile.write("\n")
            #print("")
                 
    elif choice == "dfs":
        sol = get_solution(dfs_goal)
        for i in reversed(sol):
            i.board.display(outputfile)
            #print("")
            outputfile.write("\n")
        
    outputfile.close()
    