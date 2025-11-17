"""
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
