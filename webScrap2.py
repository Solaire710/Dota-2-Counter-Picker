import time
import requests
from bs4 import BeautifulSoup

# Define the base URL
base_url = 'https://www.dotabuff.com/heroes/'
urlList = []

# Initialize a list for hero names
hero_names = []

print("Enter up to 5 hero names (leave blank to stop):")

# Loop through the input for hero names
for i in range(5):
    user_input = input(f"Enter hero name {i + 1}: ")
    if user_input:  # Ensure the input is not empty
        hero_names.append(user_input.replace(" ", "-").lower())  # Append formatted hero names
    else:
        break

print("Hero names:", hero_names)

# Create URLs for each hero
for name in hero_names:
    newUrl = base_url + name + '/counters'
    urlList.append(newUrl)
print("Generated URLs:", urlList)

# Define headers to mimic a regular browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'
}

# Function to fetch and parse win rates
def fetch_win_rates(url):
    max_retries = 5
    retry_count = 0
    advantage_percentages = {}

    while retry_count < max_retries:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            website_code = response.text
            soup = BeautifulSoup(website_code, 'html.parser')

            # Find the sortable table
            win_rate_table = soup.find('table', class_='sortable')
            
            if win_rate_table:
                rows = win_rate_table.find('tbody').find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        # Extract hero name and win rate
                        hero_name_td = cells[0]
                        hero_name = hero_name_td.get('data-value') or hero_name_td.text.strip()
                        win_rate_td = cells[2]
                        data_value = win_rate_td.get('data-value')
                        
                        if data_value:
                            advantage_percentages[hero_name] = float(data_value)
            break  # Exit the retry loop if successful

        elif response.status_code == 429:
            wait_time = 2 ** retry_count  # Exponential backoff
            print(f"Too many requests. Waiting for {wait_time} seconds...")
            time.sleep(wait_time)
            retry_count += 1
        else:
            print(f"Failed to retrieve the website. Status code: {response.status_code}")
            break

    return advantage_percentages

# Dictionary to store total advantages for each hero
all_hero_advantages = {}

# Loop through each URL in urlList and fetch win rates
for url in urlList:
    print(f"Fetching data for: {url}")
    advantages = fetch_win_rates(url)
    
    # Aggregate the advantages
    for hero, advantage in advantages.items():
        if hero not in all_hero_advantages:
            all_hero_advantages[hero] = []
        all_hero_advantages[hero].append(advantage)

# Print the lists of advantages for each hero before aggregation
#print("\nAdvantage Percentage Lists (Before Aggregation):")
#for hero, advantages in all_hero_advantages.items():
#    print(f"{hero}: {advantages}")

# Now calculate the average advantage percentages
average_advantages = {}

# Calculate averages
for hero, advantages in all_hero_advantages.items():
    average_advantages[hero] = sum(advantages) / len(advantages) if advantages else 0

# Ensure all heroes are represented in the output
for hero in all_hero_advantages.keys():
    if hero not in average_advantages:
        average_advantages[hero] = 0  # Or None, depending on your preference

# Output the final aggregated advantages in descending order
print("\nAggregated Advantage Percentages (Sorted):")
sorted_advantages = sorted(average_advantages.items(), key=lambda x: x[1], reverse=False)

for hero, avg in sorted_advantages:
    print(f"{hero}: Average Advantage Percentage - {avg:.2f}%")

