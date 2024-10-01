from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from components import create_battleships, place_battleships, initialise_board
from game_engine import attack, check_game_end
from mp_game_engine import generate_attack, players
import json

#app = Flask(__name__)
app = Flask(__name__)
app.config['SECRET_KEY'] = '1234'
socketio = SocketIO(app)

rooms = {}

#initialise an array that records the previous attacks of the ai, so that it doesn't attack the same coordinate multiple times
ai_previous_attacks = [(-1,-1)]
player_previous_attacks = [(-1,-1)]

def parse_shipdata(data):
    ship_lengths = create_battleships()
    new_board = initialise_board()

    for ship in data:
        if data[ship][2] == 'h':
            orientation = 'horizontal'
        else:
            orientation = 'vertical'
        
        ship_length = ship_lengths[ship]
        x = int(data[ship][0])
        y = int(data[ship][1])

        if orientation == 'horizontal':
            for i in range (ship_length):
                new_board[y][x+i] = ship
        elif orientation == 'vertical':
            for i in range (ship_length):
                new_board[y+i][x] = ship
        else:
            raise ValueError('orientation must be either vertical or horizontal')

    return new_board
  
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

# @app.route('/multiplayer')
# def index():
#     render_template('index.html')
games = {}

@app.route('/loadmultiplayer')
def render_multiplayer():
    p_board = place_battleships(board = initialise_board(), ships=create_battleships(), algorithm="Custom")
    return render_template('loadmultiplayer.html')
@socketio.on("connect")
def connect():
    print("connected")

@app.route('/load_game')
def load_game():
    gamecode = request.args.get('gamecode')
    playerid = request.args.get('playerid')
    
    print(f"Revieved gamecode: {gamecode}, playerid: {playerid}")
    print(f"Games: {games}")

    if gamecode not in games:
        games[gamecode] = {'joined':[playerid]}
        return render_template('waiting.html', gamecode = gamecode, playerid = playerid.strip())
    else:
        games[gamecode]['joined'].append(playerid)
        return render_template('mpplacement.html', gamecode = gamecode, playerid = playerid.strip(), ships = create_battleships(), board_size = 10)
    
@app.route('/mpplacement', methods = ['GET', 'POST'])
def mpplacement():
    if request.method == 'GET':
        gamecode = request.args.get('gamecode')
        playerid = request.args.get('playerid')
        return render_template('placementmp.html', gamecode = gamecode, playerid= playerid.strip(), ships = create_battleships(), board_size = 10)
    elif request.method == "POST":
        data = request.get_json()
        print(data)

        gamecode = str(data['gamecode'])
        playerid = str(data['playerid'])

        del data['gamecode']
        del data['playerid']

        ship_data = data
        games[gamecode][playerid] = [parse_shipdata(ship_data), create_battleships()]
        # print(" \n \n \n ship data added")
        # print(games[gamecode][playerid])
        # print("\n \n \n ")
        return jsonify({'success': True})
    
    else:
        return jsonify({'error': 'Invalid request method'}), 405
            
@app.route('/multiplayer') 
def multiplayer():
    gamecode = request.args.get('gamecode')
    playerid = request.args.get('playerid')

    return render_template('multiplayer.html', gamecode = gamecode, playerid = playerid.strip(), board_size = 10, player_board = games[gamecode][playerid.strip()][0])    

#@app.route('create_game')

@app.route('/attack', methods = ['POST'])
def handle_mp_attack():
    #data = request.get_json()
    
    # Access gamecode and playerid from the data dictionary
    # gamecode = data.get('gamecode')
    # playerid = data.get('playerid')
    # x = data.get('x')
    # y = data.get('y')

    print('\n\n\n')
    print('entering handle attack function')
    print('\n\n\n')

    gamecode = request.get_json()['gamecode']
    print('gamecode: ', gamecode)
    playerid = request.get_json()['playerid']
    print('playerid: ', playerid)
    x =  request.get_json()['x']
    print('x: ', x)
    y =  request.get_json()['y']
    print('y: ', y)

    print('\n\n\n')

    other_player = [i for i in games[gamecode]['joined'] if i != playerid][0]
    print('otherplayer id: ', other_player)
    # for i in games[gamecode]['joined']:
    #     if i!= playerid:
    #         other_player = i
    
    # other_player_data = games[gamecode].get(other_player)
    # if not other_player_data or len(other_player_data) < 2:
    #     return jsonify({'waiting': False, 'msg': 'opposition player hasn\'t places ships yet'})
    
    try:
        opp_board = games[gamecode][other_player.strip()][0]
        print('opponents board: ', opp_board)
        opp_ships = games[gamecode][other_player.strip()][1]
        print('opponents ships: ', opp_ships)
    except KeyError:
        return jsonify({'waiting': False, 'msg': 'opposition player hasn\'t places ships yet'})

    print('\n\n\n')

    player_hit = attack((y,x), opp_board, opp_ships)

    print('games[gamecode][playerid]: ', games[gamecode][playerid.strip()])
    print('\n\n\n')
    if len(games[gamecode][other_player.strip()]) < 3 :
        player_total_ship_amount = 0
        for key, value in games[gamecode][other_player.strip()][1].items():
            player_total_ship_amount= player_total_ship_amount + int(value)
        print(type(player_total_ship_amount))
        games[gamecode][other_player.strip()].append({'ship_amount': player_total_ship_amount})
    else:
        if player_hit:
            games[gamecode][other_player.strip()][2]['ship_amount'] = games[gamecode][other_player.strip()][2]['ship_amount'] -1 
    
    print('playerhit: ', player_hit)

    return_dict_player_hit = {'hit':player_hit}
    print('return player dictionary: ', return_dict_player_hit)
    print('\n\n\n')

    if 'hits' not in games[gamecode]:
        print('hits not in games dictionary')
        games[gamecode]['hits'] = {}
        games[gamecode]['hits'][playerid.strip()] = [x,y,player_hit]
        result = games[gamecode]['hits'][playerid.strip()] 
        print('games[gamecode][hits][playerid]: ', result)
        # return jsonify({'waiting': True})
    
    games[gamecode]['hits'][playerid.strip()] = [x,y,player_hit]
    result = games[gamecode]['hits'][playerid.strip()] 
    print('games[gamecode][hits][playerid]: ', result)
    print('\n\n\n\n\n\n')
    print('games[gamecode][\'hits\']', games[gamecode]['hits'])
    print('\n\n\n\n\n\n')

    
    if len(games[gamecode]['hits'])==2 or len(games[gamecode]['hits'])==3:
        #the "ai_turn" is just the term used by the frontend for the opposition move,
        #so each player will have eachothers attack data here
        return_dict_opp_hit = {}
        return_dict_opp_hit['AI_Turn'] = games[gamecode]['hits'][playerid.strip()][:2]
        return_dict_opp_hit['ai_hit'] = games[gamecode]['hits'][playerid.strip()][2]
        return_dict_opp_hit['hit'] =games[gamecode]['hits'][other_player.strip()][2]
        return_dict_opp_hit['x'] = games[gamecode]['hits'][other_player.strip()][0]
        return_dict_opp_hit['y'] = games[gamecode]['hits'][other_player.strip()][1]
        print('return_dict_opp_hit: ', return_dict_opp_hit)
        return_dict_player_hit['AI_Turn'] = games[gamecode]['hits'][other_player.strip()][:2]
        return_dict_player_hit['ai_hit'] = games[gamecode]['hits'][other_player.strip()][2]
        return_dict_player_hit['x'] = games[gamecode]['hits'][playerid.strip()][0]
        return_dict_player_hit['y'] = games[gamecode]['hits'][playerid.strip()][1]
        print('return_dict_player_hit: ', return_dict_player_hit)
        print('\n\n\n')

        print('opp_ships: ', opp_ships)
        print('player ships: ', games[gamecode][playerid.strip()][1])

        print('\n\n\n')

    #yes this is not the best way to do this, shhhhhhh
    #^^^ shushing is the most efficient programming paradigm
    

    print('player total ship amt: ', games[gamecode][playerid][2]['ship_amount']) 
    print('opp total ship amt: ', games[gamecode][other_player][2]['ship_amount'])

    print('\n\n\n')

    if  games[gamecode][other_player.strip()][2]['ship_amount'] == 0:
        return_dict_player_hit['finished'] = f'player {playerid} has won'
        return_dict_opp_hit['finished'] = f'player {playerid} has won'
    elif  games[gamecode][other_player.strip()][2]['ship_amount'] == 0:
        return_dict_player_hit['finished'] = f'Player {other_player} has won'
        return_dict_opp_hit['finished'] = f'Player {other_player} has won'

    print('emmiting socket')
    print({playerid: return_dict_player_hit})
    
    socketio.emit('attacksoc', {playerid.strip(): return_dict_player_hit, other_player.strip(): return_dict_opp_hit, 'room': gamecode})
    
        #clear hits data for the current game session
    del games[gamecode]['hits']

    return jsonify({'waiting': False})
    

if __name__ == '__main__':
   app.template_folder = 'templates'
   socketio.run(app, port = 5000)

   app.run(port = 5000)