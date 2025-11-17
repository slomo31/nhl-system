"""
Verify Optimization Changes
============================
Check if the new thresholds are actually being used
"""

import sys
sys.path.append('analyzers')
sys.path.append('config')

from offensive_power_analyzer import OffensivePowerAnalyzer
from pace_analyzer import PaceAnalyzer
import season_config
import pandas as pd

print("\n" + "=" * 70)
print("🔍 VERIFYING OPTIMIZATION CHANGES")
print("=" * 70)

# Check season config
print("\n1. Season Config Thresholds:")
print(f"   YES threshold: {season_config.CONFIDENCE_THRESHOLD_YES}")
print(f"   MAYBE threshold: {season_config.CONFIDENCE_THRESHOLD_MAYBE}")
print()
if season_config.CONFIDENCE_THRESHOLD_YES == 75:
    print("   ✅ Season config updated correctly!")
else:
    print(f"   ❌ Still using old threshold ({season_config.CONFIDENCE_THRESHOLD_YES})")

# Test offensive analyzer
print("\n2. Testing Offensive Power Analyzer:")
team_stats = pd.read_csv('data/nhl_team_stats_2024_2025.csv')
offensive = OffensivePowerAnalyzer(team_stats)

# Test Washington (3.51) + Carolina (3.24) = avg 3.375
result = offensive.analyze_matchup('WSH', 'CAR')
avg = (3.51 + 3.24) / 2
print(f"   Washington (3.51) + Carolina (3.24) = {avg:.2f} avg")
print(f"   Score: {result['score']}/30 pts")
print(f"   Reason: {result['reason']}")

if result['score'] == 30:
    print("   ✅ Offensive analyzer updated correctly!")
elif result['score'] == 20:
    print("   ⚠️  Getting 20 pts (old threshold)")
else:
    print(f"   ❌ Unexpected score: {result['score']}")

# Test pace analyzer
print("\n3. Testing Pace Analyzer:")
pace = PaceAnalyzer(team_stats)
result = pace.analyze_matchup('WSH', 'CAR')
print(f"   Combined pace score: {result['score']}/25 pts")
print(f"   Reason: {result['reason']}")

if result['score'] == 25:
    print("   ✅ Pace analyzer updated correctly!")
else:
    print(f"   ⚠️  Not getting max points")

print("\n" + "=" * 70)
print("💡 ANALYSIS")
print("=" * 70)
print("\nExpected for Washington @ Carolina:")
print("  Offensive: 30 pts (3.375 avg > 3.1 threshold)")
print("  Pace: 25 pts (33.8 avg > 32 threshold)")
print("  Form: 3 pts (teams cold/neutral)")
print("  Buffer: 15 pts (3.26 buffer)")
print("  Schedule: 10 pts (rested)")
print("  TOTAL: 83 pts → YES at 75 threshold")
print("\nIf you're still seeing 73 pts, the files didn't update.")
print("=" * 70)
