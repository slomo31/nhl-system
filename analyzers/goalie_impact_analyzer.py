"""Goalie Impact Analyzer - Elite goalie detection"""
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.season_config import ELITE_GOALIE_SAVE_PCT, ELITE_GOALIE_GAA

class GoalieImpactAnalyzer:
    def __init__(self, goalie_stats):
        self.goalie_stats = goalie_stats
    
    def check_starting_goalies(self, away_team, home_team):
        """
        Check if either starting goalie is elite hot
        Returns flag and warning message
        """
        away_goalies = self.goalie_stats[self.goalie_stats['Team'] == away_team]
        home_goalies = self.goalie_stats[self.goalie_stats['Team'] == home_team]
        
        elite_goalie_flag = False
        warning_message = ""
        
        # Check away team starter (highest GP)
        if not away_goalies.empty:
            away_starter = away_goalies.sort_values('GP', ascending=False).iloc[0]
            if away_starter['Is_Elite_Hot']:
                elite_goalie_flag = True
                warning_message += f"{away_starter['Goalie']} ({away_team}) - {away_starter['Last_10_SV_PCT']:.1%} Sv%, {away_starter['Last_10_GAA']:.2f} GAA"
        
        # Check home team starter
        if not home_goalies.empty:
            home_starter = home_goalies.sort_values('GP', ascending=False).iloc[0]
            if home_starter['Is_Elite_Hot']:
                if elite_goalie_flag:
                    warning_message += " | "
                elite_goalie_flag = True
                warning_message += f"{home_starter['Goalie']} ({home_team}) - {home_starter['Last_10_SV_PCT']:.1%} Sv%, {home_starter['Last_10_GAA']:.2f} GAA"
        
        return {
            'elite_goalie_flag': elite_goalie_flag,
            'warning_message': warning_message if elite_goalie_flag else "No elite goalie concerns"
        }
