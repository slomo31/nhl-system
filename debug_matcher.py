"""
Debug Matcher - Figure out why matching is failing
"""

import pandas as pd
import glob
from datetime import timedelta

# Load decisions
decision_files = glob.glob('output_archive/decisions/*_decisions.csv')
all_decisions = []
for file in sorted(decision_files):
    df = pd.read_csv(file)
    all_decisions.append(df)

decisions = pd.concat(all_decisions, ignore_index=True)
decisions['game_time_parsed'] = pd.to_datetime(decisions['game_time'], utc=True)
decisions['game_date'] = decisions['game_time_parsed'].dt.date

# Load completed games
completed = pd.read_csv('data/nhl_completed_games_2024_2025.csv')
completed['Date'] = pd.to_datetime(completed['Date']).dt.date

print("=" * 80)
print("DECISION FILE SAMPLE:")
print("=" * 80)
sample = decisions[decisions['decision'] == 'YES'].head(3)
for _, row in sample.iterrows():
    print(f"\nGame: {row['game']}")
    print(f"Date: {row['game_date']}")
    print(f"Decision: {row['decision']}")

print("\n" + "=" * 80)
print("COMPLETED GAMES SAMPLE (Recent):")
print("=" * 80)
recent = completed[completed['Date'] >= pd.to_datetime('2025-11-11').date()]
for _, row in recent.iterrows():
    print(f"\nDate: {row['Date']}")
    print(f"Game: {row['Away_Team']} @ {row['Home_Team']}")
    print(f"Total: {row['Total_Goals']}")

print("\n" + "=" * 80)
print("TESTING MATCH LOGIC:")
print("=" * 80)

# Test one match
test_pred = decisions[decisions['decision'] == 'YES'].iloc[0]
test_date = test_pred['game_date']
test_game = test_pred['game']

print(f"\nTest Prediction:")
print(f"  Date: {test_date}")
print(f"  Game: {test_game}")

# Parse game
parts = test_game.split(' @ ')
if len(parts) == 2:
    print(f"  Away (full): {parts[0]}")
    print(f"  Home (full): {parts[1]}")
    
    # Check dates
    dates = [test_date - timedelta(days=1), test_date, test_date + timedelta(days=1)]
    print(f"\n  Checking dates: {dates}")
    
    # Look for matches
    matches = completed[completed['Date'].isin(dates)]
    print(f"\n  Games on those dates: {len(matches)}")
    
    for _, comp in matches.iterrows():
        away = comp['Away_Team']
        home = comp['Home_Team']
        
        print(f"\n    Checking: {away} @ {home}")
        print(f"      Away '{away}' in '{parts[0]}'? {away in parts[0]}")
        print(f"      Home '{home}' in '{parts[1]}'? {home in parts[1]}")
        
        if away in parts[0] and home in parts[1]:
            print(f"      ✅ MATCH FOUND!")
            break
