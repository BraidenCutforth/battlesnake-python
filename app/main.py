import bottle
import os
import random
import time
import Queue

current_milli_time = lambda: int(round(time.time() * 1000))

def BFS(board, head, goals, height, width):
    q = Queue.Queue()
    q.put([head['y'], head['x']])
    # visited = [[False for x in range(board_width)] for y in range(board_height)]
    paths = [[None for x in range(width)] for y in range(height)]
    while not q.empty():
        pos = q.get()
        adjacent = []
        adjacent.append([pos[0]-1, pos[1]])
        adjacent.append([pos[0]+1, pos[1]])
        adjacent.append([pos[0], pos[1]-1])
        adjacent.append([pos[0], pos[1]+1])
        for spot in adjacent:
            y, x = spot[0], spot[1]
            if(y>=0 and y<height and x>=0 and x<width and board[y][x]!=1):
                paths[y][x] = pos
                if board[y][x] in goals:
                    return [spot, paths]
                else:
                    board[y][x] = 1
                    q.put(spot)
    return None

def getMove(head, spot, paths):
    # print "Paths array:"
    # for x in paths:
    #     print x
    
    print "Target spot: ", spot
    print "Our head: ", head
    y = spot[0]
    x = spot[1]
    while paths[y][x] != head:
        temp = paths[y][x]
        print "Path pos: ", temp
        y = temp[0]
        x = temp[1]
    if(y == head[0]-1):
        return "up"
    elif(y == head[0]+1):
        return "down"
    elif(x == head[1]-1):
        return "left"
    else:
        return "right"
        

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
    board = [[0 for x in range(board_width)] for y in range(board_height)]
    ourLength = data['you']['length']
    ourHead = data['you']['body']['data'][0]
    print "Our Length: ", ourLength
    snakeData = data['snakes']['data']
    for snake in snakeData:
        length = snake['length']
        body = snake['body']['data']
        for part in body:
            x = part['x']
            y = part['y']
            # print y, x
            board[y][x] = 1
        if(length < ourLength):
            board[body[0]['y']][body[0]['x']] = 2
    foodData = data['food']['data']
    for food in foodData:
        x = food['x']
        y = food['y']
        board[y][x] = 2
    if data['you']['health'] < healthThreshold:
        goals = [2]
    else:
        goals = [2,3]
    plan = BFS(board, ourHead, goals, board_height, board_width)
    # for x in board:
    #     print x

    if plan != None:
        endTime = current_milli_time()
        print "Time: ", (endTime - startTime)
        direction = getMove([ourHead['y'],ourHead['x']], plan[0], plan[1])
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
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug = True)
