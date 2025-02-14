import pandas as pd
import json
import os
from datetime import datetime

# File paths
schedule_path = 'docs/OHL_SCHEDULE/OHL_Schedule_2024_2025.csv'
predictions_folder = 'docs/JSON_DATA'
output_file = 'docs/JSON_DATA/accuracy.json'
tossup_file = 'docs/JSON_DATA/tossup_games.json'
non_tossup_file = 'docs/JSON_DATA/non_tossup_games.json'

# Load schedule
schedule_df = pd.read_csv(schedule_path)
schedule_df['Date'] = pd.to_datetime(schedule_df['Date'])
filtered_schedule = schedule_df[schedule_df['Date'] >= '2025-01-29']

# Accuracy counters
total_correct = 0
total_games = 0
tossup_correct = 0
tossup_games = 0
non_tossup_correct = 0
non_tossup_games = 0
accuracy_data = []
tossup_games_data = []
non_tossup_games_data = []

# Process predictions for each game date
for date in filtered_schedule['Date'].unique():
    date_str = pd.to_datetime(date).strftime('%Y-%m-%d')
    prediction_file_path = f'{predictions_folder}/{date_str}.json'

    if os.path.exists(prediction_file_path):
        with open(prediction_file_path, 'r') as file:
            predictions = json.load(file)

        games_today = filtered_schedule[filtered_schedule['Date'] == date]
        correct_predictions = 0
        games_count = 0
        game_details = []

        for _, game in games_today.iterrows():
            predicted_game = next(
                (p for p in predictions if p['home_team'] == game['HomeTeam'] and p['away_team'] == game['AwayTeam']), None)
            
            if predicted_game:
                # Determine the actual winner
                if game['HomeGoals'] == 0 and game['AwayGoals'] == 0:
                    actual_winner = "Not Started"
                else:
                    actual_winner = game['HomeTeam'] if game['HomeGoals'] > game['AwayGoals'] else game['AwayTeam']
                    games_count += 1
                    total_games += 1

                    if predicted_game['winner'] == actual_winner:
                        correct_predictions += 1
                        total_correct += 1

                    # Toss-up logic: Both teams must have negative odds
                    is_tossup = (
                        predicted_game['odds'].get(game['HomeTeam'], '').startswith('-') and
                        predicted_game['odds'].get(game['AwayTeam'], '').startswith('-')
                    )

                    game_data = {
                        'date': date_str,
                        'home_team': game['HomeTeam'],
                        'away_team': game['AwayTeam'],
                        'predicted_winner': predicted_game['winner'],
                        'actual_winner': actual_winner,
                        'home_score': game['HomeGoals'],
                        'away_score': game['AwayGoals'],
                        'odds': predicted_game['odds']
                    }

                    if is_tossup:
                        tossup_games += 1
                        tossup_games_data.append(game_data)
                        if predicted_game['winner'] == actual_winner:
                            tossup_correct += 1
                    else:
                        non_tossup_games += 1
                        non_tossup_games_data.append(game_data)
                        if predicted_game['winner'] == actual_winner:
                            non_tossup_correct += 1

                # Add game details for daily accuracy summary, including odds
                game_details.append({
                    'home_team': game['HomeTeam'],
                    'away_team': game['AwayTeam'],
                    'predicted_winner': predicted_game['winner'],
                    'actual_winner': actual_winner,
                    'home_score': game['HomeGoals'],
                    'away_score': game['AwayGoals'],
                    'odds': predicted_game['odds']  # Keep odds for accuracy tracking
                })

        # Calculate daily accuracy
        accuracy_percent = round((correct_predictions / games_count) * 100, 1) if games_count > 0 else 0
        accuracy_data.append({
            'date': date_str,
            'accuracy': accuracy_percent,
            'correct_predictions': correct_predictions,
            'total_games': games_count,
            'game_details': game_details
        })

# Calculate summary accuracies
total_accuracy = round((total_correct / total_games) * 100, 1) if total_games > 0 else 0
tossup_accuracy = round((tossup_correct / tossup_games) * 100, 1) if tossup_games > 0 else 0
non_tossup_accuracy = round((non_tossup_correct / non_tossup_games) * 100, 1) if non_tossup_games > 0 else 0

# Create summary JSON
summary = {
    'daily_accuracies': accuracy_data,
    'total_accuracy': total_accuracy,
    'tossup_accuracy': tossup_accuracy,
    'non_tossup_accuracy': non_tossup_accuracy,
    'total_correct': total_correct,
    'total_games': total_games,
    'tossup_correct': tossup_correct,
    'tossup_games': tossup_games,
    'non_tossup_correct': non_tossup_correct,
    'non_tossup_games': non_tossup_games
}

# Save summary to files
with open(output_file, 'w') as outfile:
    json.dump(summary, outfile, indent=4)

with open(tossup_file, 'w') as tossup_outfile:
    json.dump(tossup_games_data, tossup_outfile, indent=4)

with open(non_tossup_file, 'w') as non_tossup_outfile:
    json.dump(non_tossup_games_data, non_tossup_outfile, indent=4)

print(f"Accuracy summary saved to {output_file}")
print(f"Toss-up games saved to {tossup_file}")
print(f"Non-toss-up games saved to {non_tossup_file}")
