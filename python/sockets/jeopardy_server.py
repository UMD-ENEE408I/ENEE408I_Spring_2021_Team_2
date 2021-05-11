#!/usr/bin/env python3
# Below is based heavily on the examples in:
# https://websockets.readthedocs.io/en/stable/intro.html

import asyncio
import json
import websockets
import random
import time
import operator
import random

USERS = set()
SCORE = {}
CONTROL = {}
BUZZED_DICT = {}
ORDER_DICT = {}
QUESTION = {}
round_number = 0

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


async def get_question(points, daily_double):
    global round_number 
    print("GET QUESTION")
        # find question with the proper point value, if not found keep looping
    while True:
        i = str(random.randint(0,len(jeopardy_dict)-1))
        if jeopardy_dict[i]["value"] == points:
            QUESTION['question'] = jeopardy_dict[i]['question']
            QUESTION['answer'] = jeopardy_dict[i]['answer']
            QUESTION['category'] = jeopardy_dict[i]['category']
            QUESTION['value'] = jeopardy_dict[i]['value']
            QUESTION['daily_double'] = daily_double
            QUESTION['round_number'] = round_number
            print("points: ", jeopardy_dict[i]["value"] )
            break

    # give all clients the question
    await send_to_all(json.dumps({"type": "question", "q_info": QUESTION}))
    


async def end_game(answer_dict): 
    await send_to_all(json.dumps({"type": "game over", "scores": SCORE, "final_answer": answer_dict}))

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
    if len(list(ORDER_DICT)) != 0:
        first = min(ORDER_DICT.items(), key=operator.itemgetter(1))[0]
        await send_to_all(json.dumps({"type": "prompt", "value": first}))
    # if all players pass
    else:
    # send answer to all players with who got the answer correct
        answer_dict = {"answer": QUESTION['answer'], "answered_by": "no one"}
        await send_to_all(json.dumps({"type": "control", "control info": CONTROL, "prev answer":answer_dict}))


async def check_answer(name, ans, GAME_LENGTH, daily_double):
    global round_number
    ans = ans.lower()
    replace_words = ["who is ", "what is ", "where is ", " the ", " a ", '?', '.', "who are ", "what are ", "where are "]
    for word in replace_words:
        ans = ans.replace(word, "")
    ans = ans.lstrip()
    ans = ans.rstrip()
    print(ans)
    # NOT COMMUNICATING QUESTIOn
    print(QUESTION['answer'])
    if ans == QUESTION['answer']:
        # if the answer is correct - add points and give control to the person who answered
        print("CORRECT")
        # check if this is the daily double round
        print(daily_double)
        print(round_number)
        if round_number == daily_double:
            dd_multiplier = 2
        else:
            dd_multiplier = 1
        # modify of the score of the player who got the question correct
        SCORE[name] = int(SCORE[name]) + int(QUESTION['value']) * dd_multiplier
        CONTROL['value'] = name
        print(SCORE)
        answer_dict = {"answer": QUESTION['answer'], "answered_by": name}
        if round_number < GAME_LENGTH: 
            # tell the clients who has control
            await send_to_all(json.dumps({"type": "control", "control info": CONTROL, "prev answer":answer_dict}))
            # clear these dicts for the next question
            BUZZED_DICT.clear()
            ORDER_DICT.clear()
            # QUESTION.clear()
        else :
            await end_game(answer_dict)
    else:
        # if the answer is incorrect - subtract points and leave control with whoever had it last
        print("INCORRECT")
        SCORE[name] = int(SCORE[name]) - int(QUESTION['value'])
        # remove name from buzzed and order dictionaties
        BUZZED_DICT.pop(name)
        ORDER_DICT.pop(name)
        print(SCORE)
        # if no one is left to answer
        if ORDER_DICT == {}:
            answer_dict = {"answer": QUESTION['answer'], "answered_by": "no one"}
            # send out the control of the board with the preev q's answer if not end of the game 
            if round_number < GAME_LENGTH: 
                # tell the clients who has control
                await send_to_all(json.dumps({"type": "control", "control info": CONTROL, "prev answer": answer_dict}))
                BUZZED_DICT.clear()
                ORDER_DICT.clear()
            else :
                await end_game(answer_dict)
            
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
            # print(message_dict['type'])

            # clients will send their name once the lobby is full
            if message_dict['type'] == 'name':
                #set some constants and globals :/
                GAME_LENGTH = 2
                daily_double = random.randint(1,GAME_LENGTH)
                # round_number = 0
                SCORE[message_dict['value']] = 0
                if len(SCORE) == len(USERS):
                    # Give initial control to the first person to submit their name
                    CONTROL['value'] = list(SCORE)[0]
                    await send_to_all(json.dumps({"type": "control", "control info": CONTROL, "prev answer": {}}))
                print(SCORE)

            # the client in control of the game selects a point value for the next question
            elif message_dict['type'] == 'points':
                global round_number
                round_number = round_number + 1
                # check if this is the daily double round
                if round_number == daily_double:
                    dd_string = "true"
                else:
                    dd_string = "false"
                await get_question(message_dict['value'], dd_string)
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
                await check_answer(message_dict['name'], message_dict['value'], GAME_LENGTH, daily_double)

            elif message_dict['type'] == 'ping':
                await send_to_all(json.dumps({"type": "ping"}))
                
                
    finally:
        await unregister(websocket)


start_server = websockets.serve(message_parse, '0.0.0.0', 5001)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()