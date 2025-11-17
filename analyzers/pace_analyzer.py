"""Pace Analyzer - Shots per game analysis (OPTIMIZED FOR NHL)"""
import pandas as pd

class PaceAnalyzer:
    def __init__(self, team_stats):
        self.team_stats = team_stats
    
    def analyze_matchup(self, away_team, home_team):
        """Analyze combined pace (25 pts max)"""
        away = self.team_stats[self.team_stats['Team'] == away_team]
        home = self.team_stats[self.team_stats['Team'] == home_team]
        
        if away.empty or home.empty:
            return {'score': 0, 'reason': 'Missing team stats'}
        
        avg_spg = (away['SPG'].values[0] + home['SPG'].values[0]) / 2
        
        # OPTIMIZED THRESHOLDS FOR NHL
        if avg_spg >= 32:
            return {'score': 25, 'reason': f'Fast pace ({avg_spg:.1f} shots/game)'}
        elif avg_spg >= 30:
            return {'score': 17, 'reason': f'Good pace ({avg_spg:.1f} shots/game)'}
        elif avg_spg >= 28:
            return {'score': 10, 'reason': f'Average pace ({avg_spg:.1f} shots/game)'}
        else:
            return {'score': 0, 'reason': f'Slow pace ({avg_spg:.1f} shots/game)'}