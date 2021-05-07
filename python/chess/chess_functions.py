import chess
from gtts import gTTS
import os
from playsound import playsound


def piece_list(board, color):
    pieces = []
    valid_piece_types = [chess.KING, chess.QUEEN, chess.BISHOP, chess.ROOK, chess.KNIGHT, chess.PAWN]
    for piece_type in valid_piece_types:
        pieces.append(list(chess.BaseBoard.pieces(board, piece_type, color)))
    pieces = sorted(sum(pieces, []))
    return pieces

def speak(speak_string):
    myobj = gTTS(text=speak_string, lang='en', slow=False)
    myobj.save('audio.mp3')
    playsound('audio.mp3')
    os.remove('audio.mp3')

def declare_winner(board, color):
    if board.is_game_over():
        outcome = board.result()
        if outcome == '1/2-1/2':
            speak('Good game. Its a draw.')
        elif outcome == '1-0' and color:
            speak("Good job. You beat me.")
        elif outcome == '0-1' and not color:
            speak("Good job. You beat me.")
        else:
            speak('You lost. Get better.')
    else:
        speak('The game was not over, but you were losing.')
    

