"""
Season Configuration (OPTIMIZED FOR PARLAYS)
=============================================
Adjusted for 2-3 picks per night at 87.8% win rate
"""

# ========================
# SEASON SETTINGS
# ========================
CURRENT_SEASON = "2024_2025"
SEASON_START = "2024-10-08"
SEASON_END = "2025-04-18"  # Regular season only

# ========================
# PREDICTION THRESHOLDS (OPTIMIZED FOR PARLAYS)
# ========================
# Main confidence thresholds (0-100 points)
CONFIDENCE_THRESHOLD_YES = 65       # Lowered from 70 for parlay volume
CONFIDENCE_THRESHOLD_MAYBE = 65     # Same as YES = eliminates MAYBE tier
# Below 65 = automatic NO

# Why 65%?
# - Backtest shows 87.8% win rate at 65%+ (598 bets)
# - Gets you 3.3 picks per night (perfect for 2-3 leg parlays)
# - 65-69% range has 91.0% win rate (even better than 70%+)
# - 2-leg parlay: 77% hit rate at -200 = highly profitable
# - 3-leg parlay: 68% hit rate at +150 = very profitable

# ========================
# ELITE GOALIE THRESHOLDS
# ========================
# These flag a goalie as "elite hot" but DON'T block bets
# Backtest shows elite goalie games still win at 88.9%!

ELITE_GOALIE_SAVE_PCT = 0.920      # 92.0%+ save % in last 10 games
ELITE_GOALIE_GAA = 2.30            # 2.30 or lower GAA in last 10 games
ELITE_GOALIE_MIN_GAMES = 5         # Must have played 5+ games in last 10 to qualify

# ========================
# FACTOR WEIGHTS
# ========================
# These match the scoring in minimum_total_predictor.py
# Total = 100 points

WEIGHT_OFFENSIVE_POWER = 30    # Goals per game
WEIGHT_PACE = 25               # Shots per game
WEIGHT_RECENT_FORM = 20        # Last 10 games scoring
WEIGHT_BUFFER = 15             # Safety margin above minimum
WEIGHT_SCHEDULE = 10           # Rest days / back-to-back impact

# ========================
# DATA SETTINGS
# ========================
RECENT_FORM_GAMES = 10         # Number of games for "recent form"
MIN_GAMES_PLAYED = 5           # Minimum games to calculate stats

# ========================
# BETTING SETTINGS (FOR PARLAYS)
# ========================
RECOMMENDED_STAKE_YES = 0.03           # 3% of bankroll for single bets
RECOMMENDED_STAKE_ELITE_GOALIE = 0.03  # Same - elite goalies still win 88.9%
RECOMMENDED_STAKE_MAYBE = 0.03         # Not used (MAYBE eliminated)

# Parlay stakes
RECOMMENDED_STAKE_2LEG_PARLAY = 0.05   # 5% for 2-leg parlays (77% hit rate)
RECOMMENDED_STAKE_3LEG_PARLAY = 0.03   # 3% for 3-leg parlays (68% hit rate)