"""
NHL V3.1 COMPREHENSIVE BACKTEST
================================
Validates Monte Carlo system against completed games.

Tests the same methodology that achieved:
- CBB: 14-0 (100%) on YES picks
- NBA: 66-0 (100%) on YES picks

Usage:
    python backtest_v31.py
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from nhl_monte_carlo_v31 import NHLMonteCarloPredictor, normalize_team


# Team name mapping for matching odds API to completed games
ODDS_TO_ABBREV = {
    'Anaheim Ducks': 'ANA', 'Arizona Coyotes': 'ARI', 'Boston Bruins': 'BOS',
    'Buffalo Sabres': 'BUF', 'Calgary Flames': 'CGY', 'Carolina Hurricanes': 'CAR',
    'Chicago Blackhawks': 'CHI', 'Colorado Avalanche': 'COL', 'Columbus Blue Jackets': 'CBJ',
    'Dallas Stars': 'DAL', 'Detroit Red Wings': 'DET', 'Edmonton Oilers': 'EDM',
    'Florida Panthers': 'FLA', 'Los Angeles Kings': 'LAK', 'Minnesota Wild': 'MIN',
    'Montreal Canadiens': 'MTL', 'Nashville Predators': 'NSH', 'New Jersey Devils': 'NJD',
    'New York Islanders': 'NYI', 'New York Rangers': 'NYR', 'Ottawa Senators': 'OTT',
    'Philadelphia Flyers': 'PHI', 'Pittsburgh Penguins': 'PIT', 'San Jose Sharks': 'SJS',
    'Seattle Kraken': 'SEA', 'St. Louis Blues': 'STL', 'Tampa Bay Lightning': 'TBL',
    'Toronto Maple Leafs': 'TOR', 'Vancouver Canucks': 'VAN', 'Vegas Golden Knights': 'VGK',
    'Washington Capitals': 'WSH', 'Winnipeg Jets': 'WPG', 'Utah Hockey Club': 'UTA',
}


def load_data():
    """Load all required data files."""
    print("📊 Loading data...")
    
    # Team stats
    team_stats = pd.read_csv('data/nhl_team_stats_2024_2025.csv')
    print(f"   ✅ Team stats: {len(team_stats)} teams")
    
    # Goalie stats
    goalie_stats = pd.read_csv('data/nhl_goalie_stats_2024_2025.csv')
    print(f"   ✅ Goalie stats: {len(goalie_stats)} goalies")
    
    # Completed games
    completed_games = pd.read_csv('data/nhl_completed_games_2024_2025.csv')
    completed_games['Date'] = pd.to_datetime(completed_games['Date'])
    print(f"   ✅ Completed games: {len(completed_games)} games")
    print(f"      Date range: {completed_games['Date'].min()} to {completed_games['Date'].max()}")
    print(f"      Avg total: {completed_games['Total_Goals'].mean():.2f}")
    
    return team_stats, goalie_stats, completed_games


def run_backtest_on_completed_games(team_stats, goalie_stats, completed_games, 
                                     minimum_total=3.5, sample_size=None):
    """
    Run V3.1 backtest on completed games.
    
    Uses assumed minimum total since we don't have historical odds.
    """
    print(f"\n{'='*70}")
    print(f"🎲 V3.1 BACKTEST - Minimum {minimum_total} Goals")
    print(f"{'='*70}")
    
    # Initialize predictor
    predictor = NHLMonteCarloPredictor(team_stats, completed_games, goalie_stats)
    
    # Sample games if requested
    if sample_size:
        games_to_test = completed_games.sample(n=min(sample_size, len(completed_games)))
    else:
        games_to_test = completed_games
    
    results = []
    yes_picks = []
    maybe_picks = []
    no_picks = []
    
    print(f"\nTesting {len(games_to_test)} games...")
    print()
    
    for idx, game in games_to_test.iterrows():
        away_team = game['Away_Team']
        home_team = game['Home_Team']
        actual_total = game['Total_Goals']
        game_date = game['Date']
        
        # Run prediction
        result = predictor.predict_game(
            away_team=away_team,
            home_team=home_team,
            minimum_total=minimum_total,
            game_date=game_date.strftime('%Y-%m-%d') if hasattr(game_date, 'strftime') else str(game_date)
        )
        
        # Determine if bet would have hit
        hit = actual_total > minimum_total
        
        game_result = {
            'date': game_date,
            'game': f"{away_team} @ {home_team}",
            'minimum': minimum_total,
            'actual': actual_total,
            'hit': hit,
            'decision': result['decision'],
            'hit_rate': result['hit_rate'],
            'flag_count': result['flag_count'],
            'flags': result['flags'],
            'floor_10th': result['floor_10th'],
            'buffer': result['buffer']
        }
        
        results.append(game_result)
        
        # Track by decision
        if result['decision'] == 'YES':
            yes_picks.append(game_result)
        elif result['decision'] == 'MAYBE':
            maybe_picks.append(game_result)
        else:
            no_picks.append(game_result)
    
    # Calculate statistics
    print(f"\n{'='*70}")
    print("📊 BACKTEST RESULTS")
    print(f"{'='*70}")
    
    # Overall stats
    total_games = len(results)
    total_hits = sum(1 for r in results if r['hit'])
    overall_rate = total_hits / total_games * 100 if total_games > 0 else 0
    
    print(f"\n📈 OVERALL (All {total_games} games):")
    print(f"   Games above {minimum_total}: {total_hits} ({overall_rate:.1f}%)")
    
    # YES picks performance
    if yes_picks:
        yes_wins = sum(1 for p in yes_picks if p['hit'])
        yes_losses = len(yes_picks) - yes_wins
        yes_rate = yes_wins / len(yes_picks) * 100
        
        print(f"\n✅ YES PICKS ({len(yes_picks)} picks):")
        print(f"   Record: {yes_wins}-{yes_losses} ({yes_rate:.1f}%)")
        
        if yes_losses > 0:
            print(f"\n   ❌ LOSSES (games to analyze):")
            for p in yes_picks:
                if not p['hit']:
                    print(f"      {p['date']} | {p['game']}")
                    print(f"         Actual: {p['actual']} | Hit Rate: {p['hit_rate']:.1f}%")
                    print(f"         Flags: {p['flag_count']} - {p['flags']}")
    else:
        print(f"\n✅ YES PICKS: None (system was too conservative)")
    
    # MAYBE picks performance
    if maybe_picks:
        maybe_wins = sum(1 for p in maybe_picks if p['hit'])
        maybe_rate = maybe_wins / len(maybe_picks) * 100
        
        print(f"\n⚠️  MAYBE PICKS ({len(maybe_picks)} picks):")
        print(f"   Win Rate: {maybe_rate:.1f}%")
    
    # NO picks performance (should be lower hit rate)
    if no_picks:
        no_wins = sum(1 for p in no_picks if p['hit'])
        no_rate = no_wins / len(no_picks) * 100
        
        print(f"\n❌ NO PICKS ({len(no_picks)} picks):")
        print(f"   Would have hit: {no_rate:.1f}%")
        print(f"   (Lower is better - confirms we're avoiding risky games)")
    
    # Flag analysis
    print(f"\n🚩 FLAG ANALYSIS:")
    flag_buckets = {0: [], 1: [], 2: [], 3: []}
    for r in results:
        bucket = min(r['flag_count'], 3)
        flag_buckets[bucket].append(r)
    
    for flags, games in flag_buckets.items():
        if games:
            wins = sum(1 for g in games if g['hit'])
            rate = wins / len(games) * 100
            label = f"{flags}" if flags < 3 else "3+"
            print(f"   {label} flags: {len(games)} games, {rate:.1f}% hit rate")
    
    # Summary
    print(f"\n{'='*70}")
    print("📋 V3.1 VALIDATION SUMMARY")
    print(f"{'='*70}")
    
    if yes_picks:
        yes_wins = sum(1 for p in yes_picks if p['hit'])
        yes_rate = yes_wins / len(yes_picks) * 100
        
        if yes_rate >= 95:
            print(f"\n✅ SYSTEM VALIDATED!")
            print(f"   YES pick win rate: {yes_rate:.1f}% ({yes_wins}/{len(yes_picks)})")
            print(f"   Target: 95%+ ✅")
        elif yes_rate >= 85:
            print(f"\n⚠️  SYSTEM GOOD BUT NOT PERFECT")
            print(f"   YES pick win rate: {yes_rate:.1f}% ({yes_wins}/{len(yes_picks)})")
            print(f"   Target: 95%+ ❌")
            print(f"   Consider tightening thresholds")
        else:
            print(f"\n❌ SYSTEM NEEDS CALIBRATION")
            print(f"   YES pick win rate: {yes_rate:.1f}% ({yes_wins}/{len(yes_picks)})")
            print(f"   Review flag thresholds and hit rate requirements")
    else:
        print(f"\n⚠️  No YES picks generated")
        print(f"   System may be too conservative")
        print(f"   Consider lowering hit rate thresholds")
    
    return {
        'total_games': total_games,
        'yes_picks': len(yes_picks),
        'yes_wins': sum(1 for p in yes_picks if p['hit']) if yes_picks else 0,
        'yes_rate': (sum(1 for p in yes_picks if p['hit']) / len(yes_picks) * 100) if yes_picks else 0,
        'maybe_picks': len(maybe_picks),
        'no_picks': len(no_picks),
        'results': results
    }


def run_minimum_sweep(team_stats, goalie_stats, completed_games):
    """
    Test different minimum totals to find optimal threshold.
    """
    print(f"\n{'='*70}")
    print("📊 MINIMUM TOTAL SWEEP")
    print(f"{'='*70}")
    print("Testing which minimum total the system performs best on...")
    print()
    
    minimums = [3.5, 4.0, 4.5, 5.0, 5.5]
    
    sweep_results = []
    
    for minimum in minimums:
        result = run_backtest_on_completed_games(
            team_stats, goalie_stats, completed_games,
            minimum_total=minimum,
            sample_size=200  # Use subset for sweep
        )
        
        sweep_results.append({
            'minimum': minimum,
            'yes_picks': result['yes_picks'],
            'yes_wins': result['yes_wins'],
            'yes_rate': result['yes_rate']
        })
    
    print(f"\n{'='*70}")
    print("📊 SWEEP SUMMARY")
    print(f"{'='*70}")
    print(f"\n{'Minimum':<10} {'YES Picks':<12} {'Record':<12} {'Win Rate':<10}")
    print("-" * 50)
    
    for r in sweep_results:
        record = f"{r['yes_wins']}-{r['yes_picks'] - r['yes_wins']}"
        print(f"{r['minimum']:<10} {r['yes_picks']:<12} {record:<12} {r['yes_rate']:.1f}%")
    
    return sweep_results


def main():
    """Run comprehensive V3.1 backtest."""
    
    print("\n" + "=" * 70)
    print("🏒 NHL V3.1 MONTE CARLO BACKTEST")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Testing methodology that achieved 100% on CBB and NBA")
    print("=" * 70)
    
    # Load data
    team_stats, goalie_stats, completed_games = load_data()
    
    # Main backtest at 3.5 minimum (standard DraftKings minimum)
    print("\n" + "=" * 70)
    print("🎯 MAIN BACKTEST: Over 3.5 Goals")
    print("=" * 70)
    
    main_result = run_backtest_on_completed_games(
        team_stats, goalie_stats, completed_games,
        minimum_total=3.5,
        sample_size=500  # Test on 500 games
    )
    
    # Optional: Run sweep to find optimal minimum
    # sweep_results = run_minimum_sweep(team_stats, goalie_stats, completed_games)
    
    print("\n" + "=" * 70)
    print("✅ BACKTEST COMPLETE")
    print("=" * 70)
    
    if main_result['yes_rate'] >= 95:
        print("\n🎉 V3.1 SYSTEM VALIDATED!")
        print("   Ready for live betting")
    elif main_result['yes_rate'] >= 85:
        print("\n⚠️  System performing well but not at target")
        print("   Consider adjusting flag thresholds")
    else:
        print("\n❌ System needs calibration")
        print("   Review flag detection and thresholds")
    
    # Save results
    results_df = pd.DataFrame(main_result['results'])
    results_df.to_csv('output_archive/backtest_v31_results.csv', index=False)
    print(f"\n📁 Results saved to: output_archive/backtest_v31_results.csv")


if __name__ == "__main__":
    main()
