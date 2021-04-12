#!/usr/bin/env python

# WS client example

import asyncio
import websockets
import json

async def get_user_input():
    # change to microphone
    message = input("plus or minus: ")
    return message


async def ask_server_for(websocket, server_request):
    # get a response from server for various things - 'score', 'question', more to be added?
    # server responds according to string input
    await websocket.send(server_request)
    server_msg = await websocket.recv()
    return server_msg


async def give_server_answer(websocket, answer):
    # tell the server you are sending an answer
    await websocket.send("answer")

    # send the answer
    await websocket.send(answer)

    # get the responses from server and return to the game loop
    correct = await websocket.recv()
    score = await websocket.recv()
    return correct, score


async def client_loop():
    uri = "ws://localhost:6789"
    async with websockets.connect(uri) as websocket:
        name = input("What is your name?: ")
        await websocket.send(name)
        while True: # GAME LOOP
            # do i have control? - if so decide point value
            # listen to question, print/speak to user
            # send buzz to server/see if someone else buzzed earlier - simultaneous
            # get answer from user and send to server
            # get correctness from server, tell all users who answered and if it was right


            # SIMPLE START
            # ask user if they want question or quit
            play = input("play or quit (p/q): ")
            if play == 'q':
                # can i break connection cleaner?
                break

            # get question and ask it
            question = await ask_server_for(websocket, 'question')
            print(question)

            # get user response - change to microphone
            resp = input("Your answer: ")

            # send response back and wait for correctness/ new score
            right_wrong, score = await give_server_answer(websocket, resp)

            # display correctness/new score - change to speaker
            print(right_wrong)
            print(score)


asyncio.get_event_loop().run_until_complete(client_loop())