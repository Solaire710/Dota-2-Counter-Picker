import cloudscraper

BEARER = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJTdWJqZWN0IjoiNzg0YTZhY2YtY2U1MC00NWUwLTliYzktYTZiOGNjNTIxYjM2IiwiU3RlYW1JZCI6IjEyNzc1OTM2NCIsIkFQSVVzZXIiOiJ0cnVlIiwibmJmIjoxNzU4Njc5MTcxLCJleHAiOjE3OTAyMTUxNzEsImlhdCI6MTc1ODY3OTE3MSwiaXNzIjoiaHR0cHM6Ly9hcGkuc3RyYXR6LmNvbSJ9.O-dkBVYLmg8lwKvE8yxUb_CpCErlfmtKdERaLA3DT-A"

STRATZ_URL = "https://api.stratz.com/graphql"

HEADERS = {
    "Authorization": f"Bearer {BEARER}" if BEARER else "",
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
    resp = scraper.post(STRATZ_URL, json={"query": query})
    resp.raise_for_status()
    data = resp.json()
    heroes = data["data"]["constants"]["heroes"]
    return {hero["id"]: hero["displayName"] for hero in heroes}

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
    return data["data"]["heroStats"]["matchUp"][0]["vs"]

if __name__ == "__main__":
    hero_id = 18
    hero_names = get_hero_name_map()
    matchups = get_worst_matchups(hero_id)

    print(f"\nTop 5 worst matchups for {hero_names.get(hero_id, 'Unknown')}:\n")
    for m in matchups:
      enemy_id = m["heroId2"]
      print(f"- {hero_names.get(enemy_id, 'Unknown')} (ID: {enemy_id})")
      print(f"  Match Count: {m['matchCount']}")
      print(f"  Wins: {m['winCount']}")
      win_rate = m["winCount"] / m["matchCount"] if m["matchCount"] > 0 else 0
      print(f"  Win Rate (vs): {round(win_rate * 100, 2)}%\n")

