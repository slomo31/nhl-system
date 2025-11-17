"""
NHL Results Tracker
===================
Track your bets and system performance over time
"""

import pandas as pd
import os
from datetime import datetime

class ResultsTracker:
    """Track betting results and calculate performance"""
    
    def __init__(self):
        self.results_file = 'data/betting_results.csv'
        self.ensure_results_file()
    
    def ensure_results_file(self):
        """Create results file if it doesn't exist"""
        if not os.path.exists(self.results_file):
            os.makedirs('data', exist_ok=True)
            df = pd.DataFrame(columns=[
                'date',
                'game',
                'bet_type',  # 'single', '2-leg', '3-leg', '4-leg'
                'legs',  # JSON list of games in parlay
                'minimum_total',
                'odds',
                'confidence',
                'elite_goalie',
                'stake',
                'result',  # 'pending', 'won', 'lost', 'push'
                'actual_total',
                'profit_loss',
                'notes'
            ])
            df.to_csv(self.results_file, index=False)
            print(f"✅ Created results tracking file: {self.results_file}")
    
    def add_bet(self, game, bet_type, legs, minimum_total, odds, confidence, 
                elite_goalie, stake, notes=""):
        """Add a new bet to tracking"""
        df = pd.read_csv(self.results_file)
        
        new_bet = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'game': game,
            'bet_type': bet_type,
            'legs': str(legs) if isinstance(legs, list) else game,
            'minimum_total': minimum_total,
            'odds': odds,
            'confidence': confidence,
            'elite_goalie': elite_goalie,
            'stake': stake,
            'result': 'pending',
            'actual_total': None,
            'profit_loss': None,
            'notes': notes
        }
        
        df = pd.concat([df, pd.DataFrame([new_bet])], ignore_index=True)
        df.to_csv(self.results_file, index=False)
        print(f"✅ Logged bet: {game} (${stake})")
    
    def update_result(self, date, game, actual_total, result):
        """Update a bet with actual results"""
        df = pd.read_csv(self.results_file)
        
        mask = (df['date'] == date) & (df['game'] == game)
        
        if mask.any():
            df.loc[mask, 'actual_total'] = actual_total
            df.loc[mask, 'result'] = result
            
            # Calculate profit/loss
            stake = df.loc[mask, 'stake'].values[0]
            odds = df.loc[mask, 'odds'].values[0]
            
            if result == 'won':
                # Convert American odds to profit
                if odds < 0:
                    profit = stake * (100 / abs(odds))
                else:
                    profit = stake * (odds / 100)
                df.loc[mask, 'profit_loss'] = profit
            elif result == 'lost':
                df.loc[mask, 'profit_loss'] = -stake
            else:  # push
                df.loc[mask, 'profit_loss'] = 0
            
            df.to_csv(self.results_file, index=False)
            print(f"✅ Updated: {game} - {result.upper()}")
        else:
            print(f"⚠️  Bet not found: {date} {game}")
    
    def show_stats(self):
        """Display current performance statistics"""
        if not os.path.exists(self.results_file):
            print("❌ No results file found. Place some bets first!")
            return
        
        df = pd.read_csv(self.results_file)
        
        if len(df) == 0:
            print("❌ No bets logged yet!")
            return
        
        print("\n" + "=" * 80)
        print("📊 SYSTEM PERFORMANCE")
        print("=" * 80)
        
        # Overall stats
        completed = df[df['result'].isin(['won', 'lost'])]
        pending = df[df['result'] == 'pending']
        
        if len(completed) > 0:
            wins = len(completed[completed['result'] == 'won'])
            losses = len(completed[completed['result'] == 'lost'])
            win_rate = (wins / len(completed) * 100) if len(completed) > 0 else 0
            
            total_staked = completed['stake'].sum()
            total_profit = completed['profit_loss'].sum()
            roi = (total_profit / total_staked * 100) if total_staked > 0 else 0
            
            print(f"\n📈 Overall Record:")
            print(f"   Total bets: {len(completed)}")
            print(f"   Wins: {wins}")
            print(f"   Losses: {losses}")
            print(f"   Win rate: {win_rate:.1f}%")
            print(f"   Total staked: ${total_staked:.2f}")
            print(f"   Total profit: ${total_profit:+.2f}")
            print(f"   ROI: {roi:+.1f}%")
        
        if len(pending) > 0:
            print(f"\n⏳ Pending bets: {len(pending)}")
            print(f"   Total at risk: ${pending['stake'].sum():.2f}")
        
        # Break down by bet type
        print(f"\n🎯 Performance by Bet Type:")
        for bet_type in df['bet_type'].unique():
            subset = completed[completed['bet_type'] == bet_type]
            if len(subset) > 0:
                wins = len(subset[subset['result'] == 'won'])
                win_rate = (wins / len(subset) * 100)
                profit = subset['profit_loss'].sum()
                print(f"   {bet_type}: {wins}/{len(subset)} ({win_rate:.1f}%) | ${profit:+.2f}")
        
        # Elite goalie impact
        print(f"\n🔥 Elite Goalie Impact:")
        elite_yes = completed[completed['elite_goalie'] == True]
        elite_no = completed[completed['elite_goalie'] == False]
        
        if len(elite_yes) > 0:
            elite_wins = len(elite_yes[elite_yes['result'] == 'won'])
            elite_rate = (elite_wins / len(elite_yes) * 100)
            print(f"   With elite goalie: {elite_wins}/{len(elite_yes)} ({elite_rate:.1f}%)")
        
        if len(elite_no) > 0:
            no_elite_wins = len(elite_no[elite_no['result'] == 'won'])
            no_elite_rate = (no_elite_wins / len(elite_no) * 100)
            print(f"   No elite goalie: {no_elite_wins}/{len(elite_no)} ({no_elite_rate:.1f}%)")
        
        # Recent performance (last 10 bets)
        print(f"\n📅 Last 10 Bets:")
        recent = completed.tail(10)
        for _, bet in recent.iterrows():
            result_icon = "✅" if bet['result'] == 'won' else "❌"
            elite = "🔥" if bet['elite_goalie'] else ""
            print(f"   {result_icon} {bet['date']} | {bet['game']:<40} | {bet['confidence']}% | ${bet['profit_loss']:+6.2f} {elite}")
        
        print("\n" + "=" * 80)


def main():
    """Interactive results tracker"""
    tracker = ResultsTracker()
    
    print("\n" + "=" * 80)
    print("📊 NHL RESULTS TRACKER")
    print("=" * 80)
    
    print("\nOptions:")
    print("  1. View current stats")
    print("  2. Add a bet")
    print("  3. Update bet result")
    print("  4. Export to Excel")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == '1':
        tracker.show_stats()
    
    elif choice == '2':
        print("\n📝 Add a new bet:")
        game = input("Game (e.g., 'WSH @ CAR'): ")
        bet_type = input("Bet type (single/2-leg/3-leg/4-leg): ")
        minimum = float(input("Minimum total (e.g., 3.5): "))
        odds = int(input("Odds (e.g., -825): "))
        confidence = int(input("Confidence % (e.g., 73): "))
        elite = input("Elite goalie? (y/n): ").lower() == 'y'
        stake = float(input("Stake amount ($): "))
        
        tracker.add_bet(game, bet_type, [game], minimum, odds, confidence, elite, stake)
    
    elif choice == '3':
        print("\n✏️  Update bet result:")
        date = input("Date (YYYY-MM-DD): ")
        game = input("Game: ")
        actual = float(input("Actual total goals: "))
        result = input("Result (won/lost/push): ")
        
        tracker.update_result(date, game, actual, result)
    
    elif choice == '4':
        df = pd.read_csv(tracker.results_file)
        output = 'betting_results_export.xlsx'
        df.to_excel(output, index=False)
        print(f"✅ Exported to {output}")


if __name__ == "__main__":
    main()
