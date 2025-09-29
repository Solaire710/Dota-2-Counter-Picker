# debug_stratz.py
import json
import sys
import cloudscraper

# <-- PUT YOUR TOKEN HERE (keep it secret). If empty, script will try unauthenticated.
BEARER = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJTdWJqZWN0IjoiNzg0YTZhY2YtY2U1MC00NWUwLTliYzktYTZiOGNjNTIxYjM2IiwiU3RlYW1JZCI6IjEyNzc1OTM2NCIsIkFQSVVzZXIiOiJ0cnVlIiwibmJmIjoxNzU4Njc5MTcxLCJleHAiOjE3OTAyMTUxNzEsImlhdCI6MTc1ODY3OTE3MSwiaXNzIjoiaHR0cHM6Ly9hcGkuc3RyYXR6LmNvbSJ9.O-dkBVYLmg8lwKvE8yxUb_CpCErlfmtKdERaLA3DT-A"

STRATZ_URL = "https://api.stratz.com/graphql"

HEADERS = {
    "Authorization": f"Bearer {BEARER}" if BEARER else "",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Origin": "https://stratz.com",
    "Referer": "https://stratz.com/",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
}

scraper = cloudscraper.create_scraper()  # handles Cloudflare challenges much better than plain requests
# optional: set scraper headers as defaults
scraper.headers.update({k: v for k, v in HEADERS.items() if v})

def safe_post(query):
    resp = scraper.post(STRATZ_URL, json={"query": query})
    print("HTTP", resp.status_code)
    print("Content-Type:", resp.headers.get("content-type"))
    print("Content-Encoding:", resp.headers.get("content-encoding"))
    # print small headers for troubleshooting
    print("Server:", resp.headers.get("server"))
    print("--- first 400 bytes (raw) ---")
    raw = resp.content[:400]
    # show both repr and attempt to decode a bit
    try:
        decoded_preview = raw.decode("utf-8")
    except Exception:
        decoded_preview = raw.decode("utf-8", errors="replace")
    print(decoded_preview)
    print("--- raw bytes (hex) ---")
    print(raw.hex()[:400])  # truncated
    
    # Attempt to parse JSON cleanly
    try:
        return resp.json()
    except Exception as e:
        print("Failed to parse JSON:", e)
        # print full text fallback safely
        try:
            print("--- resp.text (utf-8, errors=replace) ---")
            print(resp.text[:2000])
        except Exception:
            print("(unable to print resp.text)")
        return None

if __name__ == "__main__":
    # small constants.heroes query
    q = """
    {
      constants {
        heroes {
          id
          displayName
        }
      }
    }
    """
    data = safe_post(q)
    if not data:
        print("\nNo JSON returned. See the debug above. Likely Cloudflare blocked the request or token invalid.")
        sys.exit(1)

    # if data present, build mapping and print
    try:
        heroes = data["data"]["constants"]["heroes"]
        print(f"Fetched {len(heroes)} heroes.")
        mapping = {h["id"]: h["displayName"] for h in heroes}
        for _id, name in list(mapping.items())[:10]:
            print(_id, mapping[_id])
    except Exception as e:
        print("Unexpected JSON structure:", e)
        print(json.dumps(data)[:2000])
