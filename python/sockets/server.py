#!/usr/bin/env python

# WS server example that synchronizes state across clients

import asyncio
import json
import logging
import websockets
import random

logging.basicConfig()

STATE = {"value": 0}
SCORES = {}
QUESTION = {"answer": "", "points": ""}

USERS = set()

async def register(websocket):
    USERS.add(websocket)
    # get the users name - call for facial recognition?
    name = await websocket.recv()
    remote_ip =str(websocket.remote_address[0])

    # create entry for the new player in the current scores dictionary
    SCORES[remote_ip] = {}
    SCORES[remote_ip]['name'] = name
    SCORES[remote_ip]['score'] = 0
    print('registered')


async def unregister(websocket):
    # update the highscores/lifetime winnings JSON
    USERS.remove(websocket)


async def notify_score(websocket):
    # look in the current scores dict for the score of the connection that is asking
    remote_ip = str(websocket.remote_address[0])
    score = SCORES[remote_ip]['score']
    await websocket.send(score)


async def notify_question():
    # load the questions json - maybe move this so the big json doesnt need to load every time
    questions_dict = json.load(open('questions.json'))

    # select a random entry in the json - Im not sure if the big one is organized differently
    i = random.randint(0,len(questions_dict)-1)
    q = list(questions_dict)[i]

    # update the current question dictionary 
    # we need this to check the answer and update scores after a response is received
    QUESTION['answer'] = questions_dict[q]['answer']
    QUESTION['points'] = questions_dict[q]['points']

    # send the question to all connections
    await asyncio.wait([user.send(q) for user in USERS])


async def check_answer(websocket):
    # get the answer from the connection that buzzed first (have not put buzzing in yet)
    response = await websocket.recv()
    
    ip = websocket.remote_address[0]
    # if the response matches the dictionary answer, tell the it is correct and add proper points,
    # otherwise do the opposite
    if response == QUESTION['answer']:
        await websocket.send('correct')
        SCORES[ip]['score'] = int(SCORES[ip]['score']) + int(QUESTION['points'])
    else:
        await websocket.send('incorrect')
        SCORES[ip]['score'] = int(SCORES[ip]['score']) - int(QUESTION['points'])
    
    # tell the player that answered their new score
    await websocket.send(str(SCORES[ip]['score']))


async def consumer(websocket, message):
    # print(message)
    # react to the messages from the client
    if message == "score":
        await notify_score(websocket)
    elif message == 'question':
        print('asking question')
        await notify_question()
    elif message == "answer":
        await check_answer(websocket)

async def consumer_handler(websocket, path):
    # add the new connection to the list
    await register(websocket)
    print(USERS)
    async for message in websocket:
        await consumer(websocket, message)


start_server = websockets.serve(consumer_handler, "localhost", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()