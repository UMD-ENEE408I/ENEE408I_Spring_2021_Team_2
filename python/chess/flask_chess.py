from flask import Flask
from flask_ask import Ask, statement, question, convert_errors
import os
from chess_thread import ChessThread
from chess_vision import ChessCamera

app = Flask(__name__)
ask = Ask(app, '/')

# Start chess sequence
@ask.intent('ChessIntent')
def play_chess():
    global chess_inst
    global camera
    chess_inst = ChessThread(camera)
    text = "What skill level would you like to play against?"
    return question(text).simple_card('my robot', text)

# set level for chess game
@ask.intent('LevelIntent', convert={'level': int})
def set_level(level):
    if 'level' in convert_errors:
        return question("Can you please repeat the level?")
    print(level)
    global chess_inst
    chess_inst.set_level(level)
    text = "What color would you like to play as?"
    return question(text).simple_card('my robot', text)

# set player color for chess
def to_color_bool(s):
    if s.lower() not in ['orange', 'green']:
        raise Exception("must be orange or green")
    return True if s == 'orange' else False

@ask.intent('ColorIntent', convert={'color': to_color_bool})
def set_color(color):
    if 'color' in convert_errors:
        return question("Can you repeat the color?")
    global chess_inst
    chess_inst.set_color(color)
    chess_inst.start()
    return statement("Starting a chess game for you").simple_card('my robot', "Game started.")

# Stop the chess game
@ask.intent('EndChess')
def end_chess():
    global chess_inst
    chess_inst.stop_game()
    return statement("Done")

# delete this later
@ask.intent('TestIntent')
def say_something():
    return statement("This intent is really dumb").simple_card('my robot', "hellooooooo")

@ask.intent('Wander')
def wander():
    ser.write(b'w')
    speech_text = 'Wandering'
    return statement(speech_text).simple_card('my robot', speech_text)



if __name__ == '__main__':
    camera = ChessCamera()
    chess_inst = ChessThread(camera)
    app.run()
