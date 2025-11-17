"""Schedule Analyzer - Back-to-back and rest days"""
import pandas as pd
from datetime import datetime, timedelta

class ScheduleAnalyzer:
    def __init__(self, completed_games):
        self.completed_games = completed_games
    
    def analyze_matchup(self, away_team, home_team, game_date):
        """Analyze rest/fatigue (10 pts max)"""
        away_rest = self._get_rest_days(away_team, game_date)
        home_rest = self._get_rest_days(home_team, game_date)
        
        combined_score = away_rest['score'] + home_rest['score']
        
        return {
            'score': combined_score,
            'reason': f"{away_team} {away_rest['rest_desc']} | {home_team} {home_rest['rest_desc']}"
        }
    
    def _get_rest_days(self, team, game_date):
        """Calculate rest days for a team (5 pts max)"""
        team_games = self.completed_games[
            (self.completed_games['Away_Team'] == team) | 
            (self.completed_games['Home_Team'] == team)
        ]
        
        if team_games.empty:
            return {'score': 5, 'rest_desc': 'unknown rest'}
        
        last_game = team_games['Date'].max()
        last_game_date = pd.to_datetime(last_game)
        current_date = pd.to_datetime(game_date)
        
        rest_days = (current_date - last_game_date).days
        
        if rest_days == 0:
            return {'score': 0, 'rest_desc': 'back-to-back'}
        elif rest_days == 1:
            return {'score': 3, 'rest_desc': '1 day rest'}
        elif rest_days >= 2:
            return {'score': 5, 'rest_desc': f'{rest_days} days rest'}
        else:
            return {'score': 5, 'rest_desc': 'rested'}
