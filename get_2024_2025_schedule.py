import requests
import pandas as pd
import os

# Define output file path
output_file = "docs/OHL_SCHEDULE/OHL_Schedule_2024_2025.csv"

# Ensure output directory exists
os.makedirs(os.path.dirname(output_file), exist_ok=True)

def get_schedule(output_file):
    """Fetches OHL schedule, processes it, and saves it as a CSV file."""
    
    # Retrieve the API URL from environment variable
    url_schedule = os.environ.get("SCHEDULE_API")
    if not url_schedule:
        print("Error: SCHEDULE_API environment variable is not set.")
        return

    try:
        # Fetch JSON data from API
        response = requests.get(url_schedule)
        response.raise_for_status()  # Raise an error for failed requests

        json_data = response.json()

        # Debug: Print JSON structure
        print("JSON structure keys:", json_data.keys())

        # Extract games data
        if "SiteKit" in json_data and "Scorebar" in json_data["SiteKit"]:
            games_data = json_data["SiteKit"]["Scorebar"]
        else:
            raise ValueError("Could not extract games data from JSON.")

        # Convert to DataFrame
        df = pd.DataFrame(games_data)

        # Select relevant columns and rename them
        schedule_df = df[[
            "Date",
            "ScheduledFormattedTime",
            "HomeLongName",
            "HomeGoals",
            "VisitorLongName",
            "VisitorGoals",
            "ID"
        ]].rename(columns={
            "ScheduledFormattedTime": "Time",
            "HomeLongName": "HomeTeam",
            "VisitorLongName": "AwayTeam",
            "VisitorGoals": "AwayGoals",
            "ID": "GameID"
        })

        # Convert "Date" to datetime and filter for games from September 25, 2024, onward
        schedule_df["Date"] = pd.to_datetime(schedule_df["Date"])
        schedule_df = schedule_df[schedule_df["Date"] >= "2024-09-25"]

        # Save DataFrame to CSV
        schedule_df.to_csv(output_file, index=False)

        print(f"Schedule saved successfully: {output_file}")
        print(schedule_df.head())

        return schedule_df

    except requests.RequestException as e:
        print(f"Error fetching schedule: {e}")
    except Exception as e:
        print(f"Error processing schedule: {e}")

# Run the function
if __name__ == "__main__":
    get_schedule(output_file)
