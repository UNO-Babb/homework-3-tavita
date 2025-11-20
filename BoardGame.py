#Example Flask App for a hexaganal tile game
#Logic is in this python file
from flask import Flask, render_template, request, jsonify
import random
import os

app = Flask(__name__)

# ----- GAME STATE -----
BOARD_SIZE = 20
player_positions = {"Player 1": 0, "Player 2": 0}
player_scores = {"Player 1": 0, "Player 2": 0}
players = ["Player 1", "Player 2"]
current_player_index = 0
last_roll = None
last_event_message = ""

events = {}

# ------------ LOAD EVENTS FROM FILE ------------
def load_events():
    event_dict = {}
    if os.path.exists("events.txt"):
        with open("events.txt", "r") as f:
            for line in f:
                if ":" in line:
                    pos, ev = line.strip().split(":")
                    event_dict[int(pos)] = ev.strip()
    return event_dict


events = load_events()


# ------------ APPLY EVENT ------------
def apply_event(player, pos):
    global last_event_message

    if pos not in events:
        last_event_message = "No event."
        return

    ev = events[pos]

    if ev == "Hotel":
        player_scores[player] += 3
        last_event_message = f"{player} found a Hotel (+3)"
    elif ev == "Troll":
        player_scores[player] -= 2
        last_event_message = f"{player} hit a Troll (-2)"
    else:
        last_event_message = f"{player} triggered: {ev}"


@app.route("/")
def index():
    return render_template(
        "index.html",
        board_size=BOARD_SIZE,
        player_positions=player_positions,
        player_scores=player_scores,
        events=events,
        current_player=players[current_player_index],
        last_roll=last_roll,
        last_event_message=last_event_message
    )


@app.route("/roll", methods=["POST"])
def roll():
    global current_player_index, last_roll

    player = players[current_player_index]
    roll_value = random.randint(1, 6)
    last_roll = roll_value

    # Move player
    player_positions[player] += roll_value
    if player_positions[player] >= BOARD_SIZE - 1:
        player_positions[player] = BOARD_SIZE - 1
        return jsonify({"winner": player})

    # Apply event
    apply_event(player, player_positions[player])

    # Switch turns
    current_player_index = (current_player_index + 1) % len(players)

    return jsonify({
        "player_positions": player_positions,
        "player_scores": player_scores,
        "current_player": players[current_player_index],
        "last_roll": last_roll,
        "last_event_message": last_event_message
    })


if __name__ == "__main__":
    app.run(debug=True)
