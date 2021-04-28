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
BUZZED_DICT = {}
ORDER_DICT = {}
QUESTION = {}
with open('/home/evan/ENEE408I_Spring_2021_Team_2/python/sockets/jp_questions.json') as questions_file:
    jeopardy_dict = json.load(questions_file)

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


async def send_to_all(msg):
    await asyncio.wait([user.send(msg) for user in USERS])


async def unregister(websocket):
    print('UNREGISTER')
    USERS.remove(websocket)
    await notify_users()


async def get_question(points):
    # find question with the proper point value, if not found keep looping
    while True:
        i = str(random.randint(0,len(jeopardy_dict)-1))
        if jeopardy_dict[i]["value"] == points:
            QUESTION['question'] = jeopardy_dict[i]['question']
            QUESTION['answer'] = jeopardy_dict[i]['answer']
            QUESTION['category'] = jeopardy_dict[i]['category']
            QUESTION['value'] = jeopardy_dict[i]['value']
            break

    # give all clients the question
    await send_to_all(json.dumps({"type": "question", "q_info": QUESTION}))


async def write_timestamp(name, buzz_tf):
    # record each player that buzzes (passes also count)
    BUZZED_DICT[name] = {}

    # only players that want to answer are added here
    if buzz_tf:
        t = time.localtime()
        float_time = t.tm_hour + t.tm_min/60 + t.tm_sec/3600
        ORDER_DICT[name] = float_time


async def prompt_buzzer():
    # ORDER_DICT has names as keys and timestamps as values
    # the key with the smallest value is the player that buzzed first - prompt them for an answer
    first = min(ORDER_DICT.items(), key=operator.itemgetter(1))[0]
    await send_to_all(json.dumps({"type": "prompt", "value": first}))


async def check_answer(name, ans):

    ans = ans.lower()
    replace_words = ["who is", "what is", "where is", " the ", " a "]
    for word in replace_words:
        ans = ans.replace(word, "")
    print(ans)
    print(QUESTION)
    # NOT COMMUNICATING QUESTIOn
    print(QUESTION['answer'])
    if ans == QUESTION['answer']:
        # if the answer is correct - add points and give control to the person who answered
        print("CORRECT")
        SCORE[name] = int(SCORE[name]) + int(QUESTION['value'])
        CONTROL['value'] = name
        # clear these dicts for the next question
        BUZZED_DICT.clear()
        ORDER_DICT.clear()
        QUESTION.clear()
        print(SCORE)
        # tell the clients who has control
        await send_to_all(json.dumps({"type": "control", **CONTROL}))
    else:
        # if the answer is incorrect - subtract points and leave control with whoever had it last
        print("INCORRECT")
        SCORE[name] = int(SCORE[name]) - int(QUESTION['value'])
        # remove name from buzzed and order dictionaties
        BUZZED_DICT.pop(name)
        ORDER_DICT.pop(name)
        print(SCORE)
        if ORDER_DICT == {}:
            # tell the clients who has control
            await send_to_all(json.dumps({"type": "control", **CONTROL}))
        else:
            await prompt_buzzer()
            
    # trying to send the scores out here gave me errors - i dont think you can send 2 messages in a row
    # await send_to_all({"type": "score", **SCORE}) 
    

    

# ----------- MAIN THING ----------- 
async def message_parse(websocket, path):
    # register(websocket) sends user_event() to websocket
    await register(websocket)
    try:
        async for message in websocket:
            # respond to the different types of messages that clients can send
            message_dict = json.loads(message)
            print(message_dict['type'])

            # clients will send their name once the lobby is full
            if message_dict['type'] == 'name':
                SCORE[message_dict['value']] = 0
                if len(SCORE) == len(USERS):
                    # Give initial control to the first person to submit their name
                    CONTROL['value'] = list(SCORE)[0]
                    await send_to_all(json.dumps({"type": "control", **CONTROL}))
                print(SCORE)

            # the client in control of the game selects a point value for the next question
            elif message_dict['type'] == 'points':
                await get_question(message_dict['value'])
                print(QUESTION)
                print(SCORE)

            # clients all send a buzz-type message after viewing the question
            # value is True if they wish to answer and False if they do not
            elif message_dict['type'] == 'buzz':
                await write_timestamp(message_dict['name'], message_dict['value'])
                if len(BUZZED_DICT) == len(USERS):
                    await prompt_buzzer()
            
            # the client that first buzzed will send and answer
            # in this current state, they are the only one to attempt the question (right or wrong we will go to the next question)
            elif message_dict['type'] == 'answer':
                await check_answer(message_dict['name'], message_dict['value'])
                
                
    finally:
        await unregister(websocket)


start_server = websockets.serve(message_parse, '0.0.0.0', 5001)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()