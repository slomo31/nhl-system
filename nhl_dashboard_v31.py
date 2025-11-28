"""
NHL Minimum Totals Dashboard Generator - V3.1 Monte Carlo
==========================================================
Generates a web dashboard with Monte Carlo + Legacy tabs
matching the CBB and NBA dashboard style.

Features:
- Monte Carlo tab: V3.1 system with 96%+ threshold
- Legacy tab: Original scoring system
- Live picks display
- Performance tracking
"""

import pandas as pd
import json
import os
from datetime import datetime


def load_results_data():
    """Load results from tracker CSV"""
    try:
        df = pd.read_csv('nhl_system_results.csv')
        return df
    except FileNotFoundError:
        # Return empty dataframe with expected columns
        return pd.DataFrame(columns=[
            'date', 'game', 'minimum_total', 'actual_total', 
            'decision', 'hit_rate', 'flag_count', 'result', 'system'
        ])


def load_todays_picks():
    """Load today's picks from the decisions file"""
    today = datetime.now().strftime('%Y-%m-%d')
    decisions_dir = 'output_archive/decisions'
    
    # Find today's file
    if os.path.exists(decisions_dir):
        for filename in sorted(os.listdir(decisions_dir), reverse=True):
            if filename.startswith(today):
                df = pd.read_csv(os.path.join(decisions_dir, filename))
                return df
    
    # Return empty if not found
    return pd.DataFrame()


def generate_dashboard():
    """Generate the complete HTML dashboard"""
    
    # Load data
    results_df = load_results_data()
    todays_picks = load_todays_picks()
    
    # Separate Monte Carlo vs Legacy results
    if len(results_df) > 0 and 'system' in results_df.columns:
        mc_results = results_df[results_df['system'] == 'monte_carlo']
        legacy_results = results_df[results_df['system'] != 'monte_carlo']
    else:
        mc_results = pd.DataFrame()
        legacy_results = results_df
    
    # Monte Carlo stats
    mc_completed = mc_results[mc_results['result'].isin(['WIN', 'LOSS'])] if len(mc_results) > 0 else pd.DataFrame()
    mc_wins = len(mc_completed[mc_completed['result'] == 'WIN']) if len(mc_completed) > 0 else 0
    mc_losses = len(mc_completed[mc_completed['result'] == 'LOSS']) if len(mc_completed) > 0 else 0
    mc_pending = len(mc_results[mc_results['result'] == 'PENDING']) if len(mc_results) > 0 else 0
    mc_win_rate = (mc_wins / len(mc_completed) * 100) if len(mc_completed) > 0 else 0
    mc_avg_hit_rate = mc_results['hit_rate'].mean() if len(mc_results) > 0 and 'hit_rate' in mc_results.columns else 0
    
    # Legacy stats  
    legacy_completed = legacy_results[legacy_results['result'].isin(['WIN', 'LOSS'])] if len(legacy_results) > 0 else pd.DataFrame()
    legacy_wins = len(legacy_completed[legacy_completed['result'] == 'WIN']) if len(legacy_completed) > 0 else 0
    legacy_losses = len(legacy_completed[legacy_completed['result'] == 'LOSS']) if len(legacy_completed) > 0 else 0
    legacy_pending = len(legacy_results[legacy_results['result'] == 'PENDING']) if len(legacy_results) > 0 else 0
    legacy_win_rate = (legacy_wins / len(legacy_completed) * 100) if len(legacy_completed) > 0 else 0
    
    # Today's picks breakdown
    todays_yes = todays_picks[todays_picks['decision'] == 'YES'] if len(todays_picks) > 0 else pd.DataFrame()
    todays_maybe = todays_picks[todays_picks['decision'] == 'MAYBE'] if len(todays_picks) > 0 else pd.DataFrame()
    
    # Count 0-flag picks (cleanest bets)
    zero_flag_picks = todays_yes[todays_yes['flag_count'] == 0] if len(todays_yes) > 0 and 'flag_count' in todays_yes.columns else pd.DataFrame()
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NHL Minimum Totals V3.1</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: white;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        /* Header */
        .header {{
            text-align: center;
            padding: 30px 0;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
        }}
        
        .header .emoji {{
            font-size: 2.5rem;
        }}
        
        .version-badge {{
            background: linear-gradient(135deg, #10b981, #059669);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: bold;
            margin-left: 10px;
        }}
        
        .subtitle {{
            color: #94a3b8;
            font-size: 1rem;
            margin-top: 5px;
        }}
        
        .last-updated {{
            color: #64748b;
            font-size: 0.85rem;
            margin-top: 10px;
        }}
        
        /* Tab System */
        .tab-container {{
            display: flex;
            justify-content: center;
            gap: 10px;
            margin: 30px 0;
        }}
        
        .tab-btn {{
            padding: 12px 30px;
            border: none;
            border-radius: 25px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .tab-btn.mc {{
            background: linear-gradient(135deg, #10b981, #059669);
            color: white;
        }}
        
        .tab-btn.legacy {{
            background: rgba(255,255,255,0.1);
            color: #94a3b8;
            border: 2px solid rgba(255,255,255,0.2);
        }}
        
        .tab-btn.active {{
            transform: scale(1.05);
            box-shadow: 0 5px 20px rgba(16, 185, 129, 0.4);
        }}
        
        .tab-btn:not(.active):hover {{
            background: rgba(255,255,255,0.15);
            color: white;
        }}
        
        .tab-count {{
            background: rgba(0,0,0,0.3);
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.85rem;
        }}
        
        /* Stats Grid */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 25px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        
        .stat-label {{
            color: #94a3b8;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        
        .stat-value {{
            font-size: 2.5rem;
            font-weight: bold;
        }}
        
        .stat-value.green {{ color: #10b981; }}
        .stat-value.blue {{ color: #3b82f6; }}
        .stat-value.yellow {{ color: #f59e0b; }}
        .stat-value.red {{ color: #ef4444; }}
        
        /* Strict Mode Banner */
        .strict-banner {{
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(5, 150, 105, 0.2));
            border: 1px solid rgba(16, 185, 129, 0.5);
            border-radius: 12px;
            padding: 15px 25px;
            margin-bottom: 30px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .strict-banner .icon {{
            font-size: 1.5rem;
        }}
        
        .strict-banner .title {{
            color: #10b981;
            font-weight: bold;
            font-size: 1.1rem;
        }}
        
        .strict-banner .desc {{
            color: #94a3b8;
            font-size: 0.9rem;
        }}
        
        /* Refresh Button */
        .refresh-btn {{
            background: linear-gradient(135deg, #3b82f6, #2563eb);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 25px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 30px;
        }}
        
        .refresh-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(59, 130, 246, 0.4);
        }}
        
        /* Picks Section */
        .picks-section {{
            margin-bottom: 30px;
        }}
        
        .section-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        
        .section-header .icon {{
            font-size: 1.3rem;
        }}
        
        .section-header h2 {{
            font-size: 1.2rem;
            font-weight: 600;
        }}
        
        .section-header .count {{
            color: #94a3b8;
            font-size: 0.9rem;
        }}
        
        /* Game Cards */
        .game-card {{
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            border-left: 4px solid #10b981;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .game-card.maybe {{
            border-left-color: #f59e0b;
        }}
        
        .game-card.skip {{
            border-left-color: #ef4444;
            opacity: 0.7;
        }}
        
        .game-info h3 {{
            font-size: 1.1rem;
            margin-bottom: 5px;
        }}
        
        .game-details {{
            color: #94a3b8;
            font-size: 0.9rem;
        }}
        
        .game-stats {{
            text-align: right;
        }}
        
        .hit-rate {{
            font-size: 1.5rem;
            font-weight: bold;
            color: #10b981;
        }}
        
        .hit-rate.maybe {{
            color: #f59e0b;
        }}
        
        .flag-badge {{
            background: rgba(16, 185, 129, 0.2);
            color: #10b981;
            padding: 3px 12px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-top: 5px;
            display: inline-block;
        }}
        
        .flag-badge.warning {{
            background: rgba(245, 158, 11, 0.2);
            color: #f59e0b;
        }}
        
        /* Tab Content */
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        /* Results Table */
        .results-table {{
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            overflow: hidden;
            margin-top: 30px;
        }}
        
        .results-table table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        .results-table th {{
            background: rgba(0,0,0,0.3);
            padding: 15px;
            text-align: left;
            font-size: 0.85rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .results-table td {{
            padding: 15px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }}
        
        .results-table tr:hover {{
            background: rgba(255,255,255,0.03);
        }}
        
        .result-win {{
            color: #10b981;
            font-weight: bold;
        }}
        
        .result-loss {{
            color: #ef4444;
            font-weight: bold;
        }}
        
        .result-pending {{
            color: #f59e0b;
            font-weight: bold;
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            
            .header h1 {{
                font-size: 1.8rem;
            }}
            
            .game-card {{
                flex-direction: column;
                text-align: center;
            }}
            
            .game-stats {{
                text-align: center;
                margin-top: 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>
                <span class="emoji">🏒</span>
                NHL Minimum Totals
                <span class="version-badge">V3.1 • 100%</span>
            </h1>
            <p class="subtitle">Monte Carlo V3.1 • 7-0 backtest on 0-flag games</p>
            <p class="last-updated">Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <!-- Tab Buttons -->
        <div class="tab-container">
            <button class="tab-btn mc active" onclick="switchTab('mc')">
                🎲 Monte Carlo
                <span class="tab-count">{len(todays_yes)}</span>
            </button>
            <button class="tab-btn legacy" onclick="switchTab('legacy')">
                📊 Legacy
                <span class="tab-count">{legacy_wins + legacy_losses + legacy_pending}</span>
            </button>
        </div>
        
        <!-- Monte Carlo Tab -->
        <div id="mc-content" class="tab-content active">
            <!-- Stats Grid -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Record</div>
                    <div class="stat-value green">{mc_wins}-{mc_losses}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Win Rate</div>
                    <div class="stat-value blue">{mc_win_rate:.1f}%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">0-Flag Picks</div>
                    <div class="stat-value yellow">{len(zero_flag_picks)}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Avg MC Prob</div>
                    <div class="stat-value green">{mc_avg_hit_rate:.1f}%</div>
                </div>
            </div>
            
            <!-- Strict Mode Banner -->
            <div class="strict-banner">
                <span class="icon">✅</span>
                <div>
                    <div class="title">V3.1 STRICT MODE</div>
                    <div class="desc">Backtest: 7-0 (100%) • Only betting 0-flag games at 96%+ hit rate</div>
                </div>
            </div>
            
            <!-- Refresh Button -->
            <button class="refresh-btn" onclick="location.reload()">
                🔄 Refresh Data
            </button>
            
            <!-- YES Picks -->
            <div class="picks-section">
                <div class="section-header">
                    <span class="icon">🟢</span>
                    <h2>✅ BET THESE - Zero Flags ({len(zero_flag_picks)})</h2>
                    <span class="count">100% backtest win rate</span>
                </div>
"""
    
    # Add YES picks (0 flags only)
    if len(zero_flag_picks) > 0:
        for _, pick in zero_flag_picks.iterrows():
            html += f"""
                <div class="game-card">
                    <div class="game-info">
                        <h3>{pick['game']}</h3>
                        <div class="game-details">
                            Line: {pick['minimum_total']} • Expected: {pick.get('expected_total', 'N/A')} • Range: TBD
                        </div>
                    </div>
                    <div class="game-stats">
                        <div class="hit-rate">{pick['hit_rate']:.2f}%</div>
                        <div class="flag-badge">0 FLAGS</div>
                    </div>
                </div>
"""
    else:
        html += """
                <div class="game-card">
                    <div class="game-info">
                        <h3>No 0-flag picks today</h3>
                        <div class="game-details">All games have risk factors - check MAYBE section below</div>
                    </div>
                </div>
"""
    
    html += """
            </div>
            
            <!-- MAYBE Picks (Has Flags) -->
            <div class="picks-section">
                <div class="section-header">
                    <span class="icon">🟡</span>
                    <h2>⚠️ SKIP - Has Flags ({len_maybe})</h2>
                    <span class="count">Risk factors detected</span>
                </div>
""".replace('{len_maybe}', str(len(todays_maybe)))
    
    # Add MAYBE picks (top 5 by hit rate)
    if len(todays_maybe) > 0:
        top_maybes = todays_maybe.nlargest(5, 'hit_rate') if 'hit_rate' in todays_maybe.columns else todays_maybe.head(5)
        for _, pick in top_maybes.iterrows():
            flag_count = pick.get('flag_count', 0) if pd.notna(pick.get('flag_count', 0)) else 0
            flags_str = str(pick.get('flags', 'N/A')) if pd.notna(pick.get('flags', '')) else 'N/A'
            flags_display = flags_str[:50] if len(flags_str) > 50 else flags_str
            hit_rate_val = pick.get('hit_rate', 0) if pd.notna(pick.get('hit_rate', 0)) else 0
            html += f"""
                <div class="game-card maybe">
                    <div class="game-info">
                        <h3>{pick['game']}</h3>
                        <div class="game-details">
                            Line: {pick['minimum_total']} • Flags: {flags_display}...
                        </div>
                    </div>
                    <div class="game-stats">
                        <div class="hit-rate maybe">{hit_rate_val:.2f}%</div>
                        <div class="flag-badge warning">{int(flag_count)} FLAGS</div>
                    </div>
                </div>
"""
    
    html += """
            </div>
        </div>
        
        <!-- Legacy Tab -->
        <div id="legacy-content" class="tab-content">
            <!-- Legacy Stats Grid -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Record</div>
                    <div class="stat-value green">{legacy_wins}-{legacy_losses}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Win Rate</div>
                    <div class="stat-value blue">{legacy_win_rate:.1f}%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Pending</div>
                    <div class="stat-value yellow">{legacy_pending}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Total Picks</div>
                    <div class="stat-value green">{legacy_total}</div>
                </div>
            </div>
            
            <p style="color: #94a3b8; text-align: center; padding: 40px;">
                Legacy system uses the original 100-point scoring methodology.<br>
                V3.1 Monte Carlo is recommended for higher accuracy.
            </p>
        </div>
    </div>
    
    <script>
        function switchTab(tab) {{
            // Update buttons
            document.querySelectorAll('.tab-btn').forEach(btn => {{
                btn.classList.remove('active');
            }});
            
            // Update content
            document.querySelectorAll('.tab-content').forEach(content => {{
                content.classList.remove('active');
            }});
            
            if (tab === 'mc') {{
                document.querySelector('.tab-btn.mc').classList.add('active');
                document.getElementById('mc-content').classList.add('active');
            }} else {{
                document.querySelector('.tab-btn.legacy').classList.add('active');
                document.getElementById('legacy-content').classList.add('active');
            }}
        }}
    </script>
</body>
</html>
""".replace('{legacy_wins}', str(legacy_wins)).replace('{legacy_losses}', str(legacy_losses)).replace('{legacy_win_rate:.1f}', f'{legacy_win_rate:.1f}').replace('{legacy_pending}', str(legacy_pending)).replace('{legacy_total}', str(legacy_wins + legacy_losses + legacy_pending))
    
    return html


def main():
    """Generate and save the dashboard"""
    print("🏒 Generating NHL V3.1 Dashboard...")
    
    html = generate_dashboard()
    
    # Save to index.html for web deployment
    with open('index.html', 'w') as f:
        f.write(html)
    
    print("✅ Dashboard saved to index.html")
    print("   Push to GitHub to update live site")


if __name__ == "__main__":
    main()