"""
NHL V3.1 Results Tracker
========================
Tracks Monte Carlo system results separately from legacy system.

Usage:
    python nhl_results_tracker_v31.py
"""

import pandas as pd
import os
from datetime import datetime, timedelta


def load_or_create_results():
    """Load existing results or create new file"""
    results_file = 'nhl_system_results.csv'
    
    if os.path.exists(results_file):
        return pd.read_csv(results_file)
    else:
        return pd.DataFrame(columns=[
            'date', 'game', 'minimum_total', 'actual_total',
            'decision', 'hit_rate', 'flag_count', 'flags',
            'result', 'system'
        ])


def load_completed_games():
    """Load completed games to get actual scores"""
    try:
        df = pd.read_csv('data/nhl_completed_games_2024_2025.csv')
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    except FileNotFoundError:
        print("❌ Completed games file not found")
        return None


def load_todays_decisions():
    """Load the most recent decisions file"""
    decisions_dir = 'output_archive/decisions'
    
    if not os.path.exists(decisions_dir):
        return None
    
    files = sorted([f for f in os.listdir(decisions_dir) if f.endswith('.csv')], reverse=True)
    
    if files:
        return pd.read_csv(os.path.join(decisions_dir, files[0]))
    return None


def update_results():
    """Update results with actual game outcomes"""
    print("\n" + "=" * 60)
    print("🏒 NHL V3.1 RESULTS TRACKER")
    print("=" * 60)
    
    results_df = load_or_create_results()
    completed_games = load_completed_games()
    decisions = load_todays_decisions()
    
    if completed_games is None:
        print("❌ Cannot update without completed games data")
        return
    
    # Update pending results
    pending = results_df[results_df['result'] == 'PENDING']
    
    updated_count = 0
    for idx, row in pending.iterrows():
        game_date = pd.to_datetime(row['date'])
        
        # Find matching completed game
        matching = completed_games[
            (completed_games['Date'].dt.date == game_date.date())
        ]
        
        # Try to match by team names
        for _, completed in matching.iterrows():
            game_str = row['game'].lower()
            away = completed['Away_Team'].lower()
            home = completed['Home_Team'].lower()
            
            if away in game_str or home in game_str:
                actual_total = completed['Total_Goals']
                results_df.at[idx, 'actual_total'] = actual_total
                
                # Determine result
                if actual_total > row['minimum_total']:
                    results_df.at[idx, 'result'] = 'WIN'
                else:
                    results_df.at[idx, 'result'] = 'LOSS'
                
                updated_count += 1
                print(f"   ✅ Updated: {row['game']} - {results_df.at[idx, 'result']}")
                break
    
    # Add new decisions if they exist
    if decisions is not None:
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Check for YES decisions not yet tracked
        yes_decisions = decisions[decisions['decision'] == 'YES']
        
        for _, dec in yes_decisions.iterrows():
            # Check if already tracked
            existing = results_df[
                (results_df['date'] == today) & 
                (results_df['game'] == dec['game'])
            ]
            
            if len(existing) == 0:
                new_row = {
                    'date': today,
                    'game': dec['game'],
                    'minimum_total': dec['minimum_total'],
                    'actual_total': None,
                    'decision': 'YES',
                    'hit_rate': dec.get('hit_rate', 0),
                    'flag_count': dec.get('flag_count', 0),
                    'flags': dec.get('flags', ''),
                    'result': 'PENDING',
                    'system': 'monte_carlo'
                }
                results_df = pd.concat([results_df, pd.DataFrame([new_row])], ignore_index=True)
                print(f"   ➕ Added: {dec['game']} (PENDING)")
    
    # Save updated results
    results_df.to_csv('nhl_system_results.csv', index=False)
    
    # Print summary
    mc_results = results_df[results_df['system'] == 'monte_carlo']
    mc_completed = mc_results[mc_results['result'].isin(['WIN', 'LOSS'])]
    
    if len(mc_completed) > 0:
        mc_wins = len(mc_completed[mc_completed['result'] == 'WIN'])
        mc_losses = len(mc_completed[mc_completed['result'] == 'LOSS'])
        mc_rate = mc_wins / len(mc_completed) * 100
        
        print(f"\n📊 MONTE CARLO RESULTS:")
        print(f"   Record: {mc_wins}-{mc_losses} ({mc_rate:.1f}%)")
        print(f"   Pending: {len(mc_results[mc_results['result'] == 'PENDING'])}")
    
    print(f"\n✅ Results saved to nhl_system_results.csv")
    print(f"   Updated {updated_count} games")


def main():
    update_results()


if __name__ == "__main__":
    main()
