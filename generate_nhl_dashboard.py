"""
NHL Minimum Total System - Dashboard Generator
===============================================
Creates a beautiful HTML dashboard showing system performance

Matches the NBA system dashboard design
"""

import pandas as pd
import os
from datetime import datetime
import glob


def load_all_decisions():
    """Load all decision CSVs from archive"""
    decision_files = glob.glob('output_archive/decisions/*_decisions.csv')
    
    if not decision_files:
        return None
    
    all_decisions = []
    
    for file in sorted(decision_files):
        df = pd.read_csv(file)
        df['source_file'] = os.path.basename(file)
        all_decisions.append(df)
    
    combined = pd.concat(all_decisions, ignore_index=True)
    
    # Remove duplicates - keep highest confidence for each unique game
    combined['game_time_parsed'] = pd.to_datetime(combined['game_time'], utc=True)
    combined['game_key'] = (
        combined['game_time_parsed'].dt.date.astype(str) + '_' + 
        combined['game']
    )
    
    combined = combined.sort_values('confidence', ascending=False)
    deduplicated = combined.drop_duplicates(subset='game_key', keep='first')
    
    return deduplicated


def load_completed_games():
    """Load completed games with results"""
    try:
        games = pd.read_csv('data/nhl_completed_games_2024_2025.csv')
        return games
    except FileNotFoundError:
        return pd.DataFrame()


def match_predictions_to_results(decisions_df, completed_games_df):
    """Match each prediction to its actual result"""
    
    if completed_games_df.empty:
        return decisions_df
    
    # Parse dates
    decisions_df['game_date'] = pd.to_datetime(decisions_df['game_time'], utc=True).dt.date
    completed_games_df['Date'] = pd.to_datetime(completed_games_df['Date']).dt.date
    
    # Add result columns
    decisions_df['actual_total'] = None
    decisions_df['result'] = 'PENDING'
    
    for idx, pred in decisions_df.iterrows():
        game_date = pred['game_date']
        
        # Parse game string (e.g., "Toronto Maple Leafs @ Boston Bruins")
        parts = pred['game'].split(' @ ')
        if len(parts) != 2:
            continue
        
        away_full = parts[0].strip()
        home_full = parts[1].strip()
        
        # Try to find matching game
        from datetime import timedelta
        dates_to_check = [
            game_date,
            game_date - timedelta(days=1),
            game_date + timedelta(days=1)
        ]
        
        # Match by checking if completed game teams contain the full names
        for _, comp_game in completed_games_df.iterrows():
            if comp_game['Date'] not in dates_to_check:
                continue
            
            away_team = comp_game['Away_Team']
            home_team = comp_game['Home_Team']
            
            # Simple match - if teams are in the game string
            if away_team in away_full and home_team in home_full:
                actual_total = comp_game['Total_Goals']
                decisions_df.at[idx, 'actual_total'] = actual_total
                
                minimum = pred['minimum_total']
                
                if pred['decision'] == 'YES':
                    if actual_total > minimum:
                        decisions_df.at[idx, 'result'] = 'WIN'
                    else:
                        decisions_df.at[idx, 'result'] = 'LOSS'
                elif pred['decision'] == 'NO':
                    if actual_total > minimum:
                        decisions_df.at[idx, 'result'] = 'WOULD_WIN'
                    else:
                        decisions_df.at[idx, 'result'] = 'CORRECT_SKIP'
                break
    
    return decisions_df


def calculate_stats(decisions_df):
    """Calculate all dashboard statistics"""
    
    yes_bets = decisions_df[decisions_df['decision'] == 'YES']
    no_bets = decisions_df[decisions_df['decision'] == 'NO']
    
    # YES bets stats
    wins = len(yes_bets[yes_bets['result'] == 'WIN'])
    losses = len(yes_bets[yes_bets['result'] == 'LOSS'])
    pending = len(yes_bets[yes_bets['result'] == 'PENDING'])
    
    win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
    
    # ROI calculation (assuming average -800 odds)
    total_wagered = (wins + losses) * 100  # $100 per bet
    avg_odds_decimal = 1 + (100 / 800)  # -800 = 1.125 decimal
    profit_per_win = 100 * (avg_odds_decimal - 1)
    total_profit = (wins * profit_per_win) - (losses * 100)
    roi = (total_profit / total_wagered * 100) if total_wagered > 0 else 0
    
    # Missed opportunities
    missed = len(no_bets[no_bets['result'] == 'WOULD_WIN'])
    correct_skips = len(no_bets[no_bets['result'] == 'CORRECT_SKIP'])
    
    # Confidence distribution
    conf_dist = {
        '65-69%': len(yes_bets[(yes_bets['confidence'] >= 65) & (yes_bets['confidence'] < 70)]),
        '70-74%': len(yes_bets[(yes_bets['confidence'] >= 70) & (yes_bets['confidence'] < 75)]),
        '75-79%': len(yes_bets[(yes_bets['confidence'] >= 75) & (yes_bets['confidence'] < 80)]),
        '80%+': len(yes_bets[yes_bets['confidence'] >= 80])
    }
    
    return {
        'wins': wins,
        'losses': losses,
        'pending': pending,
        'win_rate': win_rate,
        'roi': roi,
        'missed': missed,
        'correct_skips': correct_skips,
        'conf_dist': conf_dist,
        'yes_bets': yes_bets,
        'no_bets': no_bets
    }


def generate_html_dashboard(stats):
    """Generate the HTML dashboard"""
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NHL Minimum Total System - Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }}
        
        .header h1 {{
            font-size: 48px;
            font-weight: 700;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            font-size: 18px;
            opacity: 0.9;
        }}
        
        .header .updated {{
            font-size: 14px;
            opacity: 0.7;
            margin-top: 5px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .stat-label {{
            font-size: 14px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        
        .stat-value {{
            font-size: 48px;
            font-weight: 700;
            color: #2d3748;
        }}
        
        .stat-value.green {{
            color: #48bb78;
        }}
        
        .stat-value.orange {{
            color: #ed8936;
        }}
        
        .stat-subtext {{
            font-size: 14px;
            color: #718096;
            margin-top: 8px;
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .chart-card {{
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .chart-title {{
            font-size: 18px;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
        }}
        
        .chart-title::before {{
            content: '';
            width: 4px;
            height: 20px;
            background: #667eea;
            margin-right: 10px;
            border-radius: 2px;
        }}
        
        .bar-chart {{
            display: flex;
            gap: 20px;
            height: 200px;
            align-items: flex-end;
        }}
        
        .bar {{
            flex: 1;
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
            border-radius: 8px 8px 0 0;
            position: relative;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            align-items: center;
            color: white;
            font-weight: 600;
            padding-bottom: 10px;
        }}
        
        .bar.green {{
            background: linear-gradient(180deg, #48bb78 0%, #38a169 100%);
        }}
        
        .bar.orange {{
            background: linear-gradient(180deg, #ed8936 0%, #dd6b20 100%);
        }}
        
        .bar-label {{
            position: absolute;
            bottom: -25px;
            font-size: 12px;
            color: #666;
            text-align: center;
        }}
        
        .table-card {{
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        
        .table-header {{
            font-size: 20px;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
        }}
        
        .table-header::before {{
            content: '✅';
            margin-right: 10px;
            font-size: 24px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th {{
            text-align: left;
            padding: 12px;
            background: #f7fafc;
            color: #2d3748;
            font-weight: 600;
            font-size: 14px;
            border-bottom: 2px solid #e2e8f0;
        }}
        
        td {{
            padding: 12px;
            border-bottom: 1px solid #e2e8f0;
            font-size: 14px;
        }}
        
        tr:hover {{
            background: #f7fafc;
        }}
        
        .win {{
            color: #48bb78;
            font-weight: 600;
        }}
        
        .loss {{
            color: #f56565;
            font-weight: 600;
        }}
        
        .pending {{
            color: #ed8936;
            font-weight: 600;
        }}
        
        .missed {{
            color: #ed8936;
            font-weight: 600;
        }}
        
        @media (max-width: 768px) {{
            .charts-grid {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 32px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏒 NHL Minimum Total System</h1>
            <div class="subtitle">Performance Dashboard - 2024-2025 Season</div>
            <div class="updated">Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">RECORD</div>
                <div class="stat-value green">{stats['wins']}-{stats['losses']}</div>
                <div class="stat-subtext">{stats['pending']} pending</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">WIN RATE</div>
                <div class="stat-value">{stats['win_rate']:.1f}%</div>
                <div class="stat-subtext">{stats['wins'] + stats['losses']} completed</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">ROI</div>
                <div class="stat-value green">+{stats['roi']:.1f}%</div>
                <div class="stat-subtext">At -800 avg odds</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">MISSED OPPORTUNITIES</div>
                <div class="stat-value orange">{stats['missed']}</div>
                <div class="stat-subtext">{stats['correct_skips']} correct skips</div>
            </div>
        </div>
        
        <div class="charts-grid">
            <div class="chart-card">
                <div class="chart-title">📊 Confidence Distribution</div>
                <div class="bar-chart">
"""
    
    # Add confidence bars
    max_height = max(stats['conf_dist'].values()) if stats['conf_dist'].values() else 1
    
    for conf_range, count in stats['conf_dist'].items():
        height_pct = (count / max_height * 100) if max_height > 0 else 0
        html += f"""
                    <div class="bar" style="height: {height_pct}%;">
                        {count}
                        <div class="bar-label">{conf_range}</div>
                    </div>
"""
    
    # Calculate results for pie chart
    total_completed = stats['wins'] + stats['losses']
    wins_pct = (stats['wins'] / total_completed * 100) if total_completed > 0 else 0
    losses_pct = (stats['losses'] / total_completed * 100) if total_completed > 0 else 0
    missed_pct = (stats['missed'] / (total_completed + stats['missed']) * 100) if (total_completed + stats['missed']) > 0 else 0
    
    html += f"""
                </div>
            </div>
            
            <div class="chart-card">
                <div class="chart-title">📈 Results Overview</div>
                <div class="bar-chart">
                    <div class="bar green" style="height: {wins_pct}%;">
                        {stats['wins']}
                        <div class="bar-label">Wins</div>
                    </div>
                    <div class="bar loss" style="height: {losses_pct}%; background: linear-gradient(180deg, #f56565 0%, #e53e3e 100%);">
                        {stats['losses']}
                        <div class="bar-label">Losses</div>
                    </div>
                    <div class="bar orange" style="height: {missed_pct}%;">
                        {stats['missed']}
                        <div class="bar-label">Missed</div>
                    </div>
                </div>
            </div>
        </div>
"""
    
    # YES BETS TABLE
    completed_yes = stats['yes_bets'][stats['yes_bets']['result'] != 'PENDING'].sort_values('game_time_parsed', ascending=False)
    
    if len(completed_yes) > 0:
        html += """
        <div class="table-card">
            <div class="table-header">YES BETS - Completed Games</div>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Game</th>
                        <th>Line</th>
                        <th>Actual</th>
                        <th>Buffer</th>
                        <th>Conf</th>
                        <th>Result</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for _, row in completed_yes.head(20).iterrows():
            result_class = 'win' if row['result'] == 'WIN' else 'loss'
            result_text = 'WIN' if row['result'] == 'WIN' else 'LOSS'
            
            date_str = pd.to_datetime(row['game_time'], utc=True).strftime('%Y-%m-%d')
            buffer = row['actual_total'] - row['minimum_total'] if pd.notna(row['actual_total']) else 0
            buffer_str = f"+{buffer:.1f}" if buffer > 0 else f"{buffer:.1f}"
            
            html += f"""
                    <tr>
                        <td>{date_str}</td>
                        <td>{row['game']}</td>
                        <td>{row['minimum_total']:.1f}</td>
                        <td>{row['actual_total']:.1f}</td>
                        <td>{buffer_str}</td>
                        <td>{row['confidence']}%</td>
                        <td class="{result_class}">{result_text}</td>
                    </tr>
"""
        
        html += """
                </tbody>
            </table>
        </div>
"""
    
    # PENDING GAMES
    pending_yes = stats['yes_bets'][stats['yes_bets']['result'] == 'PENDING'].sort_values('game_time_parsed')
    
    if len(pending_yes) > 0:
        html += """
        <div class="table-card">
            <div class="table-header" style="font-size: 20px;">⏳ PENDING GAMES</div>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Game</th>
                        <th>Line</th>
                        <th>Conf</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for _, row in pending_yes.iterrows():
            date_str = pd.to_datetime(row['game_time'], utc=True).strftime('%Y-%m-%d')
            
            html += f"""
                    <tr>
                        <td>{date_str}</td>
                        <td>{row['game']}</td>
                        <td>{row['minimum_total']:.1f}</td>
                        <td>{row['confidence']}%</td>
                        <td class="pending">PENDING</td>
                    </tr>
"""
        
        html += """
                </tbody>
            </table>
        </div>
"""
    
    # MISSED OPPORTUNITIES
    missed_opps = stats['no_bets'][stats['no_bets']['result'] == 'WOULD_WIN'].sort_values('game_time_parsed', ascending=False)
    
    if len(missed_opps) > 0:
        html += """
        <div class="table-card">
            <div class="table-header" style="font-size: 20px;">⚠️ NO BETS - Missed Opportunities</div>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Game</th>
                        <th>Line</th>
                        <th>Actual</th>
                        <th>Conf</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for _, row in missed_opps.head(20).iterrows():
            date_str = pd.to_datetime(row['game_time'], utc=True).strftime('%Y-%m-%d')
            
            html += f"""
                    <tr>
                        <td>{date_str}</td>
                        <td>{row['game']}</td>
                        <td>{row['minimum_total']:.1f}</td>
                        <td>{row['actual_total']:.1f}</td>
                        <td>{row['confidence']}%</td>
                        <td class="missed">MISSED WIN</td>
                    </tr>
"""
        
        html += """
                </tbody>
            </table>
        </div>
"""
    
    html += """
    </div>
</body>
</html>
"""
    
    return html


def main():
    """Generate the dashboard"""
    
    print("Generating NHL System Dashboard...")
    
    # Load pre-matched results (from update_results.py)
    try:
        decisions_with_results = pd.read_csv('nhl_system_results.csv')
        decisions_with_results['game_time_parsed'] = pd.to_datetime(decisions_with_results['game_time'], utc=True)
        print(f"✅ Loaded results from nhl_system_results.csv")
    except FileNotFoundError:
        print("⚠️  No results file found. Run: python update_results.py")
        print("   Falling back to manual matching...")
        
        # Fallback to old method
        decisions = load_all_decisions()
        if decisions is None:
            print("No decision files found!")
            return
        
        completed_games = load_completed_games()
        decisions_with_results = match_predictions_to_results(decisions, completed_games)
    
    # Calculate stats
    stats = calculate_stats(decisions_with_results)
    
    # Generate HTML
    html = generate_html_dashboard(stats)
    
    # Save dashboard
    output_file = 'nhl_min_total_dashboard.html'
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"✅ Dashboard generated: {output_file}")
    print(f"\nStats Summary:")
    print(f"  Record: {stats['wins']}-{stats['losses']} ({stats['win_rate']:.1f}%)")
    print(f"  ROI: +{stats['roi']:.1f}%")
    print(f"  Missed: {stats['missed']}")


if __name__ == "__main__":
    main()