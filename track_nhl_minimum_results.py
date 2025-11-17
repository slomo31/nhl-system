"""
NHL Minimum Total System - Results Tracker
===========================================
Analyzes all past predictions against actual game results

Usage:
    python track_nhl_minimum_results.py
"""

import pandas as pd
import os
from datetime import datetime, timedelta
import glob


def load_all_decisions():
    """Load all decision CSVs from archive"""
    decision_files = glob.glob('output_archive/decisions/*_decisions.csv')
    
    if not decision_files:
        print("❌ No decision files found in output_archive/decisions/")
        return None
    
    all_decisions = []
    
    for file in sorted(decision_files):
        df = pd.read_csv(file)
        df['source_file'] = os.path.basename(file)
        all_decisions.append(df)
    
    combined = pd.concat(all_decisions, ignore_index=True)
    print(f"✅ Loaded {len(combined)} predictions from {len(decision_files)} files")
    
    # Remove duplicates - keep highest confidence
    combined['game_time_parsed'] = pd.to_datetime(combined['game_time'], utc=True)
    combined['game_key'] = (
        combined['game_time_parsed'].dt.date.astype(str) + '_' + 
        combined['game']
    )
    
    combined = combined.sort_values('confidence', ascending=False)
    deduplicated = combined.drop_duplicates(subset='game_key', keep='first')
    
    duplicates_removed = len(combined) - len(deduplicated)
    if duplicates_removed > 0:
        print(f"🔄 Removed {duplicates_removed} duplicate predictions")
    
    print(f"📊 Analyzing {len(deduplicated)} unique games")
    
    return deduplicated


def load_completed_games():
    """Load completed NHL games with results"""
    try:
        games = pd.read_csv('data/nhl_completed_games_2024_2025.csv')
        print(f"✅ Loaded {len(games)} completed games")
        return games
    except FileNotFoundError:
        print("⚠️  No completed games file found")
        return pd.DataFrame()


def match_predictions_to_results(decisions_df, completed_games_df):
    """Match each prediction to its actual result"""
    
    if completed_games_df.empty:
        print("⚠️  No completed games to match against")
        return decisions_df
    
    # Parse dates
    decisions_df['game_date'] = pd.to_datetime(decisions_df['game_time'], utc=True).dt.date
    completed_games_df['Date'] = pd.to_datetime(completed_games_df['Date']).dt.date
    
    # Add result columns
    decisions_df['actual_total'] = None
    decisions_df['result'] = 'PENDING'
    
    matched_count = 0
    
    for idx, pred in decisions_df.iterrows():
        game_date = pred['game_date']
        
        # Parse game string
        parts = pred['game'].split(' @ ')
        if len(parts) != 2:
            continue
        
        away_full = parts[0].strip()
        home_full = parts[1].strip()
        
        # Check +/- 1 day for timezone differences
        dates_to_check = [
            game_date,
            game_date - timedelta(days=1),
            game_date + timedelta(days=1)
        ]
        
        # Find matching completed game
        for _, comp_game in completed_games_df.iterrows():
            if comp_game['Date'] not in dates_to_check:
                continue
            
            away_team = comp_game['Away_Team']
            home_team = comp_game['Home_Team']
            
            # Match if abbreviations are in full names
            if away_team in away_full and home_team in home_full:
                actual_total = comp_game['Total_Goals']
                decisions_df.at[idx, 'actual_total'] = actual_total
                
                minimum = pred['minimum_total']
                
                if pred['decision'] == 'YES':
                    if actual_total > minimum:
                        decisions_df.at[idx, 'result'] = 'WIN'
                    else:
                        decisions_df.at[idx, 'result'] = 'LOSS'
                    matched_count += 1
                
                elif pred['decision'] == 'NO':
                    if actual_total > minimum:
                        decisions_df.at[idx, 'result'] = 'WOULD_WIN'
                    else:
                        decisions_df.at[idx, 'result'] = 'CORRECT_SKIP'
                    matched_count += 1
                break
    
    print(f"🔗 Matched {matched_count} predictions to completed games")
    
    return decisions_df


def generate_report(decisions_df):
    """Generate the performance report"""
    
    print("\n" + "=" * 80)
    print("🏒 NHL MINIMUM TOTAL SYSTEM - 2024-2025 SEASON RESULTS")
    print("=" * 80)
    print()
    
    # Filter YES and NO bets
    yes_bets = decisions_df[decisions_df['decision'] == 'YES'].copy()
    no_bets = decisions_df[decisions_df['decision'] == 'NO'].copy()
    
    # YES BETS SECTION
    if len(yes_bets) > 0:
        wins = len(yes_bets[yes_bets['result'] == 'WIN'])
        losses = len(yes_bets[yes_bets['result'] == 'LOSS'])
        pending = len(yes_bets[yes_bets['result'] == 'PENDING'])
        
        win_pct = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
        
        print(f"✅ YES BETS: {wins}-{losses} ({win_pct:.1f}%) - {pending} pending")
        print("-" * 80)
        print()
        
        # Show completed games
        completed_yes = yes_bets[yes_bets['result'] != 'PENDING'].sort_values('game_date')
        
        for _, row in completed_yes.iterrows():
            status = "✅ WIN" if row['result'] == 'WIN' else "❌ LOSS"
            date_str = row['game_date'].strftime('%Y-%m-%d')
            buffer = row['actual_total'] - row['minimum_total']
            
            print(f"{status} | {date_str} | {row['game']}")
            print(f"     Line: {row['minimum_total']:.1f} | Actual: {row['actual_total']:.1f} | Buffer: {buffer:+.1f} | Conf: {row['confidence']}%")
            
            if row['elite_goalie_flag']:
                print(f"     🔥 Elite goalie flagged")
            
            print()
        
        # Show pending games
        if pending > 0:
            print()
            print(f"⏳ PENDING ({pending} games not yet completed):")
            print()
            pending_yes = yes_bets[yes_bets['result'] == 'PENDING'].sort_values('game_date')
            for _, row in pending_yes.iterrows():
                date_str = row['game_date'].strftime('%Y-%m-%d')
                elite = "🔥" if row['elite_goalie_flag'] else ""
                print(f"     {date_str} | {row['game']} | Line: {row['minimum_total']:.1f} | {row['confidence']}% {elite}")
    else:
        print("❌ YES BETS: No bets yet this season")
        print("-" * 80)
    
    # NO BETS SECTION
    print()
    print()
    print(f"❌ NO BETS: {len(no_bets)} games skipped")
    print("-" * 80)
    print()
    
    if len(no_bets) > 0:
        missed_opportunities = 0
        correct_skips = 0
        
        completed_no = no_bets[no_bets['result'] != 'PENDING'].sort_values('game_date')
        
        for _, row in completed_no.iterrows():
            date_str = row['game_date'].strftime('%Y-%m-%d')
            
            if row['result'] == 'WOULD_WIN':
                status = "⚠️  MISSED"
                missed_opportunities += 1
            else:
                status = "✅ CORRECT"
                correct_skips += 1
            
            if pd.notna(row['actual_total']):
                buffer = row['actual_total'] - row['minimum_total']
                print(f"{status} | {date_str} | {row['game']}")
                print(f"        Line: {row['minimum_total']:.1f} | Actual: {row['actual_total']:.1f} | Buffer: {buffer:+.1f} | Conf: {row['confidence']}%")
                print()
        
        if missed_opportunities > 0:
            print()
            print(f"⚠️  MISSED {missed_opportunities} OPPORTUNITIES (would have won if we bet)")
        
        if correct_skips > 0:
            print(f"✅ {correct_skips} CORRECT SKIPS (game went under minimum)")
    
    print()
    print("=" * 80)
    
    # Final summary
    if len(yes_bets) > 0 and (wins + losses) > 0:
        total_wagered = (wins + losses) * 100  # $100 per bet
        # Assuming -800 avg odds = 12.5% profit per win
        avg_profit_per_win = 100 * (100 / 800)
        total_profit = (wins * avg_profit_per_win) - (losses * 100)
        roi = (total_profit / total_wagered * 100) if total_wagered > 0 else 0
        
        print()
        print("📊 SUMMARY")
        print("-" * 80)
        print(f"Completed YES bets: {wins + losses}")
        print(f"Win rate: {win_pct:.1f}%")
        print(f"Total wagered: ${total_wagered:.2f}")
        print(f"Total profit: ${total_profit:+.2f}")
        print(f"ROI: {roi:+.1f}% (assuming -800 avg odds)")
        
        # Elite goalie stats
        elite_yes = yes_bets[yes_bets['elite_goalie_flag'] == True]
        if len(elite_yes) > 0:
            elite_completed = elite_yes[elite_yes['result'] != 'PENDING']
            if len(elite_completed) > 0:
                elite_wins = len(elite_completed[elite_completed['result'] == 'WIN'])
                elite_rate = (elite_wins / len(elite_completed) * 100)
                print()
                print(f"🔥 Elite goalie impact:")
                print(f"   {elite_wins}/{len(elite_completed)} wins ({elite_rate:.1f}%)")
        
        print()


def main():
    """Main execution"""
    
    print("\n" + "=" * 80)
    print("🏒 NHL MINIMUM TOTAL RESULTS TRACKER")
    print("=" * 80)
    print()
    
    # Load all data
    decisions = load_all_decisions()
    if decisions is None:
        return
    
    completed_games = load_completed_games()
    
    print()
    
    # Match predictions to results
    decisions_with_results = match_predictions_to_results(decisions, completed_games)
    
    # Generate report
    generate_report(decisions_with_results)
    
    # Save the matched data
    decisions_with_results.to_csv('nhl_min_total_results_tracker.csv', index=False)
    print()
    print("💾 Full results saved to: nhl_min_total_results_tracker.csv")
    print()


if __name__ == "__main__":
    main()
