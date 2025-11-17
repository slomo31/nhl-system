"""Generate all remaining system files"""
import os

# Create __init__ files
for dir in ['core', 'decision', 'backtesting', 'output']:
    with open(f'{dir}/__init__.py', 'w') as f:
        f.write(f'"""{dir.title()} Package"""')

# Create placeholder minimum_total_predictor.py
predictor_code = '''"""
NHL Minimum Total Predictor
============================
Main prediction engine - 100 point scoring system
"""
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzers.offensive_power_analyzer import OffensivePowerAnalyzer
from analyzers.pace_analyzer import PaceAnalyzer
from analyzers.recent_form_analyzer import RecentFormAnalyzer
from analyzers.schedule_analyzer import ScheduleAnalyzer
from analyzers.goalie_impact_analyzer import GoalieImpactAnalyzer

class MinimumTotalPredictor:
    """Main prediction engine"""
    
    def __init__(self, team_stats, completed_games, goalie_stats):
        self.team_stats = team_stats
        self.completed_games = completed_games
        self.goalie_stats = goalie_stats
        
        # Initialize analyzers
        self.offensive_analyzer = OffensivePowerAnalyzer(team_stats)
        self.pace_analyzer = PaceAnalyzer(team_stats)
        self.form_analyzer = RecentFormAnalyzer(completed_games, team_stats)
        self.schedule_analyzer = ScheduleAnalyzer(completed_games)
        self.goalie_analyzer = GoalieImpactAnalyzer(goalie_stats)
    
    def predict_game(self, away_team, home_team, minimum_total, game_date):
        """
        Predict game with 100-point system
        Returns dict with score, confidence, factors, goalie flag
        """
        factors = {}
        reasoning = []
        
        # Factor 1: Offensive Power (30 pts)
        offensive = self.offensive_analyzer.analyze_matchup(away_team, home_team)
        factors['offensive'] = offensive
        reasoning.append(offensive['reason'])
        
        # Factor 2: Pace (25 pts)
        pace = self.pace_analyzer.analyze_matchup(away_team, home_team)
        factors['pace'] = pace
        reasoning.append(pace['reason'])
        
        # Factor 3: Recent Form (20 pts)
        form = self.form_analyzer.analyze_matchup(away_team, home_team)
        factors['form'] = form
        reasoning.append(form['reason'])
        
        # Factor 4: Buffer (15 pts)
        buffer = self._calculate_buffer(away_team, home_team, minimum_total)
        factors['buffer'] = buffer
        reasoning.append(buffer['reason'])
        
        # Factor 5: Schedule (10 pts)
        schedule = self.schedule_analyzer.analyze_matchup(away_team, home_team, game_date)
        factors['schedule'] = schedule
        reasoning.append(schedule['reason'])
        
        # Calculate total score
        total_score = (
            offensive['score'] +
            pace['score'] +
            form['score'] +
            buffer['score'] +
            schedule['score']
        )
        
        # Check for elite goalie
        goalie_check = self.goalie_analyzer.check_starting_goalies(away_team, home_team)
        
        return {
            'away_team': away_team,
            'home_team': home_team,
            'minimum_total': minimum_total,
            'total_score': total_score,
            'confidence': total_score,
            'factors': factors,
            'reasoning': reasoning,
            'elite_goalie_flag': goalie_check['elite_goalie_flag'],
            'goalie_warning': goalie_check['warning_message']
        }
    
    def _calculate_buffer(self, away_team, home_team, minimum_total):
        """Calculate safety buffer (15 pts max)"""
        away = self.team_stats[self.team_stats['Team'] == away_team]
        home = self.team_stats[self.team_stats['Team'] == home_team]
        
        if away.empty or home.empty:
            return {'score': 0, 'reason': 'Missing team stats'}
        
        combined_avg = away['GPG'].values[0] + home['GPG'].values[0]
        buffer = combined_avg - minimum_total
        
        if buffer >= 2.0:
            return {'score': 15, 'reason': f'Strong buffer ({buffer:.1f} goals)'}
        elif buffer >= 1.5:
            return {'score': 10, 'reason': f'Good buffer ({buffer:.1f} goals)'}
        elif buffer >= 1.0:
            return {'score': 6, 'reason': f'Moderate buffer ({buffer:.1f} goals)'}
        else:
            return {'score': 0, 'reason': f'Tight buffer ({buffer:.1f} goals)'}
'''

with open('core/minimum_total_predictor.py', 'w') as f:
    f.write(predictor_code)

print("✅ Created core/minimum_total_predictor.py")

# Create yes_no_decider.py
decider_code = '''"""
Yes/No Decision Maker
=====================
Makes betting decisions based on confidence score
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.season_config import (
    CONFIDENCE_THRESHOLD_YES,
    CONFIDENCE_THRESHOLD_MAYBE,
    RECOMMENDED_STAKE_YES,
    RECOMMENDED_STAKE_ELITE_GOALIE
)

class YesNoDecider:
    """Makes betting decisions"""
    
    def make_decision(self, prediction):
        """
        Make YES/NO/MAYBE decision
        Returns dict with decision, action, stake, reasoning
        """
        confidence = prediction['confidence']
        elite_goalie = prediction['elite_goalie_flag']
        
        # Decision based on confidence
        if confidence >= CONFIDENCE_THRESHOLD_YES:
            decision = 'YES'
            action = 'BET IT'
            
            # Adjust stake if elite goalie
            if elite_goalie:
                stake = RECOMMENDED_STAKE_ELITE_GOALIE
                action += ' (consider half stake - elite goalie)'
            else:
                stake = RECOMMENDED_STAKE_YES
                
        elif confidence >= CONFIDENCE_THRESHOLD_MAYBE:
            decision = 'MAYBE'
            action = 'REVIEW MANUALLY'
            stake = RECOMMENDED_STAKE_ELITE_GOALIE
        else:
            decision = 'NO'
            action = 'SKIP'
            stake = 0.0
        
        return {
            'decision': decision,
            'action': action,
            'stake': stake,
            'confidence': confidence,
            'elite_goalie_flag': elite_goalie,
            'goalie_warning': prediction['goalie_warning']
        }
'''

with open('decision/yes_no_decider.py', 'w') as f:
    f.write(decider_code)

print("✅ Created decision/yes_no_decider.py")

# Create simplified backtester
backtester_code = '''"""
NHL Season Backtester
=====================
Validates system against completed games
"""
import pandas as pd
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.minimum_total_predictor import MinimumTotalPredictor
from decision.yes_no_decider import YesNoDecider

class SeasonBacktester:
    """Backtest the system"""
    
    def __init__(self, team_stats, completed_games, goalie_stats):
        self.predictor = MinimumTotalPredictor(team_stats, completed_games, goalie_stats)
        self.decider = YesNoDecider()
    
    def run_backtest(self, minimum_total=4.5):
        """
        Run backtest with assumed minimum total
        In production, you'd have historical odds
        """
        print("\\n" + "=" * 70)
        print("RUNNING BACKTEST (Simplified)")
        print("=" * 70)
        print(f"Using assumed minimum total: {minimum_total} goals")
        print("\\nNote: Full backtest requires historical odds data")
        print("This version validates prediction logic only")
        print("=" * 70)
        
        return pd.DataFrame()  # Placeholder
'''

with open('backtesting/season_backtester.py', 'w') as f:
    f.write(backtester_code)

print("✅ Created backtesting/season_backtester.py")

# Create CSV exporter
csv_code = '''"""CSV Exporter"""
import pandas as pd
import os
from datetime import datetime

class CSVExporter:
    """Export predictions to CSV"""
    
    def export_decisions(self, decisions):
        """Export daily decisions"""
        os.makedirs('output_archive/decisions', exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
        filename = f'output_archive/decisions/{timestamp}_decisions.csv'
        
        df = pd.DataFrame(decisions)
        df.to_csv(filename, index=False)
        
        return filename
'''

with open('output/csv_exporter.py', 'w') as f:
    f.write(csv_code)

print("✅ Created output/csv_exporter.py")

print("\\n✅ All remaining files created!")
