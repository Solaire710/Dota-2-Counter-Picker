import time
import requests
from bs4 import BeautifulSoup

# Define the base URL
base_url = 'https://www.dotabuff.com/heroes/'
urlList = []

# Initialize a list with a fixed size of 5 for hero names
hero_names = [""] * 5

print("Enter up to 5 hero names (leave blank to stop):")

# Loop through the indices of the list
for i in range(5):
    user_input = input(f"Enter hero name {i + 1}: ")
    
    if user_input:  # Ensure the input is not empty
        hero_names[i] = user_input.replace(" ", "-")  # Assign the input to the list at the current index
    else:
        # If the user leaves input blank, break the loop
        break

# Remove any remaining empty strings from the list
hero_names = [name for name in hero_names if name]  # This will filter out empty entries
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
    advantage_percentages = []

    while retry_count < max_retries:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            website_code = response.text
            soup = BeautifulSoup(website_code, 'html.parser')

            # Find the sortable table
            win_rate_table = soup.find('table', class_='sortable')
            
            if win_rate_table:
                print("Win Rate Table Found")
                rows = win_rate_table.find('tbody').find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        # Extract hero name and win rate
                        hero_name_td = cells[0]
                        hero_name = hero_name_td.get('data-value') or hero_name_td.text.strip()
                        win_rate_td = cells[2]
                        data_value = win_rate_td.get('data-value')
                        win_rate_percent = win_rate_td.text.strip()  # Get the displayed win rate percentage

                        if data_value:
                            advantage_percentages.append(float(data_value))  # Collecting advantage percentages
                            print(f"{hero_name}: Win Rate - {data_value} ({win_rate_percent})")
                        else:
                            print(f"No win rate data found for {hero_name}.")
                    else:
                        print("Not enough cells in row.")
            else:
                print("Win rate table not found.")
                print(soup.prettify())  # Print the entire HTML for debugging
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

# Loop through each URL in urlList and fetch win rates
total_advantage = 0
total_heroes = 0

for url in urlList:
    print(f"Fetching data for: {url}")
    advantages = fetch_win_rates(url)
    
    # Calculate total advantages and count
    if advantages:
        total_advantage += sum(advantages)
        total_heroes += len(advantages)

# Calculate average advantage percentage if any data was collected
if total_heroes > 0:
    average_advantage = total_advantage / total_heroes
    print(f"Average Advantage Percentage Against All Input Heroes: {average_advantage:.2f}%")
else:
    print("No advantage data collected.")
