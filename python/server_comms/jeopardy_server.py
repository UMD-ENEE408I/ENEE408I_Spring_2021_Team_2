# Handles server and client interaction for the jeopardy game
from jeopardy import Jeopardy
import asyncio
import json
import websockets


USERS = set()

async def notify_users():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = json.dumps({"type": "users", "count": len(USERS)})
        await asyncio.wait([user.send(message) for user in USERS])

async def register(websocket):
    print('REGISTER')
    USERS.add(websocket)
    await notify_users()


async def unregister(websocket):
    print('UNREGISTER')
    USERS.remove(websocket)
    await notify_users()

async def one_to_all(websocket, path):
    # register(websocket) sends user_event() to websocket
    await register(websocket)
    try:
        async for message in websocket:
            # Hack due to infamiliarity with asyncio
            # List of sockets that are not this socket
            to_notify = [user for user in USERS if user != websocket]
            # If there is anyone to notify, notify all
            if to_notify:
                await asyncio.wait([user.send(message) for user in to_notify])
    finally:
        await unregister(websocket)

##### Server Notes #####
def ask_point_value(self, client_id):
    # ask client for point value
    # receive point value and set question_point_vlaue
    return

def ask_question(question_string, client_ids):
    # send question to all 3 clients
    pass

def game_loop(game):
    control_player = game.set_control_player()
    game.question_point_value = ask_point_value()
    # get quesrion and ask
    # looks for first buzzage


start_server = websockets.serve(one_to_all, '0.0.0.0', 5001)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
game = Jeopardy()
 