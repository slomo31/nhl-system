"""Recent Form Analyzer - Last 10 games scoring trends"""
import pandas as pd

class RecentFormAnalyzer:
    def __init__(self, completed_games, team_stats):
        self.completed_games = completed_games
        self.team_stats = team_stats
    
    def analyze_matchup(self, away_team, home_team):
        """Analyze recent scoring form (20 pts max)"""
        away_form = self._get_team_form(away_team)
        home_form = self._get_team_form(home_team)
        
        combined_score = away_form['score'] + home_form['score']
        
        return {
            'score': combined_score,
            'reason': f"{away_team} {away_form['status']} | {home_team} {home_form['status']}"
        }
    
    def _get_team_form(self, team):
        """Get form for one team (10 pts max)"""
        recent = self.completed_games[
            (self.completed_games['Away_Team'] == team) | 
            (self.completed_games['Home_Team'] == team)
        ].tail(10)
        
        if len(recent) < 5:
            return {'score': 0, 'status': 'insufficient data'}
        
        # Calculate goals for
        goals_for = []
        for _, game in recent.iterrows():
            if game['Away_Team'] == team:
                goals_for.append(game['Away_Goals'])
            else:
                goals_for.append(game['Home_Goals'])
        
        avg_goals = sum(goals_for) / len(goals_for)
        
        # Get team season average
        team_data = self.team_stats[self.team_stats['Team'] == team]
        if team_data.empty:
            return {'score': 0, 'status': 'no stats'}
        
        season_avg = team_data['GPG'].values[0]
        diff = avg_goals - season_avg
        
        if diff >= 1.0:
            return {'score': 10, 'status': 'hot'}
        elif diff >= 0.5:
            return {'score': 6, 'status': 'warm'}
        elif diff >= 0:
            return {'score': 3, 'status': 'neutral'}
        else:
            return {'score': 0, 'status': 'cold'}
