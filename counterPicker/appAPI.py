from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Fetch hero list from OpenDota once on startup
HEROES = requests.get("https://api.opendota.com/api/heroes").json()
HERO_MAP = {hero["localized_name"].lower(): hero["id"] for hero in HEROES}
ID_TO_NAME = {hero["id"]: hero["localized_name"] for hero in HEROES}

@app.route("/")
def index():
    return render_template("indexAPI.html")

@app.route("/get_counters", methods=["POST"])
def get_counters():
    heroes_input = request.json.get("heroes", [])
    hero_ids = [HERO_MAP[h.lower()] for h in heroes_input if h.lower() in HERO_MAP]

    if not hero_ids:
        return jsonify({"error": "No valid heroes entered"}), 400

    all_counters = {}

    for hero_id in hero_ids:
        data = requests.get(f"https://api.opendota.com/api/heroes/{hero_id}/matchups").json()
        for matchup in data:
            hid = matchup["hero_id"]
            win_rate_against_input = (matchup["games_played"] - matchup["wins"]) / matchup["games_played"] * 100
            all_counters.setdefault(hid, []).append(win_rate_against_input)

    # Average win rate vs all input heroes
    results = []
    for hid, rates in all_counters.items():
        if hid not in hero_ids:
            avg = sum(rates) / len(rates)
            results.append({"hero": ID_TO_NAME[hid], "avg_win_rate": round(avg, 1)})

    # Sort by best counter
    results.sort(key=lambda x: x["avg_win_rate"], reverse=True)

    return jsonify(results[:10])

if __name__ == "__main__":
    app.run(debug=True)
