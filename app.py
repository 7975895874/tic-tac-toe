# app.py
from flask import Flask, request, jsonify, send_from_directory
from copy import deepcopy

app = Flask(__name__, static_folder='.')

HUMAN = 'X'
COMP = 'O'
EMPTY = ''

winning_combinations = [
    (0,1,2),(3,4,5),(6,7,8), # rows
    (0,3,6),(1,4,7),(2,5,8), # cols
    (0,4,8),(2,4,6)          # diags
]

def check_winner(board):
    """Return 'X' or 'O' if a winner, 'Draw' if full and no winner, else None."""
    for a,b,c in winning_combinations:
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return board[a]
    if all(cell != EMPTY for cell in board):
        return 'Draw'
    return None

def minimax(board, player):
    """Return (best_score, best_move_index) for player on given board.
       Score from perspective of COMP (O): +1 win, -1 loss, 0 draw."""
    winner = check_winner(board)
    if winner == COMP:
        return 1, None
    elif winner == HUMAN:
        return -1, None
    elif winner == 'Draw':
        return 0, None

    if player == COMP:
        best_score = -2
        best_move = None
        for i in range(9):
            if board[i] == EMPTY:
                board[i] = COMP
                score, _ = minimax(board, HUMAN)
                board[i] = EMPTY
                if score > best_score:
                    best_score = score
                    best_move = i
        return best_score, best_move
    else:
        best_score = 2
        best_move = None
        for i in range(9):
            if board[i] == EMPTY:
                board[i] = HUMAN
                score, _ = minimax(board, COMP)
                board[i] = EMPTY
                if score < best_score:
                    best_score = score
                    best_move = i
        return best_score, best_move

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/move', methods=['POST'])
def move():
    data = request.get_json()
    board = data.get('board', [])
    # validate board
    if not isinstance(board, list) or len(board) != 9:
        return jsonify({'error': 'board must be list of length 9'}), 400

    # If already finished return current state
    winner = check_winner(board)
    if winner:
        return jsonify({'index': None, 'board': board, 'winner': winner})

    # Compute best move for COMP (O)
    _, best = minimax(deepcopy(board), COMP)
    if best is None:
        return jsonify({'index': None, 'board': board, 'winner': 'Draw'})

    board[best] = COMP
    winner = check_winner(board)
    return jsonify({'index': best, 'board': board, 'winner': winner})

if __name__ == '__main__':
    app.run(debug=True)