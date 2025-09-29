# app.py
from flask import Flask, render_template, request, jsonify
import requests
import time

app = Flask(__name__)

# --- Config ---
MIN_TOTAL_GAMES = 80   # raise to reduce noisy, low-sample counters
TOP_N = 12
REQUEST_TIMEOUT = 8    # seconds for OpenDota requests

# --- Load hero lists once at startup ---
HEROES = requests.get("https://api.opendota.com/api/heroes", timeout=REQUEST_TIMEOUT).json()
HERO_MAP = {h["localized_name"].strip().lower(): h["id"] for h in HEROES}
ID_TO_NAME = {h["id"]: h["localized_name"] for h in HEROES}

# Simple in-memory cache for matchups to avoid repeated OpenDota calls
_matchup_cache = {}

def get_matchups_for_hero(hero_id):
    """Return the JSON array from OpenDota /heroes/{id}/matchups, cached."""
    if hero_id in _matchup_cache:
        return _matchup_cache[hero_id]
    url = f"https://api.opendota.com/api/heroes/{hero_id}/matchups"
    resp = requests.get(url, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    _matchup_cache[hero_id] = data
    # be a little polite to the API
    time.sleep(0.12)
    return data

@app.route("/")
def index():
    return render_template("indexAPI.html")

@app.route("/get_counters", methods=["POST"])
def get_counters():
    payload = request.json or {}
    heroes_input = payload.get("heroes", [])  # expect list of names
    # normalize and map to IDs
    hero_ids = []
    for h in heroes_input:
        if not isinstance(h, str):
            continue
        key = h.strip().lower()
        if key in HERO_MAP:
            hero_ids.append(HERO_MAP[key])

    if not hero_ids:
        return jsonify({"error": "No valid heroes entered"}), 400

    # counters[hid] = {"enemy_wins": int, "games": int}
    counters = {}

    # For each queried input hero, pull its matchups
    for qid in hero_ids:
        try:
            matchups = get_matchups_for_hero(qid)
        except Exception as e:
            return jsonify({"error": f"Failed to fetch matchups for id {qid}: {e}"}), 502

        for m in matchups:
            hid = int(m["hero_id"])
            games = int(m.get("games_played", 0))
            wins_for_queried = int(m.get("wins", 0))  # wins for the queried hero (OpenDota)
            if games <= 0:
                continue

            # enemy wins vs the queried hero:
            enemy_wins = games - wins_for_queried

            s = counters.setdefault(hid, {"enemy_wins": 0, "games": 0})
            s["enemy_wins"] += enemy_wins
            s["games"] += games

    # Build results, filtering and excluding the heroes we queried
    results = []
    for hid, s in counters.items():
        if hid in hero_ids:
            continue
        if s["games"] < MIN_TOTAL_GAMES:
            # skip low-sample aggregated results; keep debugable if you want
            continue
        enemy_winrate = s["enemy_wins"] / s["games"] * 100
        results.append({
            "hero": ID_TO_NAME.get(hid, str(hid)),
            "enemy_winrate": round(enemy_winrate, 1),
            "games": s["games"]
        })

    # sort by how strongly the hero beats your picks
    results.sort(key=lambda x: x["enemy_winrate"], reverse=True)
    return jsonify(results[:TOP_N])

if __name__ == "__main__":
    app.run(debug=True)
