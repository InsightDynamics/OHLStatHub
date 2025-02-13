import os
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import sys

# Store season ID
season_id = 79

# OHL team IDs
ohl_teams = [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 34]

# Create an empty list to store player data
output = []

# Total number of teams and sleep time per team
total_teams = len(ohl_teams)
total_duration = 3  # Total duration in seconds
sleep_time = total_duration / total_teams  # Sleep time between requests

# Calculate the estimated completion time
start_time = datetime.now()
end_time = start_time + timedelta(seconds=total_duration)

# Print start and estimated completion times
print(f"Script started at: {start_time.strftime('%H:%M:%S')}")
print(f"Estimated completion time: {end_time.strftime('%H:%M:%S')}\n")

# Function to print a progress bar
def print_progress_bar(current, total, bar_length=40):
    progress = current / total
    block = int(bar_length * progress)
    bar = "#" * block + "-" * (bar_length - block)
    sys.stdout.write(f"\r[{bar}] {current}/{total} teams completed")
    sys.stdout.flush()

# Create the output directory if it doesn't exist
output_dir = "docs/OHL_ROSTERS"
os.makedirs(output_dir, exist_ok=True)

# Retrieve the API base URL from the environment variable
base_url = os.environ.get("ROSTERS_API")
if not base_url:
    print("Error: ROSTERS_API environment variable is not set.")
    sys.exit(1)

# Iterate over each team ID
for index, team_id in enumerate(ohl_teams, start=1):
    # Construct the full URL
    url = f"{base_url}&season_id={season_id}&team_id={team_id}"
    
    # Fetch data from the URL
    response = requests.get(url)
    response.raise_for_status()
    json_data = response.json()
    
    # Extract player list and exclude the last item (coaches/managers)
    player_list = json_data.get("SiteKit", {}).get("Roster", [])[:-1]
    
    # Extract the team name from the JSON data
    team_name = player_list[0].get("team_name", f"Team_{team_id}").replace(" ", "_") if player_list else f"Team_{team_id}"

    # Process each player in the roster
    team_roster = []  # Create a separate list for each team
    for player in player_list:
        try:
            # Extract height and ensure proper formatting
            raw_height = player.get("height", None)
            formatted_height = None
            if raw_height:
                formatted_height = raw_height if "." in raw_height else f"{raw_height}.00"

            # Create a dictionary for each player
            player_bio = {
                "player_id": int(player.get("player_id", None)),
                "full_name": player.get("name", None),
                "last_name": player.get("last_name", None),
                "first_name": player.get("first_name", None),
                "pos": player.get("position", None),
                "shoots": player.get("shoots", None),
                "height": formatted_height,
                "weight": float(player.get("weight", 0)) if player.get("weight") else None,
                "birthdate": datetime.strptime(player.get("birthdate", "1900-01-01"), "%Y-%m-%d").date() if player.get("birthdate") else None,
                "team_name": player.get("team_name", None),
                "division": player.get("division", None),
                "jersey_number": int(player.get("tp_jersey_number", None)) if player.get("tp_jersey_number") else None,
                "rookie": int(player.get("rookie", None)) if player.get("rookie") else None,
            }
            output.append(player_bio)  # Append to the overall output
            team_roster.append(player_bio)  # Append to the team-specific roster
        except Exception as e:
            print(f"Error processing player data: {e}")

    # Convert the team roster to a Pandas DataFrame and save as a CSV file
    team_df = pd.DataFrame(team_roster).drop_duplicates()
    team_file_path = os.path.join(output_dir, f"{team_name}.csv")
    team_df.to_csv(team_file_path, index=False)

    # Update the progress bar
    print_progress_bar(index, total_teams)
    
    # Sleep for the calculated duration to ensure total run time is consistent
    if index < total_teams:
        time.sleep(sleep_time)

# Convert the list of player data to a Pandas DataFrame
output_df = pd.DataFrame(output).drop_duplicates()

# Save the overall roster data
overall_file_path = os.path.join(output_dir, "OHL_ROSTERS_2024_2025.csv")
output_df.to_csv(overall_file_path, index=False)

print("\n\nRoster data has been saved to the working directory.")
print(f"Script completed at: {datetime.now().strftime('%H:%M:%S')}")
