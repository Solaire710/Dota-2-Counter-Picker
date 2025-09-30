import requests
from flask import Flask, render_template, request, jsonify
import cloudscraper

app = Flask(__name__)

BEARER = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJTdWJqZWN0IjoiNzg0YTZhY2YtY2U1MC00NWUwLTliYzktYTZiOGNjNTIxYjM2IiwiU3RlYW1JZCI6IjEyNzc1OTM2NCIsIkFQSVVzZXIiOiJ0cnVlIiwibmJmIjoxNzU4Njc5MTcxLCJleHAiOjE3OTAyMTUxNzEsImlhdCI6MTc1ODY3OTE3MSwiaXNzIjoiaHR0cHM6Ly9hcGkuc3RyYXR6LmNvbSJ9.O-dkBVYLmg8lwKvE8yxUb_CpCErlfmtKdERaLA3DT-A"
STRATZ_URL = "https://api.stratz.com/graphql"
HEADERS = {
    "Authorization": f"Bearer {BEARER}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Origin": "https://stratz.com",
    "Referer": "https://stratz.com/",
    "Accept": "application/json",
}

scraper = cloudscraper.create_scraper()
scraper.headers.update({k: v for k, v in HEADERS.items() if v})

def get_hero_name_map():
    query = """
    {
      constants {
        heroes {
          id
          displayName
          shortName
        }
      }
    }
    """
    try:
        resp = scraper.post(STRATZ_URL, json={"query": query})
        resp.raise_for_status()
        data = resp.json()

        heroes = data["data"]["constants"]["heroes"]
        if not heroes:
            print("No heroes found in response")

        # sort by displayName for dropdown order
        sorted_heroes = sorted(heroes, key=lambda hero: hero["displayName"])
        
        # Create two mappings
        id_to_name = {hero["id"]: hero["displayName"] for hero in sorted_heroes}
        name_to_short = {hero["displayName"]: hero["shortName"] for hero in sorted_heroes}

        return id_to_name, name_to_short

    except requests.exceptions.RequestException as e:
        print("Error fetching hero names:", e)
        return {}, {}


def get_best_counters_by_synergy(hero_ids, hero_names, match_limit=50):
    hero_stats = {}

    for hero_id in hero_ids:
        query = f"""
        {{
          heroStats {{
            heroVsHeroMatchup(heroId: {hero_id}, matchLimit: {match_limit}) {{
              disadvantage {{
                vs {{
                  heroId2
                  matchCount
                  synergy
                }}
              }}
            }}
          }}
        }}
        """

        try:
            resp = scraper.post(STRATZ_URL, json={"query": query})
            resp.raise_for_status()
            data = resp.json()

            print("API response data:", data)  # Debug

            matchup_data = data["data"]["heroStats"]["heroVsHeroMatchup"]
            disadvantage_list = matchup_data.get("disadvantage", [])

            if not disadvantage_list:
                continue

            vs_list = disadvantage_list[0].get("vs", [])


            for m in vs_list:
                cid = m.get("heroId2")
                if cid is None or cid in hero_ids:
                    continue  # 👈 Skip selected heroes

                synergy = m.get("synergy") or 0
                match_count = int(m.get("matchCount") or 0)

                stat = hero_stats.setdefault(cid, {"total_synergy": 0, "matches": 0})
                stat["total_synergy"] += synergy * match_count
                stat["matches"] += match_count

        except Exception as e:
            print(f"Error fetching synergy data for hero {hero_id}: {e}")
            continue

    results = []
    for cid, s in hero_stats.items():
        if s["matches"] == 0:
            continue
        avg_synergy = s["total_synergy"] / s["matches"]
        results.append((cid, avg_synergy))

    results.sort(key=lambda x: x[1])  # ascending = worst synergy
    return [(hero_names.get(cid, f"Unknown({cid})"), round(synergy, 2)) for cid, synergy in results[:10]]

@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    hero_names, hero_short_names = get_hero_name_map()
    selected_heroes = []
    matchups = []

    if request.method == "POST":
        for i in range(1, 6):
            hero_name = request.form.get(f"hero_{i}")
            if hero_name:
                selected_heroes.append(hero_name)

        if not selected_heroes:
            error = "Please select at least one hero!"
        else:
            selected_ids = [hid for hid, name in hero_names.items() if name in selected_heroes]
            matchups = get_best_counters_by_synergy(selected_ids, hero_names)

    return render_template(
        "index.html",
        hero_names=hero_names,
        hero_short_names=hero_short_names,
        matchups=matchups,
        error=error,
        selected_heroes=selected_heroes,
    )


if __name__ == "__main__":
    app.run(debug=True)
