# Handles server and client interaction for the jeopardy game
from jeopardy import Jeopardy

##### Server Notes #####
def ask_point_value(self, client_id):
    # ask client for point value
    # receive point value and set question_point_vlaue
    pass

def ask_question(question_string, client_ids):
    # send question to all 3 clients
    pass

def game_loop(game):
    control_player = game.set_control_player()
    game.question_point_value = ask_point_value()
    # get quesrion and ask
    # looks for first buzzage



# things
game = Jeopardy()
game_loop(game)