import random
import matplotlib.pyplot as plt
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import json

# Set up the ChromeDriver service
service = Service('/Users/aysudalogullari/Downloads/chromedriver-mac-x64/chromedriver')

# Initialize the Chrome driver
driver = webdriver.Chrome(service=service)

# Function to fetch real-time data
def fetch_teams_data():
    teams_data = {}

    try:
        # Open the webpage
        driver.get('https://en.volleyballworld.com/volleyball/competitions/volleyball-nations-league/2023/standings/women/#advanced')

        # Wait until the table is loaded
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'vbw-o-table-wrapper'))
        )

        # Get the page source and parse with BeautifulSoup
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Find the table containing the standings
        table = soup.find('table', class_='vbw-o-table')

        # Extract the rows from the table body
        rows = table.find('tbody').find_all('tr')

        for row in rows:
            cells = row.find_all('td')
            team_name = cells[1].text.strip()
            matches_total = int(cells[2].text.strip())
            matches_won = int(cells[3].text.strip())
            matches_lost = int(cells[4].text.strip())
            set_ratio = float(cells[14].text.strip())
            point_ratio = float(cells[17].text.strip())

            teams_data[team_name] = {
                'Matches Total': matches_total,
                'Matches Won': matches_won,
                'Matches Lost': matches_lost,
                'Set Ratio': set_ratio,
                'Point Ratio': point_ratio
            }

        # Print extracted data
        for team, data in teams_data.items():
            print(f"Team: {team}, Matches Won: {data['Matches Won']}, Matches Lost: {data['Matches Lost']}, Set Ratio: {data['Set Ratio']}, Point Ratio: {data['Point Ratio']}")

    finally:
        # Close the web driver
        driver.quit()

    return teams_data

def fetch_schedule(year, month):
    base_url = 'https://en.volleyballworld.com/api/v1/globalschedule/competitions'
    url = f'{base_url}/{year}/{month}'

    response = requests.get(url)
    if response.status_code == 200:
        schedule_data = response.json()
        return schedule_data
    else:
        print(f"Failed to retrieve data: {response.status_code}")
        return None

def parse_schedule(schedule_data):
    teams_schedule = {}

    for match in schedule_data.get('matches', []):
        home_team = match.get('home_team', {}).get('name')
        away_team = match.get('away_team', {}).get('name')
        home_score = match.get('home_score')
        away_score = match.get('away_score')
        match_date = match.get('date')

        if home_team not in teams_schedule:
            teams_schedule[home_team] = {'Matches Played': 0, 'Matches Won': 0, 'Matches Lost': 0}
        if away_team not in teams_schedule:
            teams_schedule[away_team] = {'Matches Played': 0, 'Matches Won': 0, 'Matches Lost': 0}

        teams_schedule[home_team]['Matches Played'] += 1
        teams_schedule[away_team]['Matches Played'] += 1

        if home_score > away_score:
            teams_schedule[home_team]['Matches Won'] += 1
            teams_schedule[away_team]['Matches Lost'] += 1
        else:
            teams_schedule[home_team]['Matches Lost'] += 1
            teams_schedule[away_team]['Matches Won'] += 1

    return teams_schedule

class Teams:
    def __init__(self, teams_data):
        self.teams = teams_data

    def get_teams(self):
        return self.teams

class Match:
    def __init__(self, home_team, away_team):
        self.home_team = home_team
        self.away_team = away_team

class VNLTournament:
    def __init__(self, teams):
        self.teams = teams
        self.matches = [Match(random.choice(list(teams.keys())), random.choice(list(teams.keys()))) for _ in range(12)]

    def predictability_formula(self, home_team, away_team):
        wins_squared_home = self.teams[home_team]['Matches Won'] ** 2
        wins_squared_away = self.teams[away_team]['Matches Won'] ** 2
        strength_home = self.teams[home_team]['Matches Won'] / self.teams[home_team]['Matches Total']
        strength_away = self.teams[away_team]['Matches Won'] / self.teams[away_team]['Matches Total']
        home_predictability = strength_home ** 2 / (wins_squared_home + 1)
        away_predictability = strength_away ** 2 / (wins_squared_away + 1)
        return home_team, home_predictability, away_team, away_predictability

    def run_tournament(self):
        results = []
        for match in self.matches:
            home, home_pred, away, away_pred = self.predictability_formula(match.home_team, match.away_team)
            results.append({
                'Match': f"{home} vs {away}",
                'Home Predictability': home_pred * 100,
                'Away Predictability': away_pred * 100
            })
            print(f"Match: {home} vs {away}")
            print(f"Home Predictability: {home_pred * 100:.2f}%")
            print(f"Away Predictability: {away_pred * 100:.2f}%\n")
        return results

if __name__ == '__main__':
    # Fetch real-time data
    teams_data = fetch_teams_data()

    # Initialize teams with real-time data
    teams = Teams(teams_data)

    # Run the tournament with real-time data
    tournament = VNLTournament(teams.get_teams())
    match_results = tournament.run_tournament()
    df = pd.DataFrame(match_results)

    # Plotting the Results
    fig, ax = plt.subplots(figsize=(14, 7))
    df.plot(x='Match', y=['Home Predictability', 'Away Predictability'], kind='bar', ax=ax, legend=True)
    ax.set_title('Predictability Per Match Across 12 Games')
    ax.set_xlabel('Match')
    ax.set_ylabel('Predictability (%)')
    ax.set_xticklabels(df['Match'].tolist(), rotation=45)
    plt.tight_layout()
    plt.show()
