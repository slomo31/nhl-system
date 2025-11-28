"""
NHL MINIMUM SYSTEM - MASTER WORKFLOW V3.1
==========================================
Uses Monte Carlo simulation with cumulative flag penalty.

Same methodology that achieved:
- CBB: 14-0 (100%) on YES picks
- NBA: 66-0 (100%) on YES picks

Usage:
    python master_workflow_v31.py
"""

import pandas as pd
import sys
import os
from datetime import datetime

# Import all components
from data_collection.nhl_stats_collector import NHLStatsCollector
from data_collection.goalie_stats_collector import GoalieStatsCollector
from data_collection.game_results_collector import GameResultsCollector
from data_collection.odds_minimum_fetcher import MinimumAlternateFetcher
from nhl_monte_carlo_v31 import NHLMonteCarloPredictor
from output.csv_exporter import CSVExporter


def main():
    """Run complete daily workflow with V3.1 Monte Carlo system."""
    
    print("\n" + "=" * 70)
    print("🏒 NHL MINIMUM TOTAL SYSTEM - V3.1 MONTE CARLO")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Using: 10,000 simulations + Risk Flag Penalty System")
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
        print(f"   Avg GPG: {team_stats['GPG'].mean():.2f}")
    
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
        elite_count = goalie_stats['Is_Elite_Hot'].sum() if 'Is_Elite_Hot' in goalie_stats.columns else 0
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
    
    # Step 5: Run V3.1 Monte Carlo predictions
    print("\n🎲 STEP 5: Running V3.1 Monte Carlo predictions...")
    print("   Simulations: 10,000 per game")
    print("   Risk flags: 9 categories")
    print("   Decision: Cumulative flag penalty")
    print()
    
    predictor = NHLMonteCarloPredictor(team_stats, completed_games, goalie_stats)
    
    all_decisions = []
    yes_picks = []
    maybe_picks = []
    no_picks = []
    
    for _, game in minimums_df.iterrows():
        # Run V3.1 prediction
        result = predictor.predict_game(
            away_team=game['away_team'],
            home_team=game['home_team'],
            minimum_total=game['minimum_total'],
            game_date=datetime.now().strftime('%Y-%m-%d')
        )
        
        # Print formatted prediction
        print(predictor.format_prediction(result))
        
        # Combine for output
        game_decision = {
            'game': f"{game['away_team']} @ {game['home_team']}",
            'game_time': game['game_time'],
            'minimum_total': game['minimum_total'],
            'minimum_odds': game['minimum_odds'],
            
            # V3.1 fields
            'decision': result['decision'],
            'hit_rate': result['hit_rate'],
            'flag_count': result['flag_count'],
            'flags': ' | '.join(result['flags']) if result['flags'] else 'None',
            'floor_10th': result['floor_10th'],
            'floor_safe': result['floor_safe'],
            
            # Legacy fields
            'confidence': result['hit_rate'],
            'elite_goalie_flag': result['home_goalie_elite'] or result['away_goalie_elite'],
            'goalie_warning': f"{result['home_goalie']} / {result['away_goalie']}",
            'reasoning': result['reasoning'],
            
            # Stats
            'expected_total': result['expected_total'],
            'combined_gpg': result['combined_gpg'],
            'buffer': result['buffer']
        }
        
        all_decisions.append(game_decision)
        
        # Track by decision type
        if result['decision'] == 'YES':
            yes_picks.append(game_decision)
        elif result['decision'] == 'MAYBE':
            maybe_picks.append(game_decision)
        else:
            no_picks.append(game_decision)
    
    # Step 6: Export results
    print("\n💾 STEP 6: Exporting results...")
    exporter = CSVExporter()
    output_file = exporter.export_decisions(all_decisions)
    
    print(f"✅ Saved to: {output_file}")
    
    # Step 7: Summary
    print("\n" + "=" * 70)
    print("✅ V3.1 WORKFLOW COMPLETE!")
    print("=" * 70)
    
    print(f"\n📊 SUMMARY")
    print(f"   Total games analyzed: {len(all_decisions)}")
    print(f"   ✅ YES picks: {len(yes_picks)}")
    print(f"   ⚠️  MAYBE picks: {len(maybe_picks)}")
    print(f"   ❌ NO picks: {len(no_picks)}")
    
    # Show YES bets
    if yes_picks:
        print(f"\n" + "=" * 70)
        print("✅ YES BETS - PASSED V3.1 VALIDATION")
        print("=" * 70)
        
        for pick in yes_picks:
            print(f"\n{pick['game']}")
            print(f"   Minimum: Over {pick['minimum_total']} at {pick['minimum_odds']:+d}")
            print(f"   Hit Rate: {pick['hit_rate']:.1f}%")
            print(f"   Risk Flags: {pick['flag_count']}")
            print(f"   Floor (10th %): {pick['floor_10th']:.1f}")
            print(f"   Buffer: {pick['buffer']:.2f} goals")
            print(f"   💰 BET IT")
    else:
        print(f"\n⚠️  No YES picks today - all games have too many risk flags")
    
    # Show MAYBE bets
    if maybe_picks:
        print(f"\n" + "=" * 70)
        print("⚠️  MAYBE BETS - PROCEED WITH CAUTION")
        print("=" * 70)
        
        for pick in maybe_picks:
            print(f"\n{pick['game']}")
            print(f"   Minimum: Over {pick['minimum_total']}")
            print(f"   Hit Rate: {pick['hit_rate']:.1f}%")
            print(f"   Risk Flags: {pick['flag_count']}")
            print(f"   Flags: {pick['flags']}")
            print(f"   ⚠️  REVIEW MANUALLY")
    
    print(f"\n📁 Results saved to: {output_file}")
    print("=" * 70)
    
    # Show V3.1 methodology
    print("\n📋 V3.1 METHODOLOGY USED:")
    print("   • 10,000 Monte Carlo simulations per game")
    print("   • Bad night scenarios (hot goalie, cold shooting)")
    print("   • 9 risk flag categories checked")
    print("   • Cumulative flag penalty:")
    print("     - 0 flags: 88%+ = YES")
    print("     - 1 flag:  93%+ = YES")
    print("     - 2 flags: 96%+ = YES")
    print("     - 3+ flags: AUTO-MAYBE")
    print("   • Floor safety: 10th percentile must beat minimum")
    print("=" * 70)


if __name__ == "__main__":
    main()
