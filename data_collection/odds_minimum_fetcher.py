"""
NHL Minimum Alternate Fetcher
==============================
Fetches ONLY the minimum DraftKings alternate total for each game

This is the key line we're betting: the safest over (lowest total)
"""

import requests
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.api_config import *
from config.season_config import CURRENT_SEASON


class MinimumAlternateFetcher:
    """Fetches minimum alternate totals from DraftKings for NHL"""
    
    def __init__(self, api_key=ODDS_API_KEY):
        self.api_key = api_key
        self.base_url = BASE_URL
        self.sport = SPORT
        
    def test_api_connection(self):
        """Test API connection and show quota"""
        print("=" * 70)
        print("TESTING ODDS API CONNECTION - NHL")
        print("=" * 70)
        
        try:
            url = f"{self.base_url}/sports/{self.sport}/odds"
            params = {
                'apiKey': self.api_key,
                'regions': REGION,
                'markets': 'totals'
            }
            
            response = requests.get(url, params=params, timeout=API_TIMEOUT)
            
            if response.status_code == 200:
                remaining = response.headers.get('x-requests-remaining', 'Unknown')
                used = response.headers.get('x-requests-used', 'Unknown')
                
                print(f"✅ API Connected!")
                print(f"   Requests remaining: {remaining}")
                print(f"   Requests used: {used}")
                return True
            else:
                print(f"❌ API Error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
            return False
    
    def fetch_upcoming_games(self):
        """
        Fetch today's NHL games
        
        Returns:
            DataFrame with columns:
            - event_id
            - commence_time
            - home_team
            - away_team
        """
        try:
            print("\n" + "=" * 70)
            print("🏒 FETCHING TODAY'S NHL GAMES")
            print("=" * 70)
            
            url = f"{self.base_url}/sports/{self.sport}/odds"
            params = {
                'apiKey': self.api_key,
                'regions': REGION,
                'markets': 'totals',
                'oddsFormat': ODDS_FORMAT
            }
            
            response = requests.get(url, params=params, timeout=API_TIMEOUT)
            
            if response.status_code != 200:
                print(f"❌ Failed to fetch games: {response.status_code}")
                return None
            
            data = response.json()
            
            if not data:
                print("⚠️  No games found for today")
                return None
            
            # Parse games
            game_list = []
            et_tz = ZoneInfo("America/New_York")
            
            for game in data:
                commence_time = datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00'))
                commence_time_et = commence_time.astimezone(et_tz)
                
                game_list.append({
                    'event_id': game['id'],
                    'commence_time': commence_time_et,
                    'home_team': game['home_team'],
                    'away_team': game['away_team']
                })
            
            df = pd.DataFrame(game_list)
            df = df.sort_values('commence_time')
            
            print("🏒 UPCOMING GAMES:")
            for _, game in df.iterrows():
                time_str = game['commence_time'].strftime('%a %m/%d %I:%M%p ET')
                print(f"  {time_str} | {game['away_team']} @ {game['home_team']}")
            
            return df
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None
    
    def fetch_minimum_alternate(self, event_id, game_info):
        """
        Fetch minimum alternate total for a specific game
        
        CRITICAL: We only want the MINIMUM over line (safest bet)
        """
        try:
            url = f"{self.base_url}/sports/{self.sport}/events/{event_id}/odds"
            params = {
                'apiKey': self.api_key,
                'regions': REGION,
                'markets': 'alternate_totals',
                'oddsFormat': ODDS_FORMAT
            }
            
            response = requests.get(url, params=params, timeout=API_TIMEOUT)
            
            if response.status_code != 200:
                print(f"  ❌ Failed for {game_info['away_team']} @ {game_info['home_team']}")
                return None
            
            data = response.json()
            
            if 'bookmakers' not in data or len(data['bookmakers']) == 0:
                print(f"  ⚠️  No alternate lines available yet")
                return None
            
            # Find DraftKings alternate totals
            dk_alternates = None
            for bookmaker in data['bookmakers']:
                if bookmaker['title'] == 'DraftKings':
                    for market in bookmaker['markets']:
                        if market['key'] == 'alternate_totals':
                            dk_alternates = market
                            break
                    break
            
            if not dk_alternates:
                print(f"  ⚠️  No DraftKings alternates found")
                return None
            
            # Find MINIMUM over line (lowest total)
            over_lines = []
            for outcome in dk_alternates['outcomes']:
                if outcome['name'] == 'Over':
                    over_lines.append({
                        'line': outcome['point'],
                        'odds': outcome['price']
                    })
            
            if not over_lines:
                print(f"  ⚠️  No over lines found")
                return None
            
            # Get the MINIMUM (lowest total = safest over bet)
            minimum_over = min(over_lines, key=lambda x: x['line'])
            
            print(f"  ✅ {game_info['away_team']} @ {game_info['home_team']}")
            print(f"    Minimum: Over {minimum_over['line']} at {minimum_over['odds']:+d}")
            
            return {
                'event_id': event_id,
                'game_time': game_info['commence_time'],
                'away_team': game_info['away_team'],
                'home_team': game_info['home_team'],
                'minimum_total': minimum_over['line'],
                'minimum_odds': minimum_over['odds'],
                'bookmaker': 'DraftKings'
            }
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return None
    
    def fetch_all_minimums(self, games_df):
        """Fetch minimum alternates for all games"""
        print("\n" + "=" * 70)
        print("🎯 FETCHING MINIMUM ALTERNATE TOTALS")
        print("=" * 70)
        
        results = []
        
        for _, game in games_df.iterrows():
            result = self.fetch_minimum_alternate(game['event_id'], game)
            
            if result:
                results.append(result)
            
            # Rate limiting
            time.sleep(REQUESTS_PER_SECOND)
        
        if not results:
            print("\n⚠️  No minimum alternates found")
            return None
        
        df = pd.DataFrame(results)
        
        # Save to data folder
        os.makedirs('data', exist_ok=True)
        df.to_csv('data/upcoming_games.csv', index=False)
        
        print(f"\n✅ Found {len(df)} games with minimum alternates")
        print(f"   Saved to data/upcoming_games.csv")
        
        return df


def main():
    """Test the minimum alternate fetcher"""
    fetcher = MinimumAlternateFetcher()
    
    # Test connection
    if not fetcher.test_api_connection():
        print("\n❌ Cannot proceed without API connection")
        return
    
    # Fetch today's games
    games_df = fetcher.fetch_upcoming_games()
    
    if games_df is None:
        print("\n⚠️  No games today")
        return
    
    # Fetch minimum alternates
    minimums_df = fetcher.fetch_all_minimums(games_df)
    
    if minimums_df is not None:
        print("\n" + "=" * 70)
        print("📊 MINIMUM ALTERNATES SUMMARY")
        print("=" * 70)
        print(minimums_df[['away_team', 'home_team', 'minimum_total', 'minimum_odds']].to_string(index=False))
        print("\n✅ Fetch complete!")


if __name__ == "__main__":
    main()
