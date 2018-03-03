import bottle
import os
import random
import time
import Queue

current_milli_time = lambda: int(round(time.time() * 1000))

def BFS(board, head, goals, height, width):
    q = Queue.Queue()
    q.put({'y':head['y'], 'x':head['x']})
    # visited = [[False for x in range(board_width)] for y in range(board_height)]
    paths = [[None for x in range(width)] for y in range(height)]
    while not q.empty():
        pos = q.get()
        # print "Pos1: ", pos
        adjacent = []
        adjacent.append({'y':pos['y']-1, 'x':pos['x']})
        adjacent.append({'y':pos['y']+1, 'x':pos['x']})
        adjacent.append({'y':pos['y'], 'x':pos['x']-1})
        adjacent.append({'y':pos['y'], 'x':pos['x']+1})
        for spot in adjacent:
            y, x = spot['y'], spot['x']
            if(y>=0 and y<height and x>=0 and x<width and board[y][x]!=1 and board[y][x]!=4):
                paths[y][x] = pos
                if board[y][x] in goals:
                    # print "Paths: "
                    # for t in paths:
                    #    print t
                    return [spot, paths]
                else:
                    board[y][x] = 1
                    q.put(spot)
    return None

def decideHead(snake, height, width):
    body = snake['body']['data']
    head = {'y':body[0]['y'],'x':body[0]['x']}
    neck = {'y':body[1]['y'],'x':body[1]['x']}
    moves = []
    moves.append({'y': head['y'],'x':head['x']-1})
    moves.append({'y': head['y'],'x':head['x']+1})
    moves.append({'y': head['y']-1,'x':head['x']})
    moves.append({'y': head['y']+1,'x':head['x']})
    for move in moves:
        if (not validMove(move, height, width)) or neck==move:
            # print "Removing: ", move
            # print "is neck:", neck==move
            moves.remove(move)
    return moves
    

def validMove(move, height, width):
    # print "height: ", height, " width: ", width
    # print ("Is this a valid move: "), move
    if(move['x']>=0 and move['x']<width and move['y']>=0 and move['y']<height):
        # print True
        return True
    # print False
    return False

def getMove(head, spot, paths):
    # print "Paths array:"
    # for x in paths:
    #     print x
    
    # print "Target spot: ", spot
    # print "Our head: ", head
    y = spot['y']
    x = spot['x']
    print "Head: ", head
    print "Spot: ", spot
    print "Paths is: ", paths[y][x] != None
    while paths[y][x]['y'] != head['y'] and paths[y][x]['x'] != head['x'] and paths[y][x] != None:
        temp = paths[y][x]
        print "Path pos: ", temp
        y = temp['y']
        x = temp['x']
    if(y == head['y']-1):
        return "up"
    elif(y == head['y']+1):
        return "down"
    elif(x == head['x']-1):
        return "left"
    else:
        return "right"
        
def buildBoard(data, width, height):
    board = [[0 for x in range(width)] for y in range(height)]
    ourLength = data['you']['length']
    ourID = data['you']['id']
    # print "Our Length: ", ourLength
    snakeData = data['snakes']['data']
    for snake in snakeData:
        length = snake['length']
        body = snake['body']['data']
        health = snake['health']
        # Mark all the body pieces as occupied
        for part in body:
            x = part['x']
            y = part['y']
                # print y, x
            board[y][x] = 1
        # Mark tails as dangerous if the tail wont grow
        if health < 100:
            board[body[-1]['y']][body[-1]['x']] = 4
        #If our snake continue
        if snake['id'] == ourID:
            continue
        # If we are bigger mark possible enemy head locations
        # Else mark the spots around enemy head as dangerous
        # print "There length: ", length
        moves = decideHead(snake, height, width)
        if(length < ourLength):
            for move in moves:
                if board[move['y']][move['x']] != 1:
                    board[move['y']][move['x']] = 3
        else:
            # print "Moves: ", moves
            for move in moves:
                if board[move['y']][move['x']] != 1:
                    board[move['y']][move['x']] = 4
            

    foodData = data['food']['data']
    for food in foodData:
        x = food['x']
        y = food['y']
        if board[y][x] != 4:
            board[y][x] = 2
    return board

def DFS(board, head, height, width):
    print "DFS!"
    q = Queue.LifoQueue()
    q.put({'y':head['y'], 'x':head['x'], 'depth':1})
    # visited = [[False for x in range(board_width)] for y in range(board_height)]
    paths = [[None for x in range(width)] for y in range(height)]
    while not q.empty():
        pos = q.get()
        adjacent = []
        adjacent.append([pos['y']-1, pos['x']])
        adjacent.append([pos['y']+1, pos['x']])
        adjacent.append([pos['y'], pos['x']-1])
        adjacent.append([pos['y'], pos['x']+1])
        for spot in adjacent:
            y, x = spot[0], spot[1]
            if(y>=0 and y<height and x>=0 and x<width and board[y][x]!=1):
                paths[y][x] = pos;
                board[y][x] = 1
                q.put({'y':y, 'x':x, 'depth':pos['depth']+1})
    depth = 0
    path = None
    for y in range(height):
        for x in range(width):
            if paths[y][x]['depth'] > depth:
                depth = paths[y][x]['depth']
                path = paths[y][x]

    return path

@bottle.route('/')
def static():
    return "the server is running"


@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():
    data = bottle.request.json
    game_id = data.get('game_id')
    board_width = data.get('width')
    board_height = data.get('height')
    print "START"
    print board_width
    print board_height
    print "END"
    head_url = '%s://%s/static/head.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    # TODO: Do things with data
    return {
        'color': '#00FF00',
        'taunt': '{} ({}x{})'.format(game_id, board_width, board_height),
        'head_url': head_url
    }


@bottle.post('/move')
def move():
    startTime = current_milli_time()
    healthThreshold = 30
    data = bottle.request.json
    board_height = data['height']
    board_width = data['width']
    ourHead = data['you']['body']['data'][0]
    board = buildBoard(data, board_width, board_height)
    # print board
    for x in board:
        print x
    if data['you']['health'] < healthThreshold:
        goals = [2]
    else:
        goals = [2,3]
    plan = BFS(board, ourHead, goals, board_height, board_width)

    if plan != None:
        endTime = current_milli_time()
        print "Time: ", (endTime - startTime)
        # print "Plan!!!", plan
        direction = getMove(ourHead, plan[0], plan[1])
        print "Chosen move: ", direction
        return{
            'move': direction
        }
    else:
        directions = ['up', 'down', 'left', 'right']
        direction = random.choice(directions)
        print "Random move:", direction
        return {
            'move': direction,
        }

@bottle.post('/end')
def end():
    print "Match ended"
    return {}
# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    board_width = 0
    board_height = 0
    bottle.run(
        application,
        host=os.getenv('IP', '192.168.96.122'),
        port=os.getenv('PORT', '8080'),
        debug = True)
