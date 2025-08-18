from flask import Flask, render_template, request
import time
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Define the base URL
base_url = 'https://www.dotabuff.com/heroes/'
hero_name_mapping = {
    "abaddon": "Abaddon",
    "alchemist": "Alchemist",
    "ancient_apparition": "Ancient Apparition",
    "anti-mage": "Anti-Mage",
    "arc_warden": "Arc Warden",
    "axe": "Axe",
    "bane": "Bane",
    "batrider": "Batrider",
    "beastmaster": "Beastmaster",
    "bloodseeker": "Bloodseeker",
    "bounty_hunter": "Bounty Hunter",
    "brewmaster": "Brewmaster",
    "bristleback": "Bristleback",
    "broodmother": "Broodmother",
    "centaur_warrunner": "Centaur Warrunner",
    "chaos_knight": "Chaos Knight",
    "chen": "Chen",
    "clinkz": "Clinkz",
    "clockwerk": "Clockwerk",
    "crystal_maiden": "Crystal Maiden",
    "dawnbreaker": "Dawnbreaker",
    "dark_seer": "Dark Seer",
    "dark_willow": "Dark Willow",
    "dazzle": "Dazzle",
    "death_prophet": "Death Prophet",
    "disruptor": "Disruptor",
    "doom": "Doom",
    "dragon_knight": "Dragon Knight",
    "drow_ranger": "Drow Ranger",
    "earth_spirit": "Earth Spirit",
    "earthshaker": "Earthshaker",
    "elder_titan": "Elder Titan",
    "ember_spirit": "Ember Spirit",
    "enchantress": "Enchantress",
    "enigma": "Enigma",
    "faceless_void": "Faceless Void",
    "grimstroke": "Grimstroke",
    "gyrocopter": "Gyrocopter",
    "hoodwink": "Hoodwink",
    "huskar": "Huskar",
    "invoker": "Invoker",
    "io": "Io",
    "jakiro": "Jakiro",
    "juggernaut": "Juggernaut",
    "keeper_of_the_light": "Keeper of the Light",
    "kunkka": "Kunkka",
    "leshrac": "Leshrac",
    "legion_commander": "Legion Commander",
    "lich": "Lich",
    "lifestealer": "Lifestealer",
    "lina": "Lina",
    "lion": "Lion",
    "luna": "Luna",
    "lycan": "Lycan",
    "magnataur": "Magnus",
    "marci": "Marci",
    "mars": "Mars",
    "medusa": "Medusa",
    "meepo": "Meepo",
    "mirana": "Mirana",
    "monkey_king": "Monkey King",
    "morphling": "Morphling",
    "naga_siren": "Naga Siren",
    "furion": "Nature's Prophet",
    "necrolyte": "Necrophos",
    "night_stalker": "Night Stalker",
    "obsidian_destroyer": "Outworld Destroyer",
    "ogre_magi": "Ogre Magi",
    "omniknight": "Omniknight",
    "oracle": "Oracle",
    "obsidian_destroyer": "Outworld Destroyer",
    "pangolier": "Pangolier",
    "phantom_assassin": "Phantom Assassin",
    "phantom_lancer": "Phantom Lancer",
    "phoenix": "Phoenix",
    "primal_beast": "Primal Beast",
    "puck": "Puck",
    "pudge": "Pudge",
    "pugna": "Pugna",
    "razor": "Razor",
    "riki": "Riki",
    "ringmaster": "Ringmaster",
    "rubick": "Rubick",
    "sand_king": "Sand King",
    "shadow_demon": "Shadow Demon",
    "nevermore": "Shadow Fiend",
    "shadow_shaman": "Shadow Shaman",
    "silencer": "Silencer",
    "skywrath_mage": "Skywrath Mage",
    "slardar": "Slardar",
    "slark": "Slark",
    "snapfire": "Snapfire",
    "sniper": "Sniper",
    "spectre": "Spectre",
    "spirit_breaker": "Spirit Breaker",
    "storm_spirit": "Storm Spirit",
    "sven": "Sven",
    "techies": "Techies",
    "templar_assassin": "Templar Assassin",
    "terrorblade": "Terrorblade",
    "tidehunter": "Tidehunter",
    "shredder": "Timbersaw",
    "tinker": "Tinker",
    "tiny": "Tiny",
    "treant_protector": "Treant Protector",
    "troll_warlord": "Troll Warlord",
    "tusk": "Tusk",
    "abyssal_underlord": "Underlord",
    "undying": "Undying",
    "ursa": "Ursa",
    "vengeful_spirit": "Vengeful Spirit",
    "venomancer": "Venomancer",
    "viper": "Viper",
    "visage": "Visage",
    "void_spirit": "Void Spirit",
    "warlock": "Warlock",
    "weaver": "Weaver",
    "windrunner": "Windrunner",
    "winter_wyvern": "Winter Wyvern",
    "witch_doctor": "Witch Doctor",
    "wraith_king": "Wraith King",
    "zeus": "Zeus",
    "muerta": "Muerta"
}

base_hero_url = 'https://cdn.akamai.steamstatic.com/apps/dota2/images/dota_react/heroes/{}.png'
hero_images = {
    hero: base_hero_url.format(hero) for hero in hero_name_mapping
}

# Function to fetch and parse win rates
def fetch_win_rates(url):
    max_retries = 5
    retry_count = 0
    advantage_percentages = {}

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'
    }

    while retry_count < max_retries:
        print(f"Fetching URL: {url}")  # Debugging statement
        response = requests.get(url, headers=headers)
        print(f"Received response: {response.status_code}")  # Debugging statement

        if response.status_code == 200:
            website_code = response.text
            soup = BeautifulSoup(website_code, 'html.parser')
            win_rate_table = soup.find('table', class_='sortable')

            if win_rate_table:
                rows = win_rate_table.find('tbody').find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        hero_name_td = cells[0]
                        hero_name = hero_name_td.get('data-value') or hero_name_td.text.strip()
                        win_rate_td = cells[2]
                        data_value = win_rate_td.get('data-value')

                        if data_value:
                            advantage_percentages[hero_name] = float(data_value)
                            print(f"Fetched {hero_name}: {data_value}%")  # Debugging statement

                break
            else:
                print("Win rate table not found.")  # Debugging statement
        elif response.status_code == 429:
            wait_time = 2 ** retry_count
            print(f"Too many requests. Waiting for {wait_time} seconds...")
            time.sleep(wait_time)
            retry_count += 1
        else:
            print(f"Failed to retrieve the website. Status code: {response.status_code}")
            break

    print("Advantage Percentages Fetched:", advantage_percentages)  # Debugging statement
    return advantage_percentages

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get all hero names
        hero_names = request.form.getlist('heroes')  # This will get all hero names

        # Now use hero_name_mapping to display the new names
        new_names = [hero_name_mapping[hero] for hero in hero_names if hero in hero_name_mapping]

        # Filter out empty inputs
        hero_names = [name.strip() for name in hero_names if name.strip()]

        # Normalize hero names for comparison
        normalized_hero_names = [name.replace(" ", "_").lower() for name in hero_names]

        print("Input Heroes (Normalized):", normalized_hero_names)  # Debugging statement

        # Create URLs for each hero
        urlList = [base_url + name.replace(" ", "_").lower() + '/counters' for name in hero_names]

        print("Generated URLs:", urlList)  # Debugging statement

        # Dictionary to store total advantages for each hero
        all_hero_advantages = {}

        # Loop through each URL in urlList and fetch win rates
        for url in urlList:
            advantages = fetch_win_rates(url)
            for hero, advantage in advantages.items():
                if hero not in all_hero_advantages:
                    all_hero_advantages[hero] = []
                all_hero_advantages[hero].append(advantage)

        print("Aggregated Advantages:", all_hero_advantages)  # Print raw advantages

        # Calculate average advantage percentages
        average_advantages = {hero: sum(adv) / len(adv) for hero, adv in all_hero_advantages.items()}

        # Normalize the keys in average_advantages for comparison
        normalized_average_advantages = {hero.replace(" ", "_").lower(): avg for hero, avg in average_advantages.items()}

        # Exclude input heroes from the sorted advantages
        filtered_advantages = {hero: avg for hero, avg in normalized_average_advantages.items() if hero not in normalized_hero_names}

        # Sort the filtered advantages
        sorted_advantages = sorted(filtered_advantages.items(), key=lambda x: x[1], reverse=True)

        return render_template('results.html', sorted_advantages=sorted_advantages, hero_images=hero_images, hero_name_mapping=hero_name_mapping)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
