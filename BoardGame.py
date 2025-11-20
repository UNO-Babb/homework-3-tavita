#Example Flask App for a hexaganal tile game
#Logic is in this python file

from flask import Flask, render_template, jsonify
from flask import Flask, render_template, request, jsonify
import random
import json
import os

app = Flask(__name__)

# ------------ GAME STATE ------------
BOARD_SIZE = 20  # number of spaces
game_state = {
    "player_positions": [0, 0],     # P1, P2
    "player_scores": [0, 0],
    "turn": 0,                      # 0 = Player 1, 1 = Player 2
    "dice_result": None,
    "events": {}                    # loaded from file
}


# ------------ LOAD EVENTS FROM FILE ------------
def load_events():
    events = {}
    if not os.path.exists("events.txt"):
        return events

    with open("events.txt", "r") as f:
        for line in f:
            if ":" in line:
                space, event = line.strip().split(":")
                events[int(space)] = event.strip()
    return events


game_state["events"] = load_events()


# ------------ SAVE GAME STATE ------------
def save_game():
    with open("savefile.json", "w") as f:
        json.dump(game_state, f)


# ------------ LOAD GAME STATE ------------
def load_game():
    if os.path.exists("savefile.json"):
        global game_state
        with open("savefile.json", "r") as f:
            game_state = json.load(f)


# ------------ APPLY EVENT (IF ANY) ------------
def apply_event(player_index, position):
    if position in game_state["events"]:
        event_text = game_state["events"][position]

        # Simple scoring rules
        if "Hotel" in event_text:
            game_state["player_scores"][player_index] += 3
        elif "Troll" in event_text:
            game_state["player_scores"][player_index] -= 2

        return f"Player {player_index+1} triggered event: {event_text}"
    return "No event."


# ------------ DICE ROLL ROUTE ------------
@app.route("/roll", methods=["POST"])
def roll():
    current_player = game_state["turn"]

    # Roll dice
    dice_value = random.randint(1, 6)
    game_state["dice_result"] = dice_value

    # Move player
    game_state["player_positions"][current_player] += dice_value
    if game_state["player_positions"][current_player] > BOARD_SIZE:
        game_state["player_positions"][current_player] = BOARD_SIZE

    # Apply event
    position = game_state["player_positions"][current_player]
    event_message = apply_event(current_player, position)

    # Switch turn
    game_state["turn"] = 1 - game_state["turn"]

    save_game()

    return jsonify({
        "dice": dice_value,
        "positions": game_state["player_positions"],
        "scores": game_state["player_scores"],
        "turn": game_state["turn"],
        "event": event_message
    })


# ------------ HOME PAGE ------------
@app.route("/")
def index():
    return render_template("board.html",
                           board_size=BOARD_SIZE,
                           positions=game_state["player_positions"],
                           scores=game_state["player_scores"],
                           turn=game_state["turn"],
                           dice=game_state["dice_result"],
                           events=game_state["events"])


if __name__ == "__main__":
    app.run(debug=True)
