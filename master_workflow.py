"""
NHL MINIMUM SYSTEM - MASTER WORKFLOW
=====================================
Main daily command - runs complete prediction pipeline

Usage:
    python master_workflow.py
"""

import pandas as pd
import sys
import os
from datetime import datetime

# Import all components (CORRECT subdirectory imports)
from data_collection.nhl_stats_collector import NHLStatsCollector
from data_collection.goalie_stats_collector import GoalieStatsCollector
from data_collection.game_results_collector import GameResultsCollector
from data_collection.odds_minimum_fetcher import MinimumAlternateFetcher
from core.minimum_total_predictor import MinimumTotalPredictor
from decision.yes_no_decider import YesNoDecider
from output.csv_exporter import CSVExporter
from team_name_mapper import map_team_name

def main():
    """Run complete daily workflow"""
    
    print("\n" + "=" * 70)
    print("🏒 NHL MINIMUM TOTAL SYSTEM - MASTER WORKFLOW")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Step 1: Load team stats
    print("\n📊 STEP 1: Loading team stats...")
    team_stats_file = 'data/nhl_team_stats_2024_2025.csv'
    
    if not os.path.exists(team_stats_file):
        print("⚠️  Team stats not found. Collecting now...")
        collector = NHLStatsCollector()
        team_stats = collector.collect_team_stats()
        if team_stats is None:
            print("❌ Failed to collect team stats")
            return
    else:
        team_stats = pd.read_csv(team_stats_file)
        print(f"✅ Loaded {len(team_stats)} teams")
    
    # Step 2: Load goalie stats
    print("\n🥅 STEP 2: Loading goalie stats...")
    goalie_stats_file = 'data/nhl_goalie_stats_2024_2025.csv'
    
    if not os.path.exists(goalie_stats_file):
        print("⚠️  Goalie stats not found. Collecting now...")
        collector = GoalieStatsCollector()
        goalie_stats = collector.collect_goalie_stats()
        if goalie_stats is None:
            print("❌ Failed to collect goalie stats")
            return
    else:
        goalie_stats = pd.read_csv(goalie_stats_file)
        elite_count = goalie_stats['Is_Elite_Hot'].sum()
        print(f"✅ Loaded {len(goalie_stats)} goalies ({elite_count} elite hot)")
    
    # Step 3: Load completed games
    print("\n📅 STEP 3: Loading completed games...")
    completed_games_file = 'data/nhl_completed_games_2024_2025.csv'
    
    if not os.path.exists(completed_games_file):
        print("⚠️  Completed games not found. Collecting now...")
        collector = GameResultsCollector()
        completed_games = collector.collect_completed_games()
        if completed_games is None:
            print("❌ Failed to collect completed games")
            return
    else:
        completed_games = pd.read_csv(completed_games_file)
        print(f"✅ Loaded {len(completed_games)} completed games")
    
    # Step 4: Fetch today's games with minimum alternates
    print("\n🎯 STEP 4: Fetching today's games and minimum alternates...")
    fetcher = MinimumAlternateFetcher()
    
    # Test API
    if not fetcher.test_api_connection():
        print("❌ Cannot proceed without API connection")
        return
    
    # Get today's games
    games_df = fetcher.fetch_upcoming_games()
    
    if games_df is None or len(games_df) == 0:
        print("\n⚠️  No games today. Enjoy your day off!")
        return
    
    # Fetch minimum alternates
    minimums_df = fetcher.fetch_all_minimums(games_df)
    
    if minimums_df is None:
        print("❌ No minimum alternates available")
        return
    
    # Step 5: Run predictions
    print("\n🤖 STEP 5: Running predictions...")
    predictor = MinimumTotalPredictor(team_stats, completed_games, goalie_stats)
    decider = YesNoDecider()
    
    all_decisions = []
    
    for _, game in minimums_df.iterrows():
        # Map full team names to abbreviations (FIX FOR THE BUG!)
        away_abbrev = map_team_name(game['away_team'])
        home_abbrev = map_team_name(game['home_team'])
        
        # Run prediction with abbreviated names
        prediction = predictor.predict_game(
            away_team=away_abbrev,
            home_team=home_abbrev,
            minimum_total=game['minimum_total'],
            game_date=datetime.now().strftime('%Y-%m-%d')
        )
        
        # Make decision
        decision = decider.make_decision(prediction)
        
        # Combine for output
        game_decision = {
            'game': f"{game['away_team']} @ {game['home_team']}",
            'game_time': game['game_time'],
            'minimum_total': game['minimum_total'],
            'minimum_odds': game['minimum_odds'],
            'confidence': decision['confidence'],
            'decision': decision['decision'],
            'elite_goalie_flag': decision['elite_goalie_flag'],
            'goalie_warning': decision['goalie_warning'],
            'action': decision['action'],
            'stake': decision['stake'],
            'reasoning': ' | '.join(prediction['reasoning'])
        }
        
        all_decisions.append(game_decision)
        
        # Print summary
        elite_marker = "⚠️ " if decision['elite_goalie_flag'] else "✅ "
        print(f"\n{elite_marker}{game['away_team']} @ {game['home_team']}")
        print(f"   Minimum: Over {game['minimum_total']} at {game['minimum_odds']:+d}")
        print(f"   Confidence: {decision['confidence']}%")
        
        if decision['elite_goalie_flag']:
            print(f"   🔥 ELITE GOALIE: {decision['goalie_warning']}")
        
        print(f"   Decision: {decision['decision']}")
        print(f"   Action: {decision['action']}")
    
    # Step 6: Export results
    print("\n💾 STEP 6: Exporting results...")
    exporter = CSVExporter()
    output_file = exporter.export_decisions(all_decisions)
    
    print(f"✅ Saved to: {output_file}")
    
    # Step 7: Summary
    print("\n" + "=" * 70)
    print("✅ WORKFLOW COMPLETE!")
    print("=" * 70)
    
    yes_count = sum(1 for d in all_decisions if d['decision'] == 'YES')
    elite_yes_count = sum(1 for d in all_decisions if d['decision'] == 'YES' and d['elite_goalie_flag'])
    
    print(f"\n📊 Ready to bet: {yes_count} YES decisions")
    
    if elite_yes_count > 0:
        print(f"   ⚠️  {elite_yes_count} with elite goalie flag (monitor closely)")
    
    print(f"📁 Results saved to: {output_file}")
    
    # Show YES bets
    if yes_count > 0:
        print("\n✅ YES BETS (85%+ confidence):")
        for d in all_decisions:
            if d['decision'] == 'YES':
                print(f"\n{d['game']}")
                print(f"  Minimum: Over {d['minimum_total']} at {d['minimum_odds']:+d}")
                print(f"  Confidence: {d['confidence']}%")
                
                if d['elite_goalie_flag']:
                    print(f"  ⚠️  ELITE GOALIE: {d['goalie_warning']}")
                
                print(f"  Action: {d['action']}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()