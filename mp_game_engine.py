import random
import json
from components import initialise_board, create_battleships, place_battleships
from game_engine import cli_coordinates_input, attack, check_game_end

players = {}
previous_attacks = [(-1,-1)]
board_length = 10

def generate_attack() -> tuple():
    #because the name of the player is undefined in this function i need to access it from the dictionary itself to allow me to get the board length (without assuming it is the default value)
    board_length = 10 #len(players[list(players.keys())[0]][0]) 
    
    #initialise coords to the value already in previous_attacks
    coords = (-1,-1)
    
    while coords in previous_attacks:
        #generate random integers between zero and the board length -1
        x = random.randint(0, board_length-1)
        y = random.randint(0, board_length-1)
        coords = (x,y)

    return coords

def ai_opponent_game_loop():
    print("welcome to battleships")

    #get player and ai usernames
    player = input("enter your username: ")
    ai = "AI"

    #add player to the player dictionary
    player_ships = create_battleships()
    #player board is made according to the coordinates and orientation in a placement.json file
    player_board = place_battleships(board = initialise_board(board_length), ships=create_battleships(), algorithm="Custom")
    players[player] = [player_board, player_ships]

    #add ai to the player dictionary
    ai_ships = create_battleships()
    #place ships randomly on the ai's board
    ai_board = place_battleships(board=initialise_board(board_length), ships=create_battleships(), algorithm="Random")
    players[ai] = [ai_board, ai_ships]

    #initialise gameEnded to False
    gameEnded = False

    #loop until the game is ended
    while not gameEnded:
        #loop through each player in the player dictionary
        for p in list(players.keys()):
            #initialise coords variable to an empty tuple
            coords = ()

            #if the current player is the user (this means it is the ai's turn)
            if p == player:
                #generate the ai's attack
                coords = generate_attack()
                #print the ai attack coordinates
                print(coords)
                x = coords[0]
                y = coords[1]
                #initialise hit and miss messages
                hit_msg = "YOU'VE BEEN HIT!!!"
                miss_msg = "AI missed you!"
            elif p == ai:
                #if the current player is ai (this means it is the users turn)
                #input the users coordinates
                coords = cli_coordinates_input()
                x = coords[0]
                y = coords[1]
                #initialise hit and miss messages
                hit_msg = "HIT!!!"
                miss_msg = "miss :("
            
            #if the selected coordinate has been hit
            if attack(coords, players[p][0], players[p][1]):
                #print the initialised hit message
                print(hit_msg)

                cell = players[p][0][x][y]

                #set the hit cell, to a none value
                players[p][0][x][y] = None
                
                #decrement the length of the ship for the player who has been hit 
                players[p][1][cell] = players[p][1][cell] - 1
            
            #if the coordinates have not got a ship in them
            else:
                #print the initialised miss message
                print(miss_msg)
            
            #if the game has ended
            if check_game_end(players[p][1]):
                #initialise winner and loser name
                winner = ''
                loser = p
                
                #finding out the winner
                for p2 in list(players.keys()):
                    if not p2==p:
                        winner = p2
                        break

                #displaying "appropriate" message
                print(winner, " has won, player: ", loser , ", you lose!")
                gameEnded = True
            else:
                gameEnded = False




if __name__ == '__main__':
    ai_opponent_game_loop()
            