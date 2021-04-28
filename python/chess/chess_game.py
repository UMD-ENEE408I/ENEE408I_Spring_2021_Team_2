import chess
# from stockfish import Stockfish
import chess.engine
import time
from chess_vision import ChessCamera
import random
from gtts import gTTS
import os
from playsound import playsound

def player_piece_list(board, color):
    pieces = []
    valid_piece_types = [chess.KING, chess.QUEEN, chess.BISHOP, chess.ROOK, chess.KNIGHT, chess.PAWN]
    for piece_type in valid_piece_types:
        pieces.append(list(chess.BaseBoard.pieces(board, piece_type, color)))
    pieces = sorted(sum(pieces, []))
    return pieces


def print_board(mask):
    # for testing
    # prints out the board that the camera sees
    i = 0
    for row in range(8):
        for col in range(8):
            if mask[i] == chess.WHITE:
                print('O', end='')
            elif mask[i] == chess.BLACK:
                print('G', end='')
            else:
                print(' ', end='')
            i = i+1
        print('\n', end='')
    print()




def get_player_move_camera(board, color, cam):
    # create a list of spaces occupied by the player on the current board
    board_list = player_piece_list(board, color)
    first_move_seen = None
    # loop until a valid move is found
    while True: 
        # time.sleep(1) # -- this makes it run too slow currently

        # capture the state of the board (list of T/F/None)
        mask = cam.current_colored_board_mask()
        # if color == chess.WHITE:
        mask.reverse()

        # select entries in this list that match the players color
        camera_list = []
        for i in range(64):
            if mask[i] == player_color:
                camera_list.append(i)
        camera_list = sorted(camera_list)

        # The player cannot gain or lose pieces on their turn
        if(len(camera_list) != len(board_list)):
            # Go back to capture the next board from camera
            # print("Something went wrong (incorrect number of pieces detected)")
            continue

        if(camera_list == board_list):
            # Go back to capture the next board from camera
            # print("No move was made yet") 
            continue
        
        source_square = list(set(board_list)-set(camera_list))
        dest_square = list(set(camera_list)-set(board_list))
        
        # Only one piece can move in a turn
        if(len(source_square) != len(dest_square) != 1):
            # Go back to capture the next board from camera
            # print("Something went wrong (more than one piece moved)") 
            continue
        
        try:
            player_move = board.find_move(source_square[0], dest_square[0])
        except:
            continue # invalid move, wait and capture again

        if first_move_seen == None:
            first_move_seen = player_move
            print('I think the move is', player_move.uci())
            for _ in range(40):
                _ = cam.current_colored_board_mask()
            continue
        elif first_move_seen.uci() == player_move.uci():
            print('I confirmed the move is', player_move.uci())
            first_move_seen = None
            return player_move
        
        first_move_seen = None
        


        # ask player to confirm move before pushing it?
        # confirmation = get_player_confirmation(player_move)
        # if confirmation:
            # return player_move 


def get_player_confirmation(player_move):
    # currently text-based, move to speaker prompt and audio reply?
    print("Your current move is", player_move)
    resp = input("Is this correct? (y/n) ")
    if resp == 'y':
        return True
    else:
        return False


def get_player_move(board):
    # text mode for testing 
    while True:
        print()
        move_str = input("what is your move? ")
        # source_file = int(input("Source file: "))
        # source_rank = int(input("Source rank: "))
        # dest_file = int(input("Dest file: "))
        # dest_rank = int(input("Dest rank: "))

        move = chess.Move.from_uci(move_str)
        if move in board.legal_moves:
            return move
        
        # try:
        #     source = chess.square(source_file, source_rank)
        #     print(source)
        #     dest = chess.square(dest_file, dest_rank)
        #     print(dest)
        #     move = board.find_move(source, dest)
        # except:
        #     print('You messed up')
        #     continue
        
        # return move


def speak(move):
    # temp = move.uci()
    # print(move.uci()[0] + move.uci()[1])
    # print(temp[2:4])
    
    move_string = 'My move is ' + move.uci()[0:2] + ' to ' + move.uci()[2:4]
    myobj = gTTS(text=move_string, lang='en', slow=False)
    myobj.save('audio.mp3')
    playsound('audio.mp3')
    os.remove('audio.mp3')


level = int(input("What skill level would you like to play against?: "))
play_as = input("What color would you like to play as? (W/B): " )
if play_as == "W":
    player_color = chess.WHITE
else:
    player_color = chess.BLACK

engine = chess.engine.SimpleEngine.popen_uci("Stockfish/src/stockfish")
engine.configure({"Skill Level": level})

board = chess.Board()
camera = ChessCamera()
print()
print(board)

while not board.is_game_over():
    if board.turn == player_color:
        move = get_player_move_camera(board, player_color, camera)
        # move = get_player_move(board)
        print('\nplayer: ', end='')
    else:
        if (level == 1):
            i = random.randint(0,len(list(board.legal_moves))-1)
            move = list(board.legal_moves)[i]
        else:
            result = engine.play(board, chess.engine.Limit(time=0.1))
            move = result.move
        print('computer: ', end='')
        speak(move)

    board.push(move)
    print(move)
    print(board)
    print()

final = board.outcome()
print(final.outcome)


x=1