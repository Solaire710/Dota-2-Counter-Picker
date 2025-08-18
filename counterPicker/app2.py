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
    "antimage": "Anti-Mage",
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
    "centaur": "Centaur Warrunner",
    "chaos_knight": "Chaos Knight",
    "chen": "Chen",
    "clinkz": "Clinkz",
    "rattletrap": "Clockwerk",
    "crystal_maiden": "Crystal Maiden",
    "dawnbreaker": "Dawnbreaker",
    "dark_seer": "Dark Seer",
    "dark_willow": "Dark Willow",
    "dazzle": "Dazzle",
    "death_prophet": "Death Prophet",
    "disruptor": "Disruptor",
    "doom_bringer": "Doom",
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
    "wisp": "Io",
    "jakiro": "Jakiro",
    "juggernaut": "Juggernaut",
    "keeper_of_the_light": "Keeper of the Light",
    "kunkka": "Kunkka",
    "leshrac": "Leshrac",
    "legion_commander": "Legion Commander",
    "lich": "Lich",
    "life_stealer": "Lifestealer",
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
    "pangolier": "Pangolier",
    "phantom_assassin": "Phantom Assassin",
    "phantom_lancer": "Phantom Lancer",
    "phoenix": "Phoenix",
    "primal_beast": "Primal Beast",
    "puck": "Puck",
    "pudge": "Pudge",
    "pugna": "Pugna",
    "queenofpain": "Queen of Pain",
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
    "treant": "Treant Protector",
    "troll_warlord": "Troll Warlord",
    "tusk": "Tusk",
    "abyssal_underlord": "Underlord",
    "undying": "Undying",
    "ursa": "Ursa",
    "vengefulspirit": "Vengeful Spirit",
    "venomancer": "Venomancer",
    "viper": "Viper",
    "visage": "Visage",
    "void_spirit": "Void Spirit",
    "warlock": "Warlock",
    "weaver": "Weaver",
    "windrunner": "Windrunner",
    "winter_wyvern": "Winter Wyvern",
    "witch_doctor": "Witch Doctor",
    "skeleton_king": "Wraith King",
    "zuus": "Zeus",
    "muerta": "Muerta"
}

base_hero_url = 'https://cdn.akamai.steamstatic.com/apps/dota2/images/dota_react/heroes/{}.png'
hero_images = {
    value: base_hero_url.format(key)  # key is internal name, value is user-friendly name
    for key, value in hero_name_mapping.items()
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
        response = requests.get(url, headers=headers)

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

                break
        elif response.status_code == 429:
            wait_time = 2 ** retry_count
            time.sleep(wait_time)
            retry_count += 1
        else:
            break

    return advantage_percentages

@app.route('/', methods=['GET', 'POST'])
def index():
    sorted_advantages = []
    if request.method == 'POST':
        hero_names = request.form.getlist('heroes')
        hero_names = [name.strip() for name in hero_names if name.strip()]
        
        # Normalize hero names to user-friendly names
        normalized_hero_names = [
            hero_name_mapping.get(hero, hero) for hero in hero_names
        ]

        # Use normalized hero names to build URLs
        urlList = [base_url + hero.replace(" ", "_").lower() + '/counters' for hero in normalized_hero_names]
        all_hero_advantages = {}

        for url in urlList:
            advantages = fetch_win_rates(url)
            for hero, advantage in advantages.items():
                if hero not in all_hero_advantages:
                    all_hero_advantages[hero] = []
                all_hero_advantages[hero].append(advantage)

        average_advantages = {hero: sum(advantage) / len(advantage) for hero, advantage in all_hero_advantages.items()}
        sorted_advantages = sorted(average_advantages.items(), key=lambda x: x[1], reverse=True)

    return render_template(
        'index3.html',
        sorted_advantages=sorted_advantages,
        hero_images=hero_images,
        hero_name_mapping=hero_name_mapping
    )

if __name__ == '__main__':
    app.run(debug=True)
