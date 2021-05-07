from threading import Thread
from chess_functions import *
import chess
import chess.engine
import random
import time

class ChessThread(Thread):
    def __init__(self, cam):
        Thread.__init__(self)
        self.camera = cam
        self.skill_level = 1
        self.player_color = True
        self.running = True

    def set_level(self, level):
        self.skill_level = level

    def set_color(self, color):
        self.player_color = color

    def stop_game(self):
        self.running = False

    def run(self):
        engine = chess.engine.SimpleEngine.popen_uci("Stockfish/src/stockfish")
        engine.configure({"Skill Level": self.skill_level})
        board = chess.Board()

        while self.running and not board.is_game_over():
            if board.turn == self.player_color:
                move = self.get_player_move_camera(board, self.player_color, self.camera)
            else:
                if (self.skill_level == 1):
                    i = random.randint(0,len(list(board.legal_moves))-1)
                    move = list(board.legal_moves)[i]
                else:
                    result = engine.play(board, chess.engine.Limit(time=0.1))
                    move = result.move
                speak('My move is ' + move.uci()[0:2] + ' to ' + move.uci()[2:4])

            if self.running:
                board.push(move)

        declare_winner(board, self.player_color)
    
    def get_player_move_camera(self, board, color, cam):
        # create a list of spaces occupied by the player on the current board
        board_list = piece_list(board, color)
        first_move_seen = None
        
        # loop until a valid move is found
        while self.running: 
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
