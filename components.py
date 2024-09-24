import random
import json

def initialise_board(size = 10) -> list[list[str]]:
    #initialise the board to an empty array
    board = []

    #make the array two dimensional size 10x10 and fill it with None values
    for i in range(size):
        board.append([])
        for j in range(size):
            board[i].append(None)
    
    
    return board
    
  

def create_battleships(filename = "battleships.txt") -> dict[str, int]:
    #initialise battleships dictionary
    battleships = {}
    
    #open the file (read-only) and read all the lines in it
    file = open(filename,'r')
    lines = file.readlines()

    #for each line in the file
    for line in lines:
        #get the index of the colon
        i = line.index(':')
        #get the substring up to the colon, representing the ship name
        ship = line[:i]    
        #get the substring after the colon, representing the ship length and convert it to an integer
        length = int(line[i+1:])
        #add to the dictionary a key value pair where k = ship name and v = ship length
        battleships[ship] = length

    return battleships

#take the player board, ships and place the ships on the board according to the specified method of placement
def place_battleships(board, ships, algorithm = "Simple") -> list[list[str]]:
    #board = initialise_board()
    #ships = create_battleships()
    
    if algorithm == "Custom":
        return place_custom(board, ships)
    elif algorithm == "Random":
        return place_random(board, ships)
    elif algorithm == "Simple":
        return place_simple(board, ships)
    
    return(board)

#this places the head of each ship at the left side of each row on the board
def place_simple(board, ships):
    i= 0
    #for each ship in the list of ships
    for ship in list(ships.keys()):
        #change the cell (board[j][i]) to the ship key for the length of the ship
        for j in range(ships[ship]):
            board[j][i] = ship
        
        #increment the row index
        i+=1
    return board

def place_random(board, ships):
    ship_orientations = ['v', 'h']
    shipArr = list(ships.keys()) # add try catch here

    for ship in shipArr:
        
        #initialise ship clash to True
        ship_clash = True

        #loop until the random coordinates don't clash with an already placed ship
        while ship_clash == True:

            #select random x value between 0 and (length of the board subtract ship length)
            #this is to stop the random value from placing the ship outside the bounds of the board
            x = random.randint(0, len(board) - ships[ship])
            #select random y value between 0 and (length of the board subtract ship length)
            #same reason why
            y = random.randint(0, len(board)- ships[ship])
            #select random ship orientation
            orientation = ship_orientations[random.randint(0,1)]

            if orientation == 'v':

                #loop through the squares where the ship will be placed and check if a ship is already there
                #if there is a ship break out of the for loop and continue through the while loop

                for i in range(ships[ship]):
                    #if there is a ship break out of the for loop
                    if  not (board[y+i][x] == None):
                        ship_clash = True
                        break
                    else:
                        ship_clash = False

                #if there is a ship clash select another set of random values by looping
                if ship_clash == True:
                    continue

                #if there isn't place the ships going from the head of the ships coordinates and downwards for the length of the ship
                else:
                    for i in range(ships[ship]):
                        board[y+i][x] = ship

            elif orientation == 'h':
                for i in range(ships[ship]):
                    if  not (board[y][x+i] == None):
                        ship_clash = True
                        break
                    else:
                        ship_clash = False
                
                #if there is a clash loop
                if ship_clash == True:
                    continue
                
                #if there isn't place the ship from the coordinates of the head of the ship, and to the right of the head for the length of the ship
                else:
                    for i in range(ships[ship]):
                        board[y][x+i] = ship

    return board

def place_custom(board, ships):
    #open the placement.json file, read-only and load the data into a dictionary
    f = open('placement.json', 'r')
    data = json.load(f)

    #iterate through each ship in the dictionary
    for ship in list(data.keys()):
        #get ship length and coordinates and ship orientation
        ship_length = ships[ship]
        x = int(data[ship][0])
        y = int(data[ship][1])
        orientation = data[ship][2]

        if orientation == 'h':
            #if the orientation is horizontal place the ship going from the head coordinate and right
            for i in range(ship_length):
                board[y][x+i] = ship
        elif orientation == 'v':
            #if the orientation is vertical place the ship going from the head coordinate and down
            for i in range(ship_length):
                board[y+i][x] = ship
        
        board[y][x] = ship

    #print(board)

    return board
