"""
NHL Game Results Collector
===========================
Collects completed game scores for backtest validation and form analysis
"""

import requests
import pandas as pd
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.api_config import NHL_API_BASE
from config.season_config import CURRENT_SEASON, SEASON_START


class GameResultsCollector:
    """Collects completed NHL game results"""
    
    def __init__(self):
        self.base_url = NHL_API_BASE
        self.season = CURRENT_SEASON
        
    def collect_completed_games(self, start_date=None):
        """
        Collect all completed games from start of season
        
        Returns:
            DataFrame with columns:
            - Date
            - Away_Team
            - Away_Goals
            - Home_Team
            - Home_Goals
            - Total_Goals
        """
        print("\n" + "=" * 70)
        print("🏒 NHL GAME RESULTS COLLECTOR")
        print("=" * 70)
        print()
        
        if start_date is None:
            start_date = datetime.strptime(SEASON_START, "%Y-%m-%d")
        else:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        
        today = datetime.now()
        
        print(f"Collecting games from {start_date.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}")
        print()
        
        all_games = []
        current_date = start_date
        
        while current_date <= today:
            date_str = current_date.strftime("%Y-%m-%d")
            games = self._get_games_for_date(date_str)
            
            if games:
                all_games.extend(games)
            
            current_date += timedelta(days=1)
        
        if not all_games:
            print("❌ No completed games found")
            return None
        
        # Create DataFrame
        df = pd.DataFrame(all_games)
        df = df.sort_values('Date')
        
        # Save to CSV
        os.makedirs('data', exist_ok=True)
        output_file = f'data/nhl_completed_games_{self.season}.csv'
        df.to_csv(output_file, index=False)
        
        print(f"\n✅ Saved {len(df)} completed games to {output_file}")
        print(f"   Date range: {df['Date'].min()} to {df['Date'].max()}")
        print(f"   Avg total goals: {df['Total_Goals'].mean():.2f}")
        
        return df
    
    def _get_games_for_date(self, date_str):
        """Get completed games for a specific date"""
        try:
            url = f"{self.base_url}/score/{date_str}"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            games_data = []
            
            for game in data.get('games', []):
                # Only include completed games
                game_state = game.get('gameState', '')
                if game_state not in ['OFF', 'FINAL']:
                    continue
                
                away_team = game.get('awayTeam', {}).get('abbrev', '')
                home_team = game.get('homeTeam', {}).get('abbrev', '')
                away_score = game.get('awayTeam', {}).get('score', 0)
                home_score = game.get('homeTeam', {}).get('score', 0)
                
                if not away_team or not home_team:
                    continue
                
                total_goals = away_score + home_score
                
                games_data.append({
                    'Date': date_str,
                    'Away_Team': away_team,
                    'Away_Goals': away_score,
                    'Home_Team': home_team,
                    'Home_Goals': home_score,
                    'Total_Goals': total_goals
                })
                
                print(f"  ✅ {date_str} | {away_team} {away_score} @ {home_team} {home_score} (Total: {total_goals})")
            
            return games_data
            
        except Exception as e:
            return []


def main():
    """Run the game results collector"""
    collector = GameResultsCollector()
    df = collector.collect_completed_games()
    
    if df is not None:
        print("\n" + "=" * 70)
        print("📊 RECENT GAMES")
        print("=" * 70)
        print(df.tail(20).to_string(index=False))
        print("\n✅ Collection complete!")
    else:
        print("\n❌ Collection failed")


if __name__ == "__main__":
    main()
