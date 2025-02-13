import pandas as pd
import requests
import os
from datetime import datetime

def fetch_json_data(url):
    """Fetch JSON data from the given URL."""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def main():
    # Retrieve the API URL from environment variable
    url_reg = os.environ.get("PLAYERSTATS_API")
    if not url_reg:
        print("Error: PLAYERSTATS_API environment variable is not set.")
        return

    # Fetch and process data
    json_data = fetch_json_data(url_reg)

    # Process player stats data
    df = pd.DataFrame(json_data['SiteKit']['Statviewtype'])
    df = df.drop(columns=['birthtown', 'birthprov', 'birthcntry', 'loose_ball_recoveries', 'caused_turnovers', 
                          'turnovers', 'phonetic_name', 'last_years_club', 'suspension_games_remaining', 
                          'suspension_indefinite'], errors='ignore')

    numeric_columns = ['player_id', 'active', 'age', 'rookie', 'jersey_number', 'team_id', 'games_played', 
                       'goals', 'assists', 'points', 'points_per_game', 'plus_minus', 'power_play_goals', 
                       'power_play_assists', 'game_winning_goals', 'empty_net_goals', 'penalty_minutes', 
                       'shots_on', 'faceoff_pct', 'num_teams']
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

    df['birthdate_year'] = df['birthdate_year'].str.split("'").str[1].astype(float) + 2000
    df['birthdate'] = pd.to_datetime(df['birthdate'], errors='coerce', format='%B %d %Y')

    # Filter and transform data
    LeagueStats_2024 = df[df['active'] == 1][[
        'player_id', 'name', 'rookie', 'jersey_number', 'birthdate', 'birthdate_year', 'height', 'weight', 
        'position', 'team_name', 'games_played', 'goals', 'assists', 'points', 'points_per_game', 'plus_minus', 
        'power_play_goals', 'power_play_assists', 'game_winning_goals', 'empty_net_goals', 'penalty_minutes'
    ]]

    # Rename columns
    LeagueStats_2024.columns = [
        'Player_ID', 'Name', 'Rookie', 'JN', 'BD', 'BD_Y', 'Hgt', 'Wgt', 'Pos', 'Team', 'GP', 'G', 'A', 'PTS', 
        'Pts/G', '+/-', 'PPG', 'PPA', 'GWG', 'ENG', 'PIM'
    ]

    # Filter out goalies
    LeagueStats_2024 = LeagueStats_2024[LeagueStats_2024['Pos'] != 'G']

    # Compute additional stats
    LeagueStats_2024['PPP'] = LeagueStats_2024['PPG'] + LeagueStats_2024['PPA']
    LeagueStats_2024['PPP_Percentage'] = (LeagueStats_2024['PPP'] / LeagueStats_2024['PTS']) * 100
    LeagueStats_2024['PPP_Percentage'] = LeagueStats_2024['PPP_Percentage'].round(1)

    LeagueStats_2024['Rookie'] = LeagueStats_2024['Rookie'].replace({1: 'YES', 0: 'NO'})
    LeagueStats_2024['RNK'] = (2 * LeagueStats_2024['G']) + (1.5 * LeagueStats_2024['A']) + \
                              (1 * LeagueStats_2024['+/-']) - (1 * LeagueStats_2024['PIM'])

    # Save the overall league stats
    output_dir = "docs/OHL_STATS"
    os.makedirs(output_dir, exist_ok=True)

    overall_file_path = os.path.join(output_dir, "LeagueStats_2024_2025.csv")
    LeagueStats_2024.to_csv(overall_file_path, index=False)

    # Save team-specific stats
    teams = LeagueStats_2024['Team'].unique()
    for team in teams:
        team_df = LeagueStats_2024[LeagueStats_2024['Team'] == team]
        team_file_path = os.path.join(output_dir, f"{team.replace(' ', '_')}.csv")
        team_df.to_csv(team_file_path, index=False)

    print(f"League stats and individual team stats saved in '{output_dir}' folder.")

if __name__ == "__main__":
    main()
