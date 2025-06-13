import os
import pandas as pd
from pydantic import BaseModel
from core import WorkDone
from typing import List
import datetime as dt


class Workout(BaseModel):
    date: dt.date
    work_done: List[WorkDone]

def df_to_workout(df: pd.DataFrame) -> Workout:
    
  for _, row in df.iterrows():
        # Skip rows without an exercise name (empty string or NaN)
        if pd.isna(row.get('exercise')) or row.get('exercise') == '':
            continue

def load_workout_data(directory="_Workouts"):
    """
    Load all CSV files from the specified directory into pandas DataFrames
    
    Args:
        directory (str): Path to the directory containing workout files
        
    Returns:
        dict: Dictionary mapping filenames to pandas DataFrames
    """
    workout_data = {}
    
    # Check if directory exists
    if not os.path.exists(directory):
        print(f"Directory '{directory}' not found.")
        return workout_data
    
    # List all files in directory
    files = os.listdir(directory)
    
    # Filter for CSV files
    csv_files = [f for f in files if f.endswith('.csv')]
    
    if not csv_files:
        print(f"No CSV files found in '{directory}'.")
        return workout_data
    
    # Read each CSV file into a DataFrame
    for file in csv_files:
        file_path = os.path.join(directory, file)
        try:
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Store DataFrame with filename (without extension) as key
            filename = os.path.splitext(file)[0]
            workout_data[filename] = df
            
            print(f"Loaded: {filename} ({len(df)} rows)")
        except Exception as e:
            print(f"Error loading {file}: {str(e)}")
    
    return workout_data


# Load all workout files
workouts = load_workout_data()

# Example: Access a specific workout by name
# If you have a file "_Workouts/Running_Log.csv", access it with:
# running_df = workouts["Running_Log"] 

# Example: Process all workouts
for name, df in workouts.items():
    print(f"\nWorkout: {name}")
    print(f"Shape: {df.shape}")
    print(f"Columns: {', '.join(df.columns)}")