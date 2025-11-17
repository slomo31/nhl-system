"""
NHL Season Backtester - REAL RESULTS
=====================================
Test the system against ALL completed 2024-2025 games
Shows exactly what would have happened
"""

import pandas as pd
import sys
from datetime import datetime

sys.path.append('core')
sys.path.append('decision')
sys.path.append('config')

from minimum_total_predictor import MinimumTotalPredictor
from yes_no_decider import YesNoDecider
import season_config

print("\n" + "=" * 80)
print("🏒 NHL SEASON BACKTEST - 2024-2025")
print("=" * 80)
print(f"Current YES threshold: {season_config.CONFIDENCE_THRESHOLD_YES}%")
print(f"Testing all completed games with minimum = 3.5 goals")
print("=" * 80)

# Load data
print("\n📊 Loading data...")
team_stats = pd.read_csv('data/nhl_team_stats_2024_2025.csv')
completed_games = pd.read_csv('data/nhl_completed_games_2024_2025.csv')
goalie_stats = pd.read_csv('data/nhl_goalie_stats_2024_2025.csv')

print(f"✅ {len(completed_games)} completed games loaded")

# Initialize predictor
predictor = MinimumTotalPredictor(team_stats, completed_games, goalie_stats)
decider = YesNoDecider()

# Backtest parameters
MINIMUM_TOTAL = 3.5  # Standard minimum alternate

# Results storage
all_results = []
yes_bets = []
no_skips = []

print("\n🔄 Running backtest (this may take a minute)...")

for idx, game in completed_games.iterrows():
    try:
        # Get prediction
        prediction = predictor.predict_game(
            away_team=game['Away_Team'],
            home_team=game['Home_Team'],
            minimum_total=MINIMUM_TOTAL,
            game_date=game['Date']
        )
        
        # Get decision
        decision = decider.make_decision(prediction)
        
        # Actual result
        actual_total = game['Total_Goals']
        hit = actual_total > MINIMUM_TOTAL
        
        result = {
            'date': game['Date'],
            'away_team': game['Away_Team'],
            'home_team': game['Home_Team'],
            'away_goals': game['Away_Goals'],
            'home_goals': game['Home_Goals'],
            'total_goals': actual_total,
            'minimum': MINIMUM_TOTAL,
            'hit': hit,
            'confidence': decision['confidence'],
            'decision': decision['decision'],
            'elite_goalie': prediction['elite_goalie_flag']
        }
        
        all_results.append(result)
        
        # Categorize
        if decision['decision'] == 'YES':
            yes_bets.append(result)
        else:
            no_skips.append(result)
            
    except Exception as e:
        continue
    
    # Progress indicator
    if (idx + 1) % 200 == 0:
        print(f"  Processed {idx + 1}/{len(completed_games)} games...")

print(f"\n✅ Backtest complete! Analyzed {len(all_results)} games")

# Convert to DataFrames
results_df = pd.DataFrame(all_results)
yes_df = pd.DataFrame(yes_bets) if yes_bets else pd.DataFrame()
no_df = pd.DataFrame(no_skips) if no_skips else pd.DataFrame()

# Save full results
results_df.to_csv('output_archive/backtests/season_backtest_3.5_minimum.csv', index=False)

# ============================================================================
# ANALYSIS
# ============================================================================

print("\n" + "=" * 80)
print("📊 BACKTEST RESULTS - MINIMUM 3.5 GOALS")
print("=" * 80)

# Overall stats
total_games = len(results_df)
total_hit = results_df['hit'].sum()
overall_hit_rate = (total_hit / total_games * 100) if total_games > 0 else 0

print(f"\n📈 Overall Market Stats:")
print(f"   Total games: {total_games}")
print(f"   Games over 3.5: {total_hit} ({overall_hit_rate:.1f}%)")
print(f"   Games under 3.5: {total_games - total_hit} ({100 - overall_hit_rate:.1f}%)")

# YES bets analysis
print("\n" + "=" * 80)
print("✅ YES BETS (System said BET IT)")
print("=" * 80)

if len(yes_df) > 0:
    yes_count = len(yes_df)
    yes_won = yes_df['hit'].sum()
    yes_lost = yes_count - yes_won
    yes_win_rate = (yes_won / yes_count * 100) if yes_count > 0 else 0
    
    print(f"\nTotal YES predictions: {yes_count}")
    print(f"  ✅ Won: {yes_won} ({yes_win_rate:.1f}%)")
    print(f"  ❌ Lost: {yes_lost} ({100 - yes_win_rate:.1f}%)")
    
    # With elite goalie
    yes_elite = yes_df[yes_df['elite_goalie'] == True]
    if len(yes_elite) > 0:
        elite_won = yes_elite['hit'].sum()
        elite_rate = (elite_won / len(yes_elite) * 100)
        print(f"\n  🔥 With elite goalie flag: {len(yes_elite)} bets")
        print(f"     Won: {elite_won}/{len(yes_elite)} ({elite_rate:.1f}%)")
    
    # Confidence breakdown
    print(f"\n  📊 Confidence breakdown:")
    for threshold in [70, 75, 80, 85, 90]:
        subset = yes_df[yes_df['confidence'] >= threshold]
        if len(subset) > 0:
            won = subset['hit'].sum()
            rate = (won / len(subset) * 100)
            print(f"     {threshold}%+: {won}/{len(subset)} won ({rate:.1f}%)")
    
    # Show some examples
    print(f"\n  📝 Sample YES bets that WON:")
    winners = yes_df[yes_df['hit'] == True].head(5)
    for _, w in winners.iterrows():
        print(f"     {w['date']} | {w['away_team']} @ {w['home_team']}: {w['total_goals']} goals ({w['confidence']}% conf)")
    
    print(f"\n  📝 Sample YES bets that LOST:")
    losers = yes_df[yes_df['hit'] == False].head(5)
    for _, l in losers.iterrows():
        elite = "🔥" if l['elite_goalie'] else ""
        print(f"     {l['date']} | {l['away_team']} @ {l['home_team']}: {l['total_goals']} goals ({l['confidence']}% conf) {elite}")

else:
    print("\n❌ NO YES BETS FOUND")
    print("   The current threshold is too high!")
    print("   Lower the threshold to get some YES predictions")

# NO bets analysis
print("\n" + "=" * 80)
print("❌ NO/MAYBE DECISIONS (System said SKIP)")
print("=" * 80)

if len(no_df) > 0:
    no_count = len(no_df)
    no_would_have_won = no_df['hit'].sum()
    no_win_rate = (no_would_have_won / no_count * 100) if no_count > 0 else 0
    
    print(f"\nTotal NO/MAYBE predictions: {no_count}")
    print(f"  Games that went OVER 3.5: {no_would_have_won} ({no_win_rate:.1f}%)")
    print(f"  Games that stayed UNDER: {no_count - no_would_have_won} ({100 - no_win_rate:.1f}%)")
    print(f"\n  💡 Missed opportunities: {no_would_have_won} games")
    
    # High confidence NOs that still hit
    high_conf_nos = no_df[(no_df['confidence'] >= 60) & (no_df['hit'] == True)]
    if len(high_conf_nos) > 0:
        print(f"\n  ⚠️  Games with 60%+ confidence that STILL went over:")
        print(f"     Count: {len(high_conf_nos)}")
        for _, g in high_conf_nos.head(10).iterrows():
            print(f"     {g['date']} | {g['away_team']} @ {g['home_team']}: {g['total_goals']} goals ({g['confidence']}% conf)")

print("\n" + "=" * 80)
print("🎯 PROFITABILITY ANALYSIS")
print("=" * 80)

# Calculate EV at different odds
typical_odds = [-1000, -800, -600, -500, -400]

if len(yes_df) > 0:
    yes_win_rate = yes_df['hit'].sum() / len(yes_df)
    
    print(f"\nYES bet win rate: {yes_win_rate:.1%}")
    print(f"\nProfitability at typical 3.5 minimum odds:")
    
    for odds in typical_odds:
        if odds < 0:
            decimal = 1 + (100 / abs(odds))
        else:
            decimal = 1 + (odds / 100)
        
        breakeven = 1 / decimal
        
        # Calculate EV per $100 bet
        win_profit = 100 * (decimal - 1)
        ev = (yes_win_rate * win_profit) + ((1 - yes_win_rate) * -100)
        
        status = "✅ +EV" if ev > 0 else "❌ -EV"
        print(f"  {odds:>6d} odds: Breakeven {breakeven:.1%} | EV: ${ev:>6.2f} per $100 {status}")

print("\n" + "=" * 80)
print("💡 RECOMMENDATIONS")
print("=" * 80)

if len(yes_df) > 0:
    yes_win_rate = yes_df['hit'].sum() / len(yes_df)
    
    if yes_win_rate >= 0.85:
        print("\n✅ SYSTEM IS GOOD!")
        print(f"   Win rate: {yes_win_rate:.1%}")
        print(f"   Recommendation: Lower threshold to get more YES bets")
        print(f"   Profitable at odds better than -600")
    elif yes_win_rate >= 0.75:
        print("\n⚠️  SYSTEM IS DECENT")
        print(f"   Win rate: {yes_win_rate:.1%}")
        print(f"   Recommendation: Need odds better than -400 to profit")
        print(f"   Consider looking at 4.5 minimums with better odds")
    else:
        print("\n❌ SYSTEM NEEDS WORK")
        print(f"   Win rate: {yes_win_rate:.1%}")
        print(f"   Recommendation: Adjust factors or thresholds")
else:
    print("\n⚠️  NO DATA - THRESHOLD TOO HIGH")
    print(f"   Current threshold: {season_config.CONFIDENCE_THRESHOLD_YES}%")
    print(f"   Recommendation: Lower to 60-70 to see results")

print("\n📁 Full results saved to:")
print("   output_archive/backtests/season_backtest_3.5_minimum.csv")

print("\n" + "=" * 80)
