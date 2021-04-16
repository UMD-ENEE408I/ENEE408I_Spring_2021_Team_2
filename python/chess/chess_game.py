import chess
# from stockfish import Stockfish
import chess.engine
import time
from chess_vision import ChessCamera


def player_piece_list(board, color):
    pieces = []
    valid_piece_types = [chess.KING, chess.QUEEN, chess.BISHOP, chess.ROOK, chess.KNIGHT, chess.PAWN]
    for piece_type in valid_piece_types:
        pieces.append(list(chess.BaseBoard.pieces(board, piece_type, color)))
    pieces = sorted(sum(pieces, []))
    return pieces

def get_player_move_camera(board, color, cam):
    board_list = player_piece_list(board, color)
    while True: # loop until a valid move is found
        time.sleep(2)
        mask = cam.current_colored_board_mask()
        camera_list = []
        for i in range(64):
            if mask[i] == player_color:
                camera_list.append(i)
        camera_list = sorted(camera_list)

        # The player cannot gain or lose pieces on their turn
        if(len(camera_list) != len(board_list)):
            print("Something went wrong") # Go back to capture the next board from camera
            continue

        if(camera_list == board_list):
            print("No move was made yet") # Go back to capture the next board from camera
            continue

        source_square = list(set(board_list)-set(camera_list))
        dest_square = list(set(camera_list)-set(board_list))
        
        # Only one piece can move in a turn
        if(len(source_square) != len(dest_square) != 1):
            print("Something went wrong") # Go back to capture the next board from camera
            continue
        
        try:
            player_move = board.find_move(source_square[0], dest_square[0])
        except:
            continue # invalid move, wait and capture again

        return player_move  # at this point --- some move was made

def get_player_move(board):
    while True:
        print()
        source_file = int(input("Source file: "))
        source_rank = int(input("Source rank: "))
        dest_file = int(input("Dest file: "))
        dest_rank = int(input("Dest rank: "))

        try:
            source = chess.square(source_file, source_rank)
            print(source)
            dest = chess.square(dest_file, dest_rank)
            print(dest)
            move = board.find_move(source, dest)
        except:
            print('You messed up')
            continue
        
        return move

limit = True
# level = int(input("What skill level would you like to play against?: "))
# play_as = input("What color would you like to play as? (W/B): " )
# if play_as == "W":
#     player_color = chess.WHITE
# else:
#     player_color = chess.BLACK

player_color = chess.WHITE

# stockfish = Stockfish("C:/Users/adamm/Downloads/Senior/408/robo/python/stockfish_13_win_x64", parameters={"UCI_LimitStrength": limit, "UCI_Elo": elo})
engine = chess.engine.SimpleEngine.popen_uci("Stockfish/src/stockfish")
# engine.configure({"UCI_LimitStrength": True, "UCI_Elo": elo})
engine.configure({"Skill Level": 1})

board = chess.Board()
print()
print(board)
camera = ChessCamera()

while not board.is_game_over():
    if board.turn == player_color:
        print('hello')
        move = get_player_move_camera(board, player_color, camera)
        print('player')
    else:
        result = engine.play(board, chess.engine.Limit(time=0.1))
        move = result.move
        print('comp')

    board.push(move)
    print()
    print(move)
    print(board)


x=1