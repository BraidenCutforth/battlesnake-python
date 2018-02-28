import bottle
import os
import random

board_width = 0
board_height = 0

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
    board = [[0 for x in range(board_height)] for y in range(board_width)] 
    data = bottle.request.json
    ourLength = data.get('you').get('length')
    snakes = data.get('snakes')
    snakeData = snakes.get('data')
    for snake in snakeData:
        length = snake.get('length')
        body = snake.get('body').get('data')
        for part in body:
            x = part.get('x')
            y = part.get('y')
            board[x][y] = 1
        if(length < ourLength):
            board[body[0].get('x')][body[0].get('y')] = 2


    # TODO: Do things with data
    print data
    directions = ['up', 'down', 'left', 'right']
    direction = random.choice(directions)
    print direction
    return {
        'move': "up",
    }


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug = True)
