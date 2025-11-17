"""Offensive Power Analyzer - Goals per game analysis (OPTIMIZED FOR NHL)"""
import pandas as pd

class OffensivePowerAnalyzer:
    def __init__(self, team_stats):
        self.team_stats = team_stats
    
    def analyze_matchup(self, away_team, home_team):
        """Analyze combined offensive power (30 pts max)"""
        away = self.team_stats[self.team_stats['Team'] == away_team]
        home = self.team_stats[self.team_stats['Team'] == home_team]
        
        if away.empty or home.empty:
            return {'score': 0, 'reason': 'Missing team stats'}
        
        avg_gpg = (away['GPG'].values[0] + home['GPG'].values[0]) / 2
        
        # OPTIMIZED THRESHOLDS FOR NHL (avg game = ~6 goals)
        if avg_gpg >= 3.4:
            return {'score': 30, 'reason': f'Elite offense ({avg_gpg:.2f} GPG)'}
        elif avg_gpg >= 3.1:
            return {'score': 20, 'reason': f'Strong offense ({avg_gpg:.2f} GPG)'}
        elif avg_gpg >= 2.8:
            return {'score': 10, 'reason': f'Average offense ({avg_gpg:.2f} GPG)'}
        else:
            return {'score': 0, 'reason': f'Weak offense ({avg_gpg:.2f} GPG)'}