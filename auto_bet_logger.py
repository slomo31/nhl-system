"""
Auto Bet Logger
===============
Automatically logs your YES picks for tracking
Run this after master_workflow.py to log today's bets
"""

import pandas as pd
import os
from datetime import datetime

def log_todays_picks():
    """Log today's YES picks from the most recent workflow run"""
    
    # Find most recent decision file
    decision_dir = 'output_archive/decisions'
    files = [f for f in os.listdir(decision_dir) if f.endswith('_decisions.csv')]
    
    if not files:
        print("❌ No decision files found. Run master_workflow.py first!")
        return
    
    latest_file = max([os.path.join(decision_dir, f) for f in files], key=os.path.getmtime)
    
    # Load decisions
    decisions = pd.read_csv(latest_file)
    yes_picks = decisions[decisions['decision'] == 'YES']
    
    if len(yes_picks) == 0:
        print("⚠️  No YES picks today!")
        return
    
    print("\n" + "=" * 80)
    print("📝 LOGGING TODAY'S PICKS")
    print("=" * 80)
    
    # Load or create results file
    results_file = 'data/betting_results.csv'
    
    if os.path.exists(results_file):
        results = pd.read_csv(results_file)
    else:
        results = pd.DataFrame(columns=[
            'date', 'game', 'bet_type', 'legs', 'minimum_total', 'odds',
            'confidence', 'elite_goalie', 'stake', 'result', 'actual_total',
            'profit_loss', 'notes'
        ])
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Check if already logged today
    if len(results[results['date'] == today]) > 0:
        print(f"⚠️  Bets already logged for {today}")
        overwrite = input("Overwrite? (y/n): ").strip().lower()
        if overwrite != 'y':
            return
        results = results[results['date'] != today]
    
    # Log each pick
    new_bets = []
    
    print(f"\n🎯 {len(yes_picks)} YES picks found:")
    for _, pick in yes_picks.iterrows():
        print(f"\n   {pick['game']}")
        print(f"   Minimum: Over {pick['minimum_total']} at {pick['minimum_odds']:+d}")
        print(f"   Confidence: {pick['confidence']}%")
        
        elite = "🔥 Elite goalie flagged" if pick['elite_goalie_flag'] else ""
        if elite:
            print(f"   {elite}")
    
    # Ask for bet type
    print("\n" + "=" * 80)
    print("How are you betting these?")
    print("  1. Single bets")
    print("  2. One 2-leg parlay")
    print("  3. One 3-leg parlay")
    print("  4. One 4-leg parlay")
    print("  5. Multiple parlays (custom)")
    print("  6. Skip logging")
    
    choice = input("\nChoice (1-6): ").strip()
    
    if choice == '6':
        print("Skipped logging.")
        return
    
    # Get stake
    default_stake = 30.0  # $30 default
    stake_input = input(f"\nStake per bet (default ${default_stake}): ").strip()
    stake = float(stake_input) if stake_input else default_stake
    
    # Log based on choice
    if choice == '1':
        # Single bets
        for _, pick in yes_picks.iterrows():
            new_bets.append({
                'date': today,
                'game': pick['game'],
                'bet_type': 'single',
                'legs': pick['game'],
                'minimum_total': pick['minimum_total'],
                'odds': pick['minimum_odds'],
                'confidence': pick['confidence'],
                'elite_goalie': pick['elite_goalie_flag'],
                'stake': stake,
                'result': 'pending',
                'actual_total': None,
                'profit_loss': None,
                'notes': ''
            })
    
    elif choice in ['2', '3', '4']:
        # Parlay
        parlay_size = int(choice)
        games_list = yes_picks['game'].tolist()[:parlay_size]
        
        # Calculate parlay odds (rough estimate)
        parlay_odds = -200 if parlay_size == 2 else (+150 if parlay_size == 3 else +300)
        
        new_bets.append({
            'date': today,
            'game': f"{parlay_size}-leg parlay",
            'bet_type': f'{parlay_size}-leg',
            'legs': ' | '.join(games_list),
            'minimum_total': yes_picks['minimum_total'].iloc[0],
            'odds': parlay_odds,
            'confidence': yes_picks['confidence'].mean(),
            'elite_goalie': yes_picks['elite_goalie_flag'].any(),
            'stake': stake,
            'result': 'pending',
            'actual_total': None,
            'profit_loss': None,
            'notes': ''
        })
    
    # Save
    if new_bets:
        new_df = pd.DataFrame(new_bets)
        results = pd.concat([results, new_df], ignore_index=True)
        results.to_csv(results_file, index=False)
        
        print(f"\n✅ Logged {len(new_bets)} bet(s) to {results_file}")
        print(f"   Total at risk: ${sum([b['stake'] for b in new_bets]):.2f}")


def update_results():
    """Update results with actual game outcomes"""
    
    results_file = 'data/betting_results.csv'
    
    if not os.path.exists(results_file):
        print("❌ No results file found!")
        return
    
    results = pd.read_csv(results_file)
    pending = results[results['result'] == 'pending']
    
    if len(pending) == 0:
        print("✅ No pending bets to update!")
        return
    
    print("\n" + "=" * 80)
    print("📊 UPDATE PENDING RESULTS")
    print("=" * 80)
    
    print(f"\n{len(pending)} pending bets:")
    for idx, bet in pending.iterrows():
        print(f"\n{idx}. {bet['date']} | {bet['game']}")
        print(f"   Bet: Over {bet['minimum_total']} | Stake: ${bet['stake']}")
    
    update_all = input("\nUpdate all? (y/n): ").strip().lower()
    
    if update_all == 'y':
        for idx, bet in pending.iterrows():
            print(f"\n{bet['game']}:")
            actual = input(f"  Actual total goals (or 'skip'): ").strip()
            
            if actual.lower() == 'skip':
                continue
            
            actual_total = float(actual)
            result = 'won' if actual_total > bet['minimum_total'] else 'lost'
            
            # Calculate profit/loss
            if result == 'won':
                if bet['odds'] < 0:
                    profit = bet['stake'] * (100 / abs(bet['odds']))
                else:
                    profit = bet['stake'] * (bet['odds'] / 100)
            else:
                profit = -bet['stake']
            
            results.loc[idx, 'actual_total'] = actual_total
            results.loc[idx, 'result'] = result
            results.loc[idx, 'profit_loss'] = profit
            
            print(f"  ✅ {result.upper()} | ${profit:+.2f}")
        
        results.to_csv(results_file, index=False)
        print(f"\n✅ Updated results saved!")


def show_performance():
    """Show current performance stats"""
    
    results_file = 'data/betting_results.csv'
    
    if not os.path.exists(results_file):
        print("❌ No results file found!")
        return
    
    results = pd.read_csv(results_file)
    completed = results[results['result'].isin(['won', 'lost'])]
    
    if len(completed) == 0:
        print("⚠️  No completed bets yet!")
        return
    
    print("\n" + "=" * 80)
    print("📊 SYSTEM PERFORMANCE")
    print("=" * 80)
    
    wins = len(completed[completed['result'] == 'won'])
    losses = len(completed[completed['result'] == 'lost'])
    win_rate = (wins / len(completed) * 100)
    
    total_staked = completed['stake'].sum()
    total_profit = completed['profit_loss'].sum()
    roi = (total_profit / total_staked * 100)
    
    print(f"\n📈 Overall Record:")
    print(f"   Total bets: {len(completed)}")
    print(f"   Record: {wins}-{losses}")
    print(f"   Win rate: {win_rate:.1f}%")
    print(f"   Total staked: ${total_staked:.2f}")
    print(f"   Total profit: ${total_profit:+.2f}")
    print(f"   ROI: {roi:+.1f}%")
    
    # Last 10
    print(f"\n📅 Last 10 Bets:")
    recent = completed.tail(10)
    for _, bet in recent.iterrows():
        icon = "✅" if bet['result'] == 'won' else "❌"
        print(f"   {icon} {bet['date']} | {bet['game']:<35} | ${bet['profit_loss']:+7.2f}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'log':
            log_todays_picks()
        elif sys.argv[1] == 'update':
            update_results()
        elif sys.argv[1] == 'stats':
            show_performance()
    else:
        print("\n" + "=" * 80)
        print("📊 NHL BET TRACKER")
        print("=" * 80)
        print("\nCommands:")
        print("  python auto_bet_logger.py log      - Log today's picks")
        print("  python auto_bet_logger.py update   - Update results")
        print("  python auto_bet_logger.py stats    - Show performance")
        print("\n" + "=" * 80)
