import random
import matplotlib.pyplot as plt
import pandas as pd


class Teams:
    def __init__(self):
        # Initializing each national team name with a dictionary to hold wins, losses data is pulled from down below
        # https://en.volleyballworld.com/volleyball/competitions/volleyball-nations-league/2023/standings/women/#advanced
        self.teams = {
            'Poland': {'Wins': 10, 'Losses': 2, 'Set Ratio': 2.461, 'Point Ratio': 1.111},
            'USA': {'Wins': 10, 'Losses': 2, 'Set Ratio': 2.125, 'Point Ratio': 1.094},
            'Turkiye': {'Wins': 9, 'Losses': 3, 'Set Ratio': 2.818, 'Point Ratio': 1.185},
            'Brazil': {'Wins': 8, 'Losses': 4, 'Set Ratio': 1.555, 'Point Ratio': 1.079},
            'China': {'Wins': 8, 'Losses': 4, 'Set Ratio': 1.526, 'Point Ratio': 1.096},
            'Italy': {'Wins': 8, 'Losses': 4, 'Set Ratio': 1.260, 'Point Ratio': 1.020},
            'Japan': {'Wins': 7, 'Losses': 5, 'Set Ratio': 1.350, 'Point Ratio': 1.091},
            'Germany': {'Wins': 7, 'Losses': 5, 'Set Ratio': 1.130, 'Point Ratio': 1.007},
            'Serbia': {'Wins': 6, 'Losses': 6, 'Set Ratio': 1.000, 'Point Ratio': 1.029},
            'Canada': {'Wins': 6, 'Losses': 6, 'Set Ratio': 1.000, 'Point Ratio': 0.987},
        }
        self.total_Games = 12

    def get_teams(self):
        return self.teams


class Match:
    def __init__(self, teams):
        self.teams = teams
        self.home_team, self.away_team = self.choose_random_match()

    def choose_random_match(self):
        team_keys = list(self.teams.keys())
        random.shuffle(team_keys)  # Shuffle team list to ensure randomness
        home_team = random.choice(team_keys)
        team_keys.remove(home_team)  # Remove the chosen home team to ensure different away team
        away_team = random.choice(team_keys)
        return home_team, away_team


class VNLTournament:
    def __init__(self, teams):
        self.teams = teams
        # Generate 12 unique matches
        self.matches = [Match(teams) for i in range(12)]

    # source for the formula https://sharmaabhishekk.github.io/projects/win-probability-implementation
    def predictability_formula(self, home_team, away_team):
        wins_squared_home = self.teams[home_team]['Wins'] ** 2
        wins_squared_away = self.teams[away_team]['Wins'] ** 2
        strength_home = self.teams[home_team]['Wins'] / 12
        strength_away = self.teams[away_team]['Wins'] / 12
        home_predictability = strength_home ** 2 / (wins_squared_home + 12)
        away_predictability = strength_away ** 2 / (wins_squared_away + 12)
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
            # Print each match's result to the console
            print(f"Match: {home} vs {away}")
            print(f"Home Predictability: {home_pred * 100:.2f}%")
            print(f"Away Predictability: {away_pred * 100:.2f}%\n")
        return results


if __name__ == '__main__':
    teams = Teams()
    tournament = VNLTournament(teams.teams)
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
