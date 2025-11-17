"""
NHL Automated Results Tracker
==============================
Automatically matches yesterday's YES picks to actual results
No manual logging needed!

Usage:
    python update_results.py
"""

import pandas as pd
import os
from datetime import datetime, timedelta
import glob


def update_results():
    """Automatically update results from yesterday's games"""
    
    print("\n" + "=" * 80)
    print("🏒 NHL AUTOMATED RESULTS UPDATER")
    print("=" * 80)
    print()
    
    # Step 1: Load ALL decision files
    decision_files = glob.glob('output_archive/decisions/*_decisions.csv')
    
    if not decision_files:
        print("❌ No decision files found")
        return
    
    all_decisions = []
    for file in sorted(decision_files):
        df = pd.read_csv(file)
        all_decisions.append(df)
    
    decisions = pd.concat(all_decisions, ignore_index=True)
    
    # Remove duplicates - keep highest confidence
    decisions['game_time_parsed'] = pd.to_datetime(decisions['game_time'], utc=True)
    decisions['game_key'] = (
        decisions['game_time_parsed'].dt.date.astype(str) + '_' + 
        decisions['game']
    )
    decisions = decisions.sort_values('confidence', ascending=False)
    decisions = decisions.drop_duplicates(subset='game_key', keep='first')
    
    print(f"📊 Loaded {len(decisions)} unique predictions")
    
    # Step 2: Load completed games
    try:
        completed = pd.read_csv('data/nhl_completed_games_2024_2025.csv')
        completed['Date'] = pd.to_datetime(completed['Date']).dt.date
        print(f"✅ Loaded {len(completed)} completed games")
    except FileNotFoundError:
        print("❌ No completed games file found")
        print("   Run: python data_collection/game_results_collector.py")
        return
    
    # Step 3: Match predictions to results
    decisions['game_date'] = decisions['game_time_parsed'].dt.date
    decisions['actual_total'] = None
    decisions['result'] = 'PENDING'
    
    matched = 0
    
    for idx, pred in decisions.iterrows():
        if pred['decision'] != 'YES':
            continue
        
        game_date = pred['game_date']
        
        # Parse game (e.g., "Washington Capitals @ Carolina Hurricanes")
        parts = pred['game'].split(' @ ')
        if len(parts) != 2:
            continue
        
        # Check +/- 1 day for timezone
        dates = [game_date - timedelta(days=1), game_date, game_date + timedelta(days=1)]
        
        # Find matching completed game
        for _, comp in completed.iterrows():
            if comp['Date'] not in dates:
                continue
            
            # Match using abbreviations to full names mapping
            away_abbrev = comp['Away_Team']
            home_abbrev = comp['Home_Team']
            
            # Create simple mapping (abbreviation appears somewhere in full name usually)
            # But we need exact team name matching, so use a comprehensive map
            team_map = {
                'ANA': 'Anaheim', 'BOS': 'Boston', 'BUF': 'Buffalo', 'CGY': 'Calgary',
                'CAR': 'Carolina', 'CHI': 'Chicago', 'COL': 'Colorado', 'CBJ': 'Columbus',
                'DAL': 'Dallas', 'DET': 'Detroit', 'EDM': 'Edmonton', 'FLA': 'Florida',
                'LAK': 'Los Angeles', 'MIN': 'Minnesota', 'MTL': 'Montréal', 'NSH': 'Nashville',
                'NJD': 'New Jersey', 'NYI': 'New York Islanders', 'NYR': 'New York Rangers',
                'OTT': 'Ottawa', 'PHI': 'Philadelphia', 'PIT': 'Pittsburgh', 'SJS': 'San Jose',
                'SEA': 'Seattle', 'STL': 'St Louis', 'TBL': 'Tampa Bay', 'TOR': 'Toronto',
                'VAN': 'Vancouver', 'VGK': 'Vegas', 'WSH': 'Washington', 'WPG': 'Winnipeg',
                'UTA': 'Utah'
            }
            
            # Get full name equivalents
            away_full = team_map.get(away_abbrev, away_abbrev)
            home_full = team_map.get(home_abbrev, home_abbrev)
            
            # Check if these match the prediction
            if away_full in parts[0] and home_full in parts[1]:
                actual = comp['Total_Goals']
                decisions.at[idx, 'actual_total'] = actual
                
                if actual > pred['minimum_total']:
                    decisions.at[idx, 'result'] = 'WIN'
                else:
                    decisions.at[idx, 'result'] = 'LOSS'
                
                matched += 1
                break
    
    print(f"🔗 Matched {matched} YES bets to completed games")
    print()
    
    # Step 4: Save updated results
    decisions.to_csv('nhl_system_results.csv', index=False)
    
    # Step 5: Show summary
    yes_bets = decisions[decisions['decision'] == 'YES']
    wins = len(yes_bets[yes_bets['result'] == 'WIN'])
    losses = len(yes_bets[yes_bets['result'] == 'LOSS'])
    pending = len(yes_bets[yes_bets['result'] == 'PENDING'])
    
    total = wins + losses
    win_rate = (wins / total * 100) if total > 0 else 0
    
    print("=" * 80)
    print("📊 SYSTEM RECORD")
    print("=" * 80)
    print(f"\n✅ Wins: {wins}")
    print(f"❌ Losses: {losses}")
    print(f"⏳ Pending: {pending}")
    print(f"\n📈 Win Rate: {win_rate:.1f}% ({wins}-{losses})")
    
    if total > 0:
        # Show recent results
        print(f"\n📅 LAST 10 COMPLETED GAMES:")
        print("-" * 80)
        
        recent = yes_bets[yes_bets['result'] != 'PENDING'].sort_values('game_date', ascending=False).head(10)
        
        for _, game in recent.iterrows():
            status = "✅" if game['result'] == 'WIN' else "❌"
            date = game['game_date'].strftime('%Y-%m-%d')
            buffer = game['actual_total'] - game['minimum_total']
            elite = "🔥" if game['elite_goalie_flag'] else ""
            
            print(f"{status} {date} | {game['game']}")
            print(f"   Line: {game['minimum_total']:.1f} | Actual: {game['actual_total']:.1f} | Buffer: {buffer:+.1f} | Conf: {game['confidence']}% {elite}")
    
    print()
    print("=" * 80)
    print(f"💾 Full results saved to: nhl_system_results.csv")
    print()


if __name__ == "__main__":
    update_results()