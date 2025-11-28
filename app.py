"""
NHL Minimum Total System - Web App V3.1
=======================================
Flask app with Monte Carlo + Legacy tabs
"""
from flask import Flask, render_template, jsonify, request
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)


def load_results():
    """Load results from CSV"""
    try:
        results = pd.read_csv('nhl_system_results.csv')
        if 'game_time' in results.columns:
            results['game_time_parsed'] = pd.to_datetime(results['game_time'], utc=True)
        return results
    except FileNotFoundError:
        return pd.DataFrame()


def load_todays_picks():
    """Load today's V3.1 Monte Carlo picks"""
    today = datetime.now().strftime('%Y-%m-%d')
    decisions_dir = 'output_archive/decisions'
    
    if os.path.exists(decisions_dir):
        files = sorted(os.listdir(decisions_dir), reverse=True)
        for filename in files:
            if filename.startswith(today) and filename.endswith('.csv'):
                filepath = os.path.join(decisions_dir, filename)
                return pd.read_csv(filepath)
    
    return pd.DataFrame()


def calculate_legacy_stats(results_df):
    """Calculate stats for legacy system"""
    if len(results_df) == 0:
        return {
            'wins': 0, 'losses': 0, 'pending': 0, 
            'win_rate': 0, 'roi': 0, 'total_bets': 0
        }
    
    yes_bets = results_df[results_df['decision'] == 'YES']
    wins = len(yes_bets[yes_bets['result'] == 'WIN'])
    losses = len(yes_bets[yes_bets['result'] == 'LOSS'])
    pending = len(yes_bets[yes_bets['result'] == 'PENDING'])
    total = wins + losses
    win_rate = (wins / total * 100) if total > 0 else 0
    
    # ROI calculation (assuming -700 avg odds)
    profit_per_win = 100 / 700 * 3  # ~0.43 units per win
    loss_per_loss = 3  # 3 units per loss
    total_profit = (wins * profit_per_win) - (losses * loss_per_loss)
    total_risked = total * 3
    roi = (total_profit / total_risked * 100) if total_risked > 0 else 0
    
    return {
        'wins': wins, 
        'losses': losses, 
        'pending': pending, 
        'win_rate': win_rate, 
        'roi': roi, 
        'total_bets': total
    }


def calculate_mc_stats(results_df):
    """Calculate stats for Monte Carlo system"""
    if len(results_df) == 0 or 'system' not in results_df.columns:
        return {
            'wins': 0, 'losses': 0, 'pending': 0,
            'win_rate': 0, 'avg_hit_rate': 0
        }
    
    mc_results = results_df[results_df['system'] == 'monte_carlo']
    
    if len(mc_results) == 0:
        return {
            'wins': 0, 'losses': 0, 'pending': 0,
            'win_rate': 0, 'avg_hit_rate': 0
        }
    
    wins = len(mc_results[mc_results['result'] == 'WIN'])
    losses = len(mc_results[mc_results['result'] == 'LOSS'])
    pending = len(mc_results[mc_results['result'] == 'PENDING'])
    total = wins + losses
    win_rate = (wins / total * 100) if total > 0 else 0
    
    avg_hit_rate = mc_results['hit_rate'].mean() if 'hit_rate' in mc_results.columns else 0
    
    return {
        'wins': wins,
        'losses': losses,
        'pending': pending,
        'win_rate': win_rate,
        'avg_hit_rate': avg_hit_rate
    }


@app.route('/')
def index():
    """Main dashboard with tabs"""
    # Get system from query param (default to 'mc')
    system = request.args.get('system', 'mc')
    
    results = load_results()
    todays_picks = load_todays_picks()
    
    # Legacy stats
    legacy_stats = calculate_legacy_stats(results)
    
    # Monte Carlo stats
    mc_stats = calculate_mc_stats(results)
    
    # Today's picks breakdown
    if len(todays_picks) > 0 and 'decision' in todays_picks.columns:
        yes_picks = todays_picks[todays_picks['decision'] == 'YES']
        maybe_picks = todays_picks[todays_picks['decision'] == 'MAYBE']
        
        # Get 0-flag picks
        if 'flag_count' in todays_picks.columns:
            zero_flag = yes_picks[yes_picks['flag_count'] == 0]
        else:
            zero_flag = pd.DataFrame()
        
        # Average hit rate for YES picks
        if 'hit_rate' in yes_picks.columns and len(yes_picks) > 0:
            mc_stats['avg_hit_rate'] = yes_picks['hit_rate'].mean()
    else:
        yes_picks = pd.DataFrame()
        maybe_picks = pd.DataFrame()
        zero_flag = pd.DataFrame()
    
    # Prepare YES picks list (0 flags only)
    yes_list = []
    for _, pick in zero_flag.iterrows():
        hit_rate = pick.get('hit_rate', 0)
        if pd.isna(hit_rate):
            hit_rate = 0
        yes_list.append({
            'game': pick['game'],
            'line': pick['minimum_total'],
            'hit_rate': hit_rate,
            'flags': 0
        })
    
    # Prepare MAYBE picks list (top 10 by hit rate)
    maybe_list = []
    if len(maybe_picks) > 0:
        if 'hit_rate' in maybe_picks.columns:
            top_maybes = maybe_picks.nlargest(10, 'hit_rate')
        else:
            top_maybes = maybe_picks.head(10)
        
        for _, pick in top_maybes.iterrows():
            hit_rate = pick.get('hit_rate', 0)
            if pd.isna(hit_rate):
                hit_rate = 0
            flag_count = pick.get('flag_count', 0)
            if pd.isna(flag_count):
                flag_count = 0
            maybe_list.append({
                'game': pick['game'],
                'line': pick['minimum_total'],
                'hit_rate': hit_rate,
                'flags': int(flag_count)
            })
    
    # Legacy completed games
    legacy_completed = []
    if len(results) > 0 and 'result' in results.columns:
        yes_bets = results[results['decision'] == 'YES']
        completed = yes_bets[yes_bets['result'].isin(['WIN', 'LOSS'])]
        
        if 'game_time_parsed' in completed.columns:
            completed = completed.sort_values('game_time_parsed', ascending=False)
        elif 'game_time' in completed.columns:
            completed = completed.sort_values('game_time', ascending=False)
        
        for _, game in completed.head(20).iterrows():
            try:
                if 'game_time' in game:
                    date_str = pd.to_datetime(game['game_time'], utc=True).strftime('%Y-%m-%d')
                else:
                    date_str = 'N/A'
            except:
                date_str = 'N/A'
            
            actual = game.get('actual_total', 0)
            if pd.isna(actual):
                actual = 0
            
            legacy_completed.append({
                'date': date_str,
                'game': game['game'],
                'line': game['minimum_total'],
                'actual': actual,
                'buffer': actual - game['minimum_total'],
                'confidence': game.get('confidence', 0),
                'result': game['result'],
                'elite_goalie': game.get('elite_goalie_flag', False)
            })
    
    # Legacy pending games
    legacy_pending = []
    if len(results) > 0 and 'result' in results.columns:
        yes_bets = results[results['decision'] == 'YES']
        pending = yes_bets[yes_bets['result'] == 'PENDING']
        
        for _, game in pending.iterrows():
            try:
                if 'game_time' in game:
                    date_str = pd.to_datetime(game['game_time'], utc=True).strftime('%Y-%m-%d')
                else:
                    date_str = 'N/A'
            except:
                date_str = 'N/A'
            
            legacy_pending.append({
                'date': date_str,
                'game': game['game'],
                'line': game['minimum_total'],
                'confidence': game.get('confidence', 0),
                'elite_goalie': game.get('elite_goalie_flag', False)
            })
    
    return render_template(
        'dashboard.html',
        system=system,
        legacy_stats=legacy_stats,
        mc_stats=mc_stats,
        yes_picks=yes_list,
        maybe_picks=maybe_list,
        legacy_completed=legacy_completed,
        legacy_pending=legacy_pending,
        yes_count=len(yes_list),
        maybe_count=len(maybe_list),
        legacy_count=legacy_stats['total_bets'],
        updated=datetime.now().strftime('%B %d, %Y at %I:%M %p')
    )


@app.route('/api/stats')
def api_stats():
    """API endpoint for stats"""
    results = load_results()
    legacy_stats = calculate_legacy_stats(results)
    mc_stats = calculate_mc_stats(results)
    return jsonify({
        'legacy': legacy_stats,
        'monte_carlo': mc_stats
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)