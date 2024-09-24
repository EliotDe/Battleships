
from components import initialise_board, create_battleships, place_battleships

board_length = 10

#function takes attack coordinates and a board, checks to see if there is a ship in the given coordinates of the given board, if there is it returns a hit
def attack(coordinates, board, battleships) -> bool:
    
    hit = False

    x = coordinates[0]
    y = coordinates[1]

    cell = board[x][y]

    # if there is a battleship in the cell, that is part of the list of battleships and isn't supposed to be sunk, then the ship has been hit
    if (not (cell== None)) and  (cell in list(battleships.keys())) and (battleships[cell] > 0):
        return True
    
    return hit

#user inputs coordinates as a two digit string, it is converted to an integer, each digit is put into a tuple and the tuple is returned
def cli_coordinates_input() -> tuple():
    while True:
        try:
            coordinatesString = input("enter coordinates for an attack e.g. 00, 12:  ")
            if len(coordinatesString) != 2:
                raise ValueError
            x=int(coordinatesString[0])
            y=int(coordinatesString[1])
            if not (0<= x <=board_length) or not(0<=y<=board_length):
                raise ValueError
            coordinates = (x, y) 
            return coordinates
        except (ValueError, KeyError, TypeError):
            print("Incorrect format, input coordinates again (00, 12)")


#main game loop
def simple_game_loop():
    #initialise game ended to false, to allow the while loop to be entered
    gameEnded = False

    welcome = "----------------WELCOME TO BATTLESHIPS, ENJOY :)-------------------"
    print(welcome)

    #Initialise board to empty values
    #Create the dictionary of battleships (and battleship lengths)
    #Place ships on the board according to the simple placement algorithm
    battleships = create_battleships()
    board = place_battleships(board = initialise_board(board_length), ships=create_battleships)

    #while the game hasn't finished repeat the main functions of the game
    while not gameEnded:
        #user inputs coordinates, coords is a tuple
        coords = cli_coordinates_input()
        x = coords[0]
        y = coords[1]

        #if the attack has hit a battleship:
        #   decrement the length of the ship it has hit in the battleships dictionary
        #   change the value of the cell in the ship to NONE
        if attack(coords, board, battleships):
            cell = board[x][y]
            board[x][y] = None
            battleships[cell] = battleships[cell] - 1

        #check if the game end criteria is met
        gameEnded = check_game_end(battleships)

    print("Game Finished :)")


#additional function for checking game end criteria
#makes for more reusable code (prevents repetative code) because this will be used a lot in other parts of the code
def check_game_end(battleships) -> bool:
    #battleship countinitialised to zero
    bcount = 0

    #iterate through each of the keys in the dictionary
    for b in list(battleships.keys()):
        #if the ship is still on the board increment the ship count
        if battleships[b] >0:
            bcount+=1
    #if there are no ships left on the board, the game is finished
    if bcount == 0:
        return True

    return False


if __name__ == '__main__':
    simple_game_loop()
