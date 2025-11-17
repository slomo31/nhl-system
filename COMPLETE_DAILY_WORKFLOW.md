# 🏒 NHL MINIMUM SYSTEM - COMPLETE DAILY WORKFLOW

**Your end-to-end guide with data collection, predictions, and results tracking**

---

## 📅 **WEEKLY SETUP (Monday Morning - 15 minutes)**

### **Run ALL data collectors to start fresh week:**

```bash
cd ~/Documents/nhl_minimum_system
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows

# Update team stats
python data_collection/nhl_stats_collector.py

# Update goalie stats  
python data_collection/goalie_stats_collector.py

# Update completed games
python data_collection/game_results_collector.py
```

**What this does:**
- ✅ Fresh team stats (GPG, pace, defense)
- ✅ Fresh goalie stats (save %, elite flags)
- ✅ All completed games (for form/rest analysis)

**Output:**
```
✅ Loaded 32 teams
✅ Loaded 42 goalies (3 elite hot)
✅ Loaded 1762+ completed games
```

---

## 🎯 **DAILY WORKFLOW (Game Days - 5-10 minutes)**

### **STEP 1: Get Today's Picks (2-3 hours before games)**

```bash
cd ~/Documents/nhl_minimum_system
source venv/bin/activate

# Run master workflow
python master_workflow.py

# Log picks for tracking
python auto_bet_logger.py log
```

**What you'll see:**
```
✅ YES BETS (65%+ confidence):

Washington Capitals @ Carolina Hurricanes
  Minimum: Over 3.5 at -825
  Confidence: 73%
  Action: BET IT

Dallas Stars @ Ottawa Senators
  Minimum: Over 3.5 at -725
  Confidence: 68%
  Action: BET IT

Anaheim Ducks @ Colorado Avalanche
  Minimum: Over 3.5 at -1600
  Confidence: 68%
  Action: BET IT

Winnipeg Jets @ Vancouver Canucks
  Minimum: Over 3.5 at -775
  Confidence: 65%
  Action: BET IT

📊 Ready to bet: 4 YES decisions
```

---

### **STEP 2: Log Your Bets**

```bash
# Log picks for tracking
python auto_bet_logger.py log

# Update your bet results
python auto_bet_logger.py update

# View current stats
python auto_bet_logger.py stats
```

**Interactive prompts:**
```
📝 LOGGING TODAY'S PICKS

🎯 4 YES picks found:
   Washington @ Carolina (73%)
   Dallas @ Ottawa (68%)
   Anaheim @ Colorado (68%)
   Winnipeg @ Vancouver (65%)

How are you betting these?
  1. Single bets
  2. One 2-leg parlay
  3. One 3-leg parlay
  4. One 4-leg parlay
  5. Multiple parlays (custom)
  6. Skip logging

Choice (1-6): 3

Stake per bet (default $30): 100

✅ Logged 1 bet(s)
   Total at risk: $100.00
```

---

### **STEP 3: Place Your Bets on DraftKings**

1. Open DraftKings Sportsbook
2. Navigate to NHL → Alternate Totals
3. Find your picks and bet the minimums
4. Build your parlay (if applicable)

**Example 3-leg parlay:**
- Washington @ Carolina: Over 3.5
- Dallas @ Ottawa: Over 3.5
- Winnipeg @ Vancouver: Over 3.5
- Combined odds: ~+150 to +200

---

## 🌅 **NEXT MORNING ROUTINE (5 minutes)**

### **STEP 1: Update Game Results**

```bash
# Optional: Update completed games for better form analysis
python data_collection/game_results_collector.py
```

This adds last night's results to your database for future predictions.

---

### **STEP 2: Log Your Results**

```bash
# Update your bet results
python auto_bet_logger.py update
```

**Interactive prompts:**
```
📊 UPDATE PENDING RESULTS

3 pending bets:

1. 2024-11-11 | 3-leg parlay
   Bet: Over 3.5 | Stake: $100.00

Update all? (y/n): y

3-leg parlay:
  Washington @ Carolina - Actual total: 7
  Dallas @ Ottawa - Actual total: 5
  Winnipeg @ Vancouver - Actual total: 6
  
  ✅ WON | +$170.00

✅ Updated results saved!
```

---

### **STEP 3: Check Your Performance**

```bash
# View current stats
python auto_bet_logger.py stats
```

**Output:**
```
================================================================================
📊 SYSTEM PERFORMANCE
================================================================================

📈 Overall Record:
   Total bets: 12
   Record: 11-1
   Win rate: 91.7%
   Total staked: $1,200.00
   Total profit: +$385.50
   ROI: +32.1%

📅 Last 10 Bets:
   ✅ 2024-11-11 | 3-leg parlay              | +$170.00
   ✅ 2024-11-10 | 2-leg parlay              | + $52.00
   ✅ 2024-11-09 | WSH @ CAR                 | +  $3.64
   ✅ 2024-11-08 | 3-leg parlay              | +$180.00
   ❌ 2024-11-07 | TOR @ MTL                 | - $30.00
   ✅ 2024-11-06 | 2-leg parlay              | + $48.00
   ...

================================================================================
```

---

## 📊 **COMPLETE WORKFLOW DIAGRAM**

```
┌─────────────────────────────────────────────────────────────┐
│                     MONDAY (WEEKLY RESET)                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. python data_collection/nhl_stats_collector.py          │
│  2. python data_collection/goalie_stats_collector.py       │
│  3. python data_collection/game_results_collector.py       │
│                                                              │
│  Result: Fresh data for the week                            │
└─────────────────────────────────────────────────────────────┘

                              ↓

┌─────────────────────────────────────────────────────────────┐
│               GAME DAY (2-3 hours before games)              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. python master_workflow.py                               │
│     → Get 3-4 YES picks at 87.8% win rate                   │
│                                                              │
│  2. python auto_bet_logger.py log                           │
│     → Log picks (single/parlay)                             │
│     → Choose stake amount                                    │
│                                                              │
│  3. Place bets on DraftKings                                │
│     → Build parlay with picks                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘

                              ↓

┌─────────────────────────────────────────────────────────────┐
│                NEXT MORNING (After games)                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. python auto_bet_logger.py update                        │
│     → Enter actual scores                                    │
│     → Calculate profit/loss                                  │
│                                                              │
│  2. python auto_bet_logger.py stats                         │
│     → Check win rate                                         │
│     → Track ROI                                              │
│                                                              │
│  3. (Optional) python data_collection/                      │
│     game_results_collector.py                               │
│     → Update for better predictions                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘

                              ↓

                    Repeat for next game day
```

---

## 🗓️ **WEEKLY SCHEDULE**

| Day | Morning | Afternoon (Game Day) | Next Morning |
|-----|---------|---------------------|--------------|
| **Monday** | Run all 3 data collectors (15 min) | - | - |
| **Tuesday** | - | master_workflow → log → bet | update → stats |
| **Wednesday** | - | master_workflow → log → bet | update → stats |
| **Thursday** | - | master_workflow → log → bet | update → stats |
| **Friday** | - | master_workflow → log → bet | update → stats |
| **Saturday** | - | master_workflow → log → bet | update → stats |
| **Sunday** | - | master_workflow → log → bet | update → stats |
| **Monday** | Run all 3 data collectors (15 min) | - | - |

---

## 💾 **FILE STRUCTURE**

```
nhl_minimum_system/
├── master_workflow.py              # Main daily command
├── auto_bet_logger.py              # Results tracker
│
├── data_collection/
│   ├── nhl_stats_collector.py      # Team stats (weekly)
│   ├── goalie_stats_collector.py   # Goalie stats (weekly)
│   └── game_results_collector.py   # Completed games (weekly)
│
├── data/
│   ├── nhl_team_stats_2024_2025.csv
│   ├── nhl_goalie_stats_2024_2025.csv
│   ├── nhl_completed_games_2024_2025.csv
│   ├── upcoming_games.csv           # Today's games (auto-generated)
│   └── betting_results.csv          # Your betting record
│
└── output_archive/
    └── decisions/                   # All daily predictions saved
```

---

## ⚡ **QUICK REFERENCE COMMANDS**

### **Weekly Reset (Mondays):**
```bash
python data_collection/nhl_stats_collector.py
python data_collection/goalie_stats_collector.py
python data_collection/game_results_collector.py
```

### **Daily Betting (Game Days):**
```bash
python master_workflow.py           # Get picks
python auto_bet_logger.py log       # Log bets
```

### **Results Tracking (Next Morning):**
```bash
python auto_bet_logger.py update    # Enter results
python auto_bet_logger.py stats     # Check performance
```

python track_nhl_minimum_results.py

python update_results.py

python generate_nhl_dashboard.py

open nhl_min_total_dashboard.html

cd ~/Documents/nhl_minimum_system

# Step 1: Get latest completed games (includes yesterday)
python data_collection/game_results_collector.py

# Step 2: Auto-match results
python update_results.py

# Step 3: Generate dashboard
python generate_nhl_dashboard.py

# Step 4: View
open nhl_min_total_dashboard.html



---

## 🎯 **WHAT TO EXPECT**

### **Picks per night:** 3-4 YES bets
### **Win rate:** 87.8% (based on backtest)
### **Parlay strategy:**
- **2-leg:** 77% hit rate at ~-200 odds
- **3-leg:** 68% hit rate at ~+150 odds

### **Monthly Performance (Example):**
- 60 total bets (20 game nights × 3 picks)
- 53 wins, 7 losses
- Win rate: 88.3%
- ROI: ~25-30%

---

## 🚨 **CRITICAL REMINDERS**

### **DO:**
✅ Update data every Monday
✅ Run workflow 2-3 hours before games
✅ Log every bet immediately
✅ Update results next morning
✅ Check stats weekly
✅ Stick to 3-5% stake per bet
✅ Trust the 65%+ threshold

### **DON'T:**
❌ Skip Monday data updates
❌ Bet without logging
❌ Chase losses
❌ Increase stakes after losses
❌ Lower threshold below 65%
❌ Bet on NO decisions
❌ Ignore elite goalie flags (track separately!)

---

## 📈 **TRACKING METRICS**

**Weekly Check (Every Monday after data update):**
1. Current win rate (target: 85%+)
2. ROI (target: 15%+)
3. Elite goalie impact
4. Parlay vs single performance
5. Adjust if needed

**Monthly Review:**
1. Total profit/loss
2. Best performing bet types
3. Confidence level accuracy
4. System improvements needed

---

## 🆘 **TROUBLESHOOTING**

### **"No YES bets today"**
- Normal! Some nights have weak matchups
- Don't force bets
- Wait for next game day

### **"API Error"**
- Check internet connection
- Verify API key in config/api_config.py
- Check requests remaining

### **"Missing data files"**
- Run Monday data collectors
- Check data/ directory exists
- Re-run specific collector

### **"Bet logging failed"**
- Make sure auto_bet_logger.py is in project root
- Check data/ directory exists
- Try logging manually

---

## 🎉 **YOU'RE ALL SET!**

Your complete system includes:
- ✅ Data collection (weekly)
- ✅ Predictions (daily)
- ✅ Bet logging (automatic)
- ✅ Results tracking (comprehensive)
- ✅ Performance stats (real-time)

**Everything you need to:**
1. Get reliable picks
2. Track your bets
3. Measure profitability
4. Improve over time

---

**Built:** November 2024  
**Season:** 2024-2025 NHL  
**System:** Minimum Alternate Totals  
**Target:** 87.8% win rate, 3-4 picks per night  
**Status:** ✅ Complete & Ready to Profit

**GOOD LUCK! 🏒💰**
