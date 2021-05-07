import chess
import chess.engine
import time
from chess_functions import *
import random
from gtts import gTTS
import os
from playsound import playsound
import argparse 


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
    board_list = piece_list(board, color)
    # comp_board_list = piece_list(board, not color)
    first_move_seen = None
    
    # loop until a valid move is found
    while True: 
        # capture the state of the board (list of T/F/None)
        mask = cam.current_colored_board_mask()
        if color == chess.WHITE:
            mask.reverse()

        # select entries in this list that match the players color
        player_cam_list = []
        for i in range(64):
            if mask[i] == color:
                player_cam_list.append(i)

        player_cam_list = sorted(player_cam_list)

        # The player cannot gain or lose pieces on their turn
        if(len(player_cam_list) != len(board_list)):
            continue

        if(player_cam_list == board_list):
            continue
        
        source_square = list(set(board_list)-set(player_cam_list))
        dest_square = list(set(player_cam_list)-set(board_list))
        
        # Only one piece can move in a turn
        if(len(source_square) != len(dest_square) != 1):
            continue
        
        try:
            player_move = board.find_move(source_square[0], dest_square[0])
        except:
            continue # invalid move, wait and capture again

        if first_move_seen == None:
            first_move_seen = player_move
            print('I think the move is', player_move.uci())
            for _ in range(25):
                _ = cam.current_colored_board_mask()
            continue
        elif first_move_seen.uci() == player_move.uci():
            print('I confirmed the move is', player_move.uci())
            first_move_seen = None
            return player_move
        
        first_move_seen = None
        

def get_player_move(board):
    # text mode for testing 
    while True:
        print()
        move_str = input("what is your move? ")

        move = chess.Move.from_uci(move_str)
        if move in board.legal_moves:
            return move


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("level", help="Level of computer to play against", type=int)
    ap.add_argument("color", help="Color for the player to use. True = Orange(White), False = Green(Black)", type=bool)

    args = ap.parse_args()

    level = args.level
    player_color = args.color

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
            speak('My move is ' + move.uci()[0:2] + ' to ' + move.uci()[2:4])

        board.push(move)
        print(move)
        print(board)
        print()
    
    declare_winner(board, player_color)


