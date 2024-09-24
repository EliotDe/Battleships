from flask import Flask, render_template, jsonify, request
from components import create_battleships, place_battleships, initialise_board
from game_engine import attack, check_game_end
from mp_game_engine import generate_attack, players
import json

app = Flask(__name__)

#initialise an array that records the previous attacks of the ai, so that it doesn't attack the same coordinate multiple times
ai_previous_attacks = [(-1,-1)]
player_previous_attacks = [(-1,-1)]

#if a get request is made to the /attack route
@app.route('/attack', methods = ['GET'])
def process_attack():
    #if the request has arguments
    if request.args:
        #get the x and y arguments
        x = int(request.args.get('x'))
        y = int(request.args.get('y'))
        
        #put those variables into a tuple called coords
        coords = (x,y)

        #this returns a Truth value if the players selected cell has hit a ship on the ai's board
        player_atck = attack(coords, players["ai"][0], players["ai"][1])

        #if the player hit the ai's ship
        if player_atck == True:
            temp = players["ai"][0][x][y]
            #set the ship in that position to a None value
            players["ai"][0][x][y] = None
            #decrement the length of the ai's ship
            players["ai"][1][temp] -= 1 

        #initialise the ai attack coordinates to -1,-1
        #this is because (-1,-1) is initially in the ai_previous_attacks record
        ai_atck_coords = (-1,-1)

        #the ai selects random coordinates until they haven't already been attacked
        while ai_atck_coords in ai_previous_attacks:
            ai_atck_coords = generate_attack()
        
        #if the coordinate hasn't been attacked add it to the previously attacked record
        ai_previous_attacks.append(ai_atck_coords)

        #get x and y values
        x = ai_atck_coords[0]
        y = ai_atck_coords[1]

        #this returns a boolean for whether the ai's selected cell on the players board has a ship in it
        ai_atck = attack(ai_atck_coords, players["user"][0], players["user"][1] )
        
        #if the ai hit the users ship
        if ai_atck == True:
            temp = players["user"][0][x][y]
            #change the cell value to none
            players["user"][0][x][y] = None
            #decrement the users ship length
            players["user"][1][temp] -= 1 
        
        #the game has ended if either of the players have 0 ships left
        game_ended = check_game_end(players["ai"][1]) or check_game_end(players["user"][1])
        
        if game_ended: 
            return jsonify({"hit": player_atck, "AI_Turn": ai_atck_coords, "finished":"GAME OVER" })
        else:
            return jsonify({"hit": player_atck, "AI_Turn": ai_atck_coords})


@app.route('/', methods = ['GET'])
def root():
    #when a GET request is made to the / route
    
    #get the boards for the player and the ai
    p_board = place_battleships(board = initialise_board(), ships=create_battleships(), algorithm="Custom")
    ai_board = place_battleships(board = initialise_board(), ships=create_battleships(),  algorithm="Random")
    
    #add the players to the player dictionary
    players["user"] = [p_board, create_battleships()]
    players["ai"] = [ai_board, create_battleships()]
    
    #render the main.html template with the board being the player board
    return render_template("main.html", player_board = p_board )



@app.route('/placement', methods = ['GET','POST'])
def placement_interface():
    #initialise the ships variable
    ships = create_battleships()

    #if a GET request is made to the /placement route, render the template using the ships variable
    if request.method == 'GET':
        return render_template(template_name_or_list= 'placement.html', ships = ships, board_size = 10)

    #if a POST request is made
    if request.method == 'POST':
        #get the data(the ship locations on the board) as a json file
        data = request.get_json()

        #write the data to the saved placement.json file
        #this is what the custom placement method uses to place the battleships
        with open('placement.json','w') as outfile:
            json.dump(data, outfile)

        #return a success message
        return jsonify({"message":"success"})
   
    return

if __name__ == '__main__':
   app.template_folder = 'templates'
   app.run()