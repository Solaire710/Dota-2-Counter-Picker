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
        }
      }
    }
    """
    try:
        resp = scraper.post(STRATZ_URL, json={"query": query})
        resp.raise_for_status()
        data = resp.json()
        
        # Debugging: print API response
        print("API Response Data:", data)

        heroes = data["data"]["constants"]["heroes"]

        if not heroes:
            print("No heroes found in response")
        
        # Sorting heroes by displayName alphabetically
        sorted_heroes = sorted(heroes, key=lambda hero: hero["displayName"])

        # Creating a dictionary of hero ID and name
        return {hero["id"]: hero["displayName"] for hero in sorted_heroes}

    except requests.exceptions.RequestException as e:
        print("Error fetching hero names:", e)
        return {}


def get_worst_matchups(hero_id):
    query = f"""
    {{
      heroStats {{
        matchUp(heroId: {hero_id}, matchLimit: 5, orderBy: 4) {{
          heroId
          matchCountVs
          vs {{
            heroId2
            matchCount
            winCount
            winRateHeroId1
            winRateHeroId2
          }}
        }}
      }}
    }}
    """
    resp = scraper.post(STRATZ_URL, json={"query": query})
    resp.raise_for_status()
    data = resp.json()

    # Print the raw response to check the win rates
    print("Raw API Response:")
    print(data)

    matchups = data["data"]["heroStats"]["matchUp"][0]["vs"]

    return matchups

@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    matchups = None
    hero_names = get_hero_name_map()

    print("Hero Names:", hero_names)  # Check that hero names are properly passed

    hero_name = None  # Default to None, in case no form is submitted

    if request.method == "POST":
        hero_name = request.form.get("hero_name")
        if not hero_name:
            error = "Please select a hero!"
        else:
            hero_id = next((hero_id for hero_id, name in hero_names.items() if name == hero_name), None)
            if hero_id:
                matchups = get_worst_matchups(hero_id)
            else:
                error = "Hero not found!"

    return render_template("index.html", hero_names=hero_names, matchups=matchups, error=error, hero_name=hero_name)



if __name__ == "__main__":
    app.run(debug=True)
