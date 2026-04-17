from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Game state
game_state = {
    "board": [""] * 9,
    "current_player": "X",
    "winner": None,  # Can be "X", "O", "Draw", or None
    "game_active": True,
}

# Helper function to check for a winner
def check_winner(board):
    winning_combinations = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Rows
        (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Columns
        (0, 4, 8), (2, 4, 6)             # Diagonals
    ]
    for combo in winning_combinations:
        a, b, c = combo
        if board[a] and board[a] == board[b] and board[a] == board[c]:
            return board[a]
    
    if all(cell != "" for cell in board):
        return "Draw"
    
    return None

class Move(BaseModel):
    index: int

@app.get("/game")
async def get_game_state():
    return game_state

@app.post("/game/start")
async def start_new_game():
    global game_state
    game_state = {
        "board": [""] * 9,
        "current_player": "X",
        "winner": None,
        "game_active": True,
    }
    return game_state

@app.post("/game/move")
async def make_move(move: Move):
    global game_state

    if not game_state["game_active"]:
        raise HTTPException(status_code=400, detail="Game is over. Start a new game.")
    
    if not (0 <= move.index < 9):
        raise HTTPException(status_code=400, detail="Invalid move index.")
    
    if game_state["board"][move.index] != "":
        raise HTTPException(status_code=400, detail="Cell is already occupied.")
    
    game_state["board"][move.index] = game_state["current_player"]
    
    winner = check_winner(game_state["board"])
    if winner:
        game_state["winner"] = winner
        game_state["game_active"] = False
    else:
        game_state["current_player"] = "O" if game_state["current_player"] == "X" else "X"
    
    return game_state

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
def home():
    return open("index.html").read()
