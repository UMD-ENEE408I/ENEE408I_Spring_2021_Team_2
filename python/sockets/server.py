#!/usr/bin/env python3
# Below is based heavily on the examples in:
# https://websockets.readthedocs.io/en/stable/intro.html

import asyncio
import json
import websockets
import random
import time
import operator

USERS = set()
SCORE = {}
CONTROL = {}
QUESTION = {}
BUZZED_DICT = {}
ORDER_DICT = {}

async def notify_users():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = json.dumps({"type": "users", "count": len(USERS)})
        await asyncio.wait([user.send(message) for user in USERS])

async def register(websocket):
    print('REGISTER')
    USERS.add(websocket)
    await notify_users()
    if len(USERS) == 2:
        await send_to_all(json.dumps({"type": "start"}))

async def get_question(points):
    # load the questions json - maybe move this so the big json doesnt need to load every time
    questions_dict = json.load(open('questions.json'))
    filtDict = {}
    for key in questions_dict:
        if questions_dict[key]['points'] == int(points):
            filtDict[key] = {}
            filtDict[key]['answer'] = questions_dict[key]['answer']

    # select a random entry in the json - Im not sure if the big one is organized differently
    i = random.randint(0,len(filtDict)-1)
    q = list(filtDict)[i]

    # update the current question dictionary 
    # we need this to check the answer and update scores after a response is received
    QUESTION['answer'] = filtDict[q]['answer']
    QUESTION['points'] = int(points)

    await send_to_all(json.dumps({"type": "question", "value": q}))

async def send_to_all(msg):
    await asyncio.wait([user.send(msg) for user in USERS])

async def unregister(websocket):
    print('UNREGISTER')
    USERS.remove(websocket)
    await notify_users()

async def write_timestamp(name, buzz_tf):
    BUZZED_DICT[name] = {}
    if buzz_tf:
        t = time.localtime()
        float_time = t.tm_hour + t.tm_min/60 + t.tm_sec/3600
        ORDER_DICT[name] = float_time

async def prompt_first_buzzer():
    first = min(ORDER_DICT.items(), key=operator.itemgetter(1))[0]
    await send_to_all(json.dumps({"type": "prompt", "value": first}))

async def check_answer(name, ans):
    if ans == QUESTION['answer']:
        print("CORRECT")
        SCORE[name] = int(SCORE[name]) + int(QUESTION['points'])
        CONTROL['value'] = name
    else:
        print("INCORRECT")
        SCORE[name] = int(SCORE[name]) - int(QUESTION['points'])

    # await send_to_all({"type": "score", **SCORE})
    print(SCORE)
    BUZZED_DICT.clear()
    ORDER_DICT.clear()
    await send_to_all(json.dumps({"type": "control", **CONTROL}))
    print('sent control')

async def message_parse(websocket, path):
    # register(websocket) sends user_event() to websocket
    await register(websocket)
    try:
        async for message in websocket:
            message_dict = json.loads(message)
            print(message_dict['type'])
            if message_dict['type'] == 'name':
                SCORE[message_dict['value']] = 0
                if len(SCORE) == len(USERS):
                    # Give initial control to the first person to submit their name
                    CONTROL['value'] = list(SCORE)[0]
                    await send_to_all(json.dumps({"type": "control", **CONTROL}))
                print(SCORE)
            elif message_dict['type'] == 'points':
                await get_question(message_dict['value'])
                print(QUESTION)
                print(SCORE)
            elif message_dict['type'] == 'buzz':
                await write_timestamp(message_dict['name'], message_dict['value'])
                if len(BUZZED_DICT) == len(USERS):
                    await prompt_first_buzzer()
            elif message_dict['type'] == 'answer':
                await check_answer(message_dict['name'], message_dict['value'])
                
    finally:
        await unregister(websocket)


start_server = websockets.serve(message_parse, '0.0.0.0', 5001)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()