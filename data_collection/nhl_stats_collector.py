"""
NHL Team Stats Collector (Hockey-Reference Version 2)
=====================================================
Collects from standings tables (East + West conferences)
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.season_config import CURRENT_SEASON


class NHLStatsCollector:
    """Collects team statistics from Hockey-Reference"""
    
    def __init__(self):
        self.base_url = "https://www.hockey-reference.com"
        self.season = "2025"  # Hockey-Reference uses end year
        
    def collect_team_stats(self):
        """
        Collect current season team stats from both conferences
        """
        print("\n" + "=" * 70)
        print("🏒 NHL TEAM STATS COLLECTOR")
        print("=" * 70)
        print()
        
        try:
            # Hockey-Reference league page
            url = f"{self.base_url}/leagues/NHL_{self.season}.html"
            
            print(f"Fetching from: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                print(f"❌ Failed to fetch data: Status {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            all_teams = []
            
            # Get Eastern Conference
            print("\n📊 Collecting Eastern Conference...")
            east_teams = self._parse_conference_table(soup, 'standings_EAS')
            if east_teams:
                all_teams.extend(east_teams)
                print(f"   ✅ Found {len(east_teams)} Eastern teams")
            
            # Get Western Conference
            print("\n📊 Collecting Western Conference...")
            west_teams = self._parse_conference_table(soup, 'standings_WES')
            if west_teams:
                all_teams.extend(west_teams)
                print(f"   ✅ Found {len(west_teams)} Western teams")
            
            if not all_teams:
                print("\n❌ No team data collected")
                return None
            
            # Create DataFrame
            df = pd.DataFrame(all_teams)
            
            # Save to CSV
            os.makedirs('data', exist_ok=True)
            output_file = f'data/nhl_team_stats_{CURRENT_SEASON}.csv'
            df.to_csv(output_file, index=False)
            
            print(f"\n✅ Saved {len(df)} teams to {output_file}")
            print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            return df
            
        except Exception as e:
            print(f"❌ Error collecting team stats: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _parse_conference_table(self, soup, table_id):
        """Parse a conference standings table"""
        teams_data = []
        
        table = soup.find('table', {'id': table_id})
        
        if not table:
            print(f"   ⚠️  Could not find table: {table_id}")
            return teams_data
        
        tbody = table.find('tbody')
        
        for row in tbody.find_all('tr'):
            # Skip division headers
            if 'thead' in row.get('class', []):
                continue
            
            team_cell = row.find('th', {'data-stat': 'team_name'})
            if not team_cell:
                continue
            
            # Get team link to extract abbreviation
            team_link = team_cell.find('a')
            if not team_link:
                continue
            
            team_name = team_link.text.strip()
            
            # Extract team abbreviation from URL
            # URL format: /teams/TOR/2025.html
            href = team_link.get('href', '')
            team_abbrev = href.split('/')[2] if len(href.split('/')) > 2 else team_name[:3].upper()
            
            # Extract stats
            try:
                gp = int(row.find('td', {'data-stat': 'games'}).text)
                wins = int(row.find('td', {'data-stat': 'wins'}).text)
                losses = int(row.find('td', {'data-stat': 'losses'}).text)
                
                goals_for = int(row.find('td', {'data-stat': 'goals'}).text)
                goals_against = int(row.find('td', {'data-stat': 'opp_goals'}).text)
                
                # Calculate per-game stats
                gpg = goals_for / gp if gp > 0 else 0
                gapg = goals_against / gp if gp > 0 else 0
                
                # Estimate shots (not in standings table)
                # NHL average is ~10 shots per goal
                # We'll use league averages as placeholder
                spg = gpg * 10  # Rough estimate
                sapg = gapg * 10  # Rough estimate
                
                teams_data.append({
                    'Team': team_abbrev,
                    'Full_Name': team_name,
                    'GP': gp,
                    'GPG': gpg,
                    'GAPG': gapg,
                    'SPG': spg,  # Estimated
                    'SAPG': sapg,  # Estimated
                    'PP_PCT': 20.0,  # League average placeholder
                    'PK_PCT': 80.0   # League average placeholder
                })
                
                print(f"   ✅ {team_abbrev:<4} {team_name:<25} {gpg:.2f} GPG | {wins}-{losses}")
                
            except Exception as e:
                print(f"   ⚠️  Error parsing {team_name}: {e}")
                continue
        
        return teams_data


def main():
    """Run the team stats collector"""
    collector = NHLStatsCollector()
    df = collector.collect_team_stats()
    
    if df is not None:
        print("\n" + "=" * 70)
        print("📊 TOP 10 TEAMS BY GOALS/GAME")
        print("=" * 70)
        top_10 = df.nlargest(10, 'GPG')[['Team', 'Full_Name', 'GP', 'GPG']]
        print(top_10.to_string(index=False))
        print("\n✅ Collection complete!")
        print("\nNOTE: SPG, PP_PCT, PK_PCT are estimates from standings.")
        print("      System will still work - these are secondary factors.")
    else:
        print("\n❌ Collection failed")


if __name__ == "__main__":
    main()