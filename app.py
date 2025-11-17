"""
NHL Minimum Total System - Web App
"""
from flask import Flask, render_template, jsonify
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

def load_results():
    try:
        results = pd.read_csv('nhl_system_results.csv')
        results['game_time_parsed'] = pd.to_datetime(results['game_time'], utc=True)
        return results
    except FileNotFoundError:
        return pd.DataFrame()

def calculate_stats(results_df):
    if len(results_df) == 0:
        return {'wins': 0, 'losses': 0, 'pending': 0, 'win_rate': 0, 'roi': 0, 'total_bets': 0}
    yes_bets = results_df[results_df['decision'] == 'YES']
    wins = len(yes_bets[yes_bets['result'] == 'WIN'])
    losses = len(yes_bets[yes_bets['result'] == 'LOSS'])
    pending = len(yes_bets[yes_bets['result'] == 'PENDING'])
    total = wins + losses
    win_rate = (wins / total * 100) if total > 0 else 0
    roi = ((wins * 12.5) - (losses * 100)) / (total * 100) * 100 if total > 0 else 0
    return {'wins': wins, 'losses': losses, 'pending': pending, 'win_rate': win_rate, 'roi': roi, 'total_bets': total}

@app.route('/')
def index():
    results = load_results()
    stats = calculate_stats(results)
    yes_bets = results[results['decision'] == 'YES']
    completed = yes_bets[yes_bets['result'] != 'PENDING'].sort_values('game_time_parsed', ascending=False).head(20)
    pending = yes_bets[yes_bets['result'] == 'PENDING'].sort_values('game_time_parsed')
    completed_list = []
    for _, game in completed.iterrows():
        completed_list.append({'date': pd.to_datetime(game['game_time'], utc=True).strftime('%Y-%m-%d'), 'game': game['game'], 'line': game['minimum_total'], 'actual': game['actual_total'], 'buffer': game['actual_total'] - game['minimum_total'], 'confidence': game['confidence'], 'result': game['result'], 'elite_goalie': game['elite_goalie_flag']})
    pending_list = []
    for _, game in pending.iterrows():
        pending_list.append({'date': pd.to_datetime(game['game_time'], utc=True).strftime('%Y-%m-%d'), 'game': game['game'], 'line': game['minimum_total'], 'confidence': game['confidence'], 'elite_goalie': game['elite_goalie_flag']})
    return render_template('dashboard.html', stats=stats, completed=completed_list, pending=pending_list, updated=datetime.now().strftime('%B %d, %Y at %I:%M %p'))

@app.route('/api/stats')
def api_stats():
    results = load_results()
    stats = calculate_stats(results)
    return jsonify(stats)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
