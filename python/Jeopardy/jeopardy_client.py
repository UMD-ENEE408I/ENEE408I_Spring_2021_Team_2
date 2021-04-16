
from jeopardy import Jeopardy
from robot_chat_client import RobotChatClient
import asyncio
import json
import websockets
import threading
import time
import queue
from flask_ask import Ask, statement
from flask import Flask

server_ip = 'ws://localhost:5001'
# server_ip = 'ws://3.140.197.159:5001
app = Flask(__name__)
ask = Ask(app, '/')

def speak():
    speech_text= "i am speaking"
    return statement(speech_text).simple_card('my robot', speech_text)
    
@ask.intent('StartJeopardy')
def start_game(): 
    speech_text = 'Starting a game of Jeopardy'
    speak()
    return statement(speech_text).simple_card('my robot', speech_text)


alexa_say = lambda speech_text: statement(speech_text).simple_card('my robot', speech_text)

# ask intent for starting game
# ask int for setting points
# ask int for buzz

def extract_data(message_dict):
    print('Received dictionary {}'.format(message_dict))
    print('The message is type {}'.format(message_dict['type']))

    # type 0 handles message that want a voice response from the user
    if message_dict['type'] == '0':
        alexa_say(message_dict['voice'])
        print('Value of field voice: {}'.format(message_dict['voice']))
        # call code that does speech to text

    # type 1 handles non-resonse messages 
    if message_dict['type'] == '1':
        alexa_say(message_dict['voice'])
        print('Number of voice: {}'.format(message_dict['voice']))

# Run this script directly to invoke this test sequence
if __name__ == '__main__':
    app.run()
    # print('Creating RobotChatClient object')
    # client = RobotChatClient(server_ip, callback=extract_data)

    # time.sleep(1)
    # print('Sending a test message')
    # client.send({'type': 'test_message_type',
    #              'foo': [1, 2, 3, 4, 5]})

    # print('Waiting for ctrl+c')
