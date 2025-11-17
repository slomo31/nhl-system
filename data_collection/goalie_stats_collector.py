"""
NHL Goalie Stats Collector (NHL Stats API - FIXED)
==================================================
Uses correct field names from NHL Stats API
"""

import requests
import pandas as pd
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.season_config import CURRENT_SEASON, ELITE_GOALIE_SAVE_PCT, ELITE_GOALIE_GAA, ELITE_GOALIE_MIN_GAMES


class GoalieStatsCollector:
    """Collects goalie statistics from NHL Stats API"""
    
    def __init__(self):
        self.stats_url = "https://api.nhle.com/stats/rest/en"
        self.season = CURRENT_SEASON
        
    def collect_goalie_stats(self):
        """
        Collect current season goalie stats
        
        Returns:
            DataFrame with elite goalie detection
        """
        print("\n" + "=" * 70)
        print("🥅 NHL GOALIE STATS COLLECTOR")
        print("=" * 70)
        print()
        
        try:
            # NHL Stats API for all goalies (2024-2025 season)
            url = f"{self.stats_url}/goalie/summary?cayenneExp=seasonId=20242025"
            
            print(f"Fetching from NHL Stats API...")
            print(f"URL: {url}\n")
            
            response = requests.get(url, timeout=15)
            
            if response.status_code != 200:
                print(f"❌ API failed: Status {response.status_code}")
                return None
            
            data = response.json()
            
            if 'data' not in data:
                print("❌ No data field in response")
                return None
            
            goalies = data['data']
            print(f"✅ Found {len(goalies)} goalies in API\n")
            
            goalies_data = []
            
            for goalie in goalies:
                try:
                    gp = int(goalie.get('gamesPlayed', 0))
                    
                    # Need minimum games
                    if gp < ELITE_GOALIE_MIN_GAMES:
                        continue
                    
                    # CORRECT FIELD NAMES
                    goalie_name = goalie.get('goalieFullName', '')  # NOT skaterFullName
                    team = goalie.get('teamAbbrevs', '')  # teamAbbrevs for multi-team
                    
                    if not goalie_name:
                        continue
                    
                    # Get stats
                    gaa = float(goalie.get('goalsAgainstAverage', 0))
                    sv_pct = float(goalie.get('savePct', 0))  # This is the key one!
                    wins = int(goalie.get('wins', 0))
                    losses = int(goalie.get('losses', 0))
                    
                    # Use season stats as proxy for last 10
                    last_10_sv_pct = sv_pct
                    last_10_gaa = gaa
                    
                    # Check if elite hot
                    is_elite_hot = (last_10_sv_pct >= ELITE_GOALIE_SAVE_PCT and 
                                   last_10_gaa <= ELITE_GOALIE_GAA and
                                   gaa > 0 and
                                   gp >= ELITE_GOALIE_MIN_GAMES)
                    
                    goalies_data.append({
                        'Goalie': goalie_name,
                        'Team': team,
                        'GP': gp,
                        'GAA': gaa,
                        'SV_PCT': sv_pct,
                        'Wins': wins,
                        'Losses': losses,
                        'Last_10_SV_PCT': last_10_sv_pct,
                        'Last_10_GAA': last_10_gaa,
                        'Is_Elite_Hot': is_elite_hot
                    })
                    
                    # Print with elite flag
                    elite_marker = "🔥" if is_elite_hot else "  "
                    print(f"  {elite_marker} {goalie_name:<25} ({team:<3}) - {sv_pct:.3f} Sv%, {gaa:.2f} GAA, {gp} GP")
                    
                except Exception as e:
                    print(f"  ⚠️  Error parsing goalie: {e}")
                    continue
            
            if not goalies_data:
                print("\n❌ No goalie data collected")
                return None
            
            # Create DataFrame
            df = pd.DataFrame(goalies_data)
            
            # Sort by save percentage
            df = df.sort_values('SV_PCT', ascending=False)
            
            # Save to CSV
            os.makedirs('data', exist_ok=True)
            output_file = f'data/nhl_goalie_stats_{self.season}.csv'
            df.to_csv(output_file, index=False)
            
            # Count elite goalies
            elite_count = df['Is_Elite_Hot'].sum()
            
            print(f"\n{'=' * 70}")
            print(f"✅ Saved {len(df)} goalies to {output_file}")
            print(f"   🚨 Elite hot goalies: {elite_count}")
            print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Show elite goalies
            if elite_count > 0:
                print("\n🔥 ELITE HOT GOALIES (>92% Sv%, <2.30 GAA):")
                print("=" * 70)
                elite_df = df[df['Is_Elite_Hot'] == True]
                for _, goalie in elite_df.iterrows():
                    print(f"   {goalie['Goalie']:<25} ({goalie['Team']}) - "
                          f"{goalie['SV_PCT']:.1%} Sv%, {goalie['GAA']:.2f} GAA, {goalie['GP']} GP")
                print("\n⚠️  These goalies will be FLAGGED in your betting decisions!")
                print("   You decide: full bet (3%), half bet (1.5%), or skip")
            else:
                print("\n✅ No elite hot goalies detected")
                print("   (No goalies meet >92% Sv% AND <2.30 GAA thresholds)")
                print("   This is GOOD for betting - less uncertainty!")
            
            return df
            
        except Exception as e:
            print(f"❌ Error collecting goalie stats: {str(e)}")
            import traceback
            traceback.print_exc()
            return None


def main():
    """Run the goalie stats collector"""
    collector = GoalieStatsCollector()
    df = collector.collect_goalie_stats()
    
    if df is not None:
        print("\n" + "=" * 70)
        print("📊 TOP 10 GOALIES BY SAVE %")
        print("=" * 70)
        top_10 = df.head(10)[['Goalie', 'Team', 'GP', 'SV_PCT', 'GAA', 'Is_Elite_Hot']]
        print(top_10.to_string(index=False))
        print("\n" + "=" * 70)
        print("✅ Collection complete!")
        print("\nNOTE: Using full season stats as proxy for 'last 10 games'")
        print("      Elite goalies: >92% Sv% AND <2.30 GAA will be flagged")
        print("=" * 70)
    else:
        print("\n❌ Collection failed")


if __name__ == "__main__":
    main()