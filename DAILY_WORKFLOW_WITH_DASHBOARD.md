# 🏒 NHL MINIMUM SYSTEM - COMPLETE DAILY WORKFLOW (WITH WEB DASHBOARD)

**Your end-to-end guide with data collection, predictions, results tracking, and live dashboard updates**


# Morning - Update results
python nhl_results_tracker_v31.py
python nhl_dashboard_v31.py
git add . && git commit -m "Update" && git push

# Evening - Get picks
python master_workflow_v31.py
python nhl_dashboard_v31.py
git add . && git commit -m "Picks" && git push
---

## 📅 **WEEKLY SETUP (Monday Morning - 20 minutes)**

### **Run ALL data collectors to start fresh week:**

```bash
cd ~/Documents/nhl_minimum_system
source venv/bin/activate  # Mac/Linux

# 1. Update team stats
python data_collection/nhl_stats_collector.py

# 2. Update goalie stats  
python data_collection/goalie_stats_collector.py

# 3. Update completed games
python data_collection/game_results_collector.py

# 4. Update results and match to actual games
python update_results.py

# 5. Push to web dashboard
git add data/ nhl_system_results.csv
git commit -m "Weekly data update - Monday"
git push

git add . && git commit -m "Update" && git push origin main
```

**What this does:**
- ✅ Fresh team stats (GPG, pace, defense)
- ✅ Fresh goalie stats (save %, elite flags)
- ✅ All completed games (for form/rest analysis)
- ✅ Updates your 14-2 record
- ✅ **Pushes to live dashboard** 🌐

**Your dashboard updates automatically within 1-2 minutes!**

---

## 🎯 **DAILY WORKFLOW (Game Days - 7 minutes)**

### **STEP 1: Get Today's Picks (2-3 hours before games)**

```bash
cd ~/Documents/nhl_minimum_system
source venv/bin/activate

# Run master workflow to get picks
python master_workflow.py
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

📊 Ready to bet: 4 YES decisions
```

---

### **STEP 2: Place Your Bets on DraftKings**

1. Open DraftKings Sportsbook
2. Navigate to NHL → Alternate Totals
3. Find your picks and bet the minimums
4. Build your parlay (2-3 legs recommended)

**Example 3-leg parlay:**
- Washington @ Carolina: Over 3.5
- Dallas @ Ottawa: Over 3.5
- Winnipeg @ Vancouver: Over 3.5
- Combined odds: ~+170 odds
- Stake: $100 to win $170

---

## 🌅 **NEXT MORNING ROUTINE (10 minutes)**

### **STEP 1: Update Game Results**

```bash
cd ~/Documents/nhl_minimum_system
source venv/bin/activate

# Fetch last night's completed games
python data_collection/game_results_collector.py
```

This adds last night's results to your database.

---

### **STEP 2: Auto-Match Results**

```bash
# Automatically match predictions to actual results
python update_results.py
```

**What you'll see:**
```
📊 SYSTEM RECORD
✅ Wins: 15
❌ Losses: 2
⏳ Pending: 0

📈 Win Rate: 88.2% (15-2)

📅 LAST 10 COMPLETED GAMES:
✅ 2025-11-17 | New York Islanders @ Colorado Avalanche
   Line: 3.5 | Actual: 5.0 | Buffer: +1.5 | Conf: 65%
```

---

### **STEP 3: Push to Live Dashboard**

```bash
# Push updated results to web
git add nhl_system_results.csv data/
git commit -m "Daily update - $(date +%Y-%m-%d)"
git push
```

**Your live dashboard updates automatically!**

Check it at: `https://nhl-dashboard-XXXX.onrender.com`

---

## 🚀 **COMPLETE DAILY COMMAND SEQUENCE**

### **Copy/Paste This Every Morning:**

```bash
cd ~/Documents/nhl_minimum_system
source venv/bin/activate

# Update yesterday's results
python data_collection/game_results_collector.py
python update_results.py

# Push to web
git add nhl_system_results.csv data/
git commit -m "Daily update - $(date +%Y-%m-%d)"
git push

echo "✅ Dashboard updated! Check: https://YOUR-DASHBOARD-URL.onrender.com"
```

---

### **Copy/Paste This Every Evening (2-3 hours before games):**

```bash
cd ~/Documents/nhl_minimum_system
source venv/bin/activate

# Get today's picks
python master_workflow.py

# Review picks and place bets on DraftKings
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
│  4. python update_results.py                                │
│  5. git add data/ nhl_system_results.csv                   │
│  6. git commit -m "Weekly update"                           │
│  7. git push                                                 │
│                                                              │
│  Result: Fresh data + Live dashboard updated                │
└─────────────────────────────────────────────────────────────┘

                              ↓

┌─────────────────────────────────────────────────────────────┐
│            GAME DAY EVENING (2-3 hours before games)         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. python master_workflow.py                               │
│     → Get 3-4 YES picks at 87.5% win rate                   │
│                                                              │
│  2. Place bets on DraftKings                                │
│     → Build 2-3 leg parlay with picks                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘

                              ↓

┌─────────────────────────────────────────────────────────────┐
│                NEXT MORNING (After games finish)             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. python data_collection/game_results_collector.py        │
│     → Fetch last night's scores                             │
│                                                              │
│  2. python update_results.py                                │
│     → Auto-match predictions to results                      │
│     → Calculate new record (15-2, 88.2%)                     │
│                                                              │
│  3. git add nhl_system_results.csv data/                   │
│     git commit -m "Daily update"                            │
│     git push                                                 │
│     → Live dashboard updates automatically!                  │
│                                                              │
│  4. Check dashboard: https://YOUR-URL.onrender.com          │
│     → See updated record, recent games, ROI                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘

                              ↓

                    Repeat for next game day
```

---

## 🗓️ **WEEKLY SCHEDULE**

| Day | Morning (10 min) | Evening (5 min) | Dashboard |
|-----|------------------|-----------------|-----------|
| **Monday** | Full data update + git push | - | Auto-updates |
| **Tuesday** | Update results + git push | Get picks | Shows 14-2 |
| **Wednesday** | Update results + git push | Get picks | Shows 15-2 |
| **Thursday** | Update results + git push | Get picks | Shows 16-2 |
| **Friday** | Update results + git push | Get picks | Shows 17-2 |
| **Saturday** | Update results + git push | Get picks | Shows 18-2 |
| **Sunday** | Update results + git push | Get picks | Shows 19-2 |
| **Monday** | Full data update + git push | - | Shows 20-2 |

---

## 💾 **FILE STRUCTURE**

```
nhl_minimum_system/
├── master_workflow.py              # Get daily picks
├── update_results.py               # Auto-match results
├── app.py                          # Web dashboard
│
├── data/
│   ├── nhl_team_stats_2024_2025.csv
│   ├── nhl_goalie_stats_2024_2025.csv
│   ├── nhl_completed_games_2024_2025.csv
│   └── upcoming_games.csv
│
├── nhl_system_results.csv          # Your betting record (push this!)
│
└── output_archive/
    └── decisions/                   # All daily predictions
```

---

## ⚡ **QUICK REFERENCE COMMANDS**

### **Every Morning (Update Dashboard):**
```bash
python data_collection/game_results_collector.py
python update_results.py
git add nhl_system_results.csv data/
git commit -m "Daily update - $(date +%Y-%m-%d)"
git push
```

### **Every Evening (Get Picks):**
```bash
python master_workflow.py
```

### **Every Monday (Fresh Data):**
```bash
python data_collection/nhl_stats_collector.py
python data_collection/goalie_stats_collector.py
python data_collection/game_results_collector.py
python update_results.py
git add data/ nhl_system_results.csv
git commit -m "Weekly update - $(date +%Y-%m-%d)"
git push
```

---

## 🌐 **YOUR LIVE DASHBOARD**

**URL:** `https://nhl-dashboard-XXXX.onrender.com`

**Shows:**
- 📊 Current Record (14-2, 87.5%)
- 📈 Win Rate %
- 💰 ROI %
- ✅ Last 20 completed games
- ⏳ Pending games
- 🔥 Elite goalie flags

**Updates:** Automatically within 1-2 minutes of git push

---

## 🎯 **WHAT TO EXPECT**

### **Picks per night:** 3-4 YES bets
### **Current Record:** 14-2 (87.5%)
### **Parlay Strategy:**
- **2-leg:** 77% hit rate at ~-200 odds
- **3-leg:** 68% hit rate at ~+150 odds

### **Dashboard Updates:**
- **Monday:** Full weekly refresh
- **Daily:** New results added each morning
- **Live:** Always shows latest stats

---

## 🚨 **CRITICAL REMINDERS**

### **DO:**
✅ Update data every Monday (full refresh)
✅ Run update_results.py every morning
✅ **Git push after every update** (dashboard won't update without this!)
✅ Check dashboard before betting
✅ Trust the 65%+ threshold
✅ Track elite goalie games

### **DON'T:**
❌ Skip Monday data updates
❌ Forget to git push (dashboard won't update!)
❌ Bet without checking dashboard
❌ Chase losses
❌ Bet on NO decisions
❌ Ignore system warnings

---

## 📈 **TRACKING YOUR PROGRESS**

**Daily:**
1. Morning: Update results → Git push → Check dashboard
2. Evening: Get picks → Place bets
3. Monitor: Dashboard shows live stats

**Weekly:**
1. Monday: Full data refresh → Git push
2. Review: Check dashboard for week's performance
3. Adjust: Fine-tune if needed

**Monthly:**
1. Total profit/loss (shown on dashboard)
2. Win rate trend (target: 85%+)
3. ROI (target: 15%+)

---

## 🆘 **TROUBLESHOOTING**

### **"Dashboard not updating"**
→ Did you git push? Run: `git push`

### **"No YES bets today"**
→ Normal! Some nights have weak matchups

### **"API Error"**
→ Check internet, verify API key

### **"Results not matching"**
→ Run: `python update_results.py` again

### **"Dashboard shows old data"**
→ Wait 2 minutes after git push, then refresh

---

## 🎉 **YOU'RE ALL SET!**

Your complete system includes:
- ✅ Data collection (weekly)
- ✅ Predictions (daily)
- ✅ Auto-results matching (automated)
- ✅ **Live web dashboard** (automatic updates)
- ✅ Git workflow (push to deploy)

**Current Status:**
- **Record:** 14-2 (87.5%)
- **Dashboard:** Live at your Render URL
- **Updates:** Automatic via git push

---

## 🚀 **BOOKMARK THESE:**

1. **Dashboard:** https://YOUR-DASHBOARD-URL.onrender.com
2. **GitHub Repo:** https://github.com/slomo31/nhl-system
3. **Render Dashboard:** https://dashboard.render.com

---

**Built:** November 2024  
**Season:** 2024-2025 NHL  
**System:** Minimum Alternate Totals  
**Record:** 14-2 (87.5%)  
**Dashboard:** ✅ Live  
**Status:** 🚀 Fully Operational

**LET'S KEEP CRUSHING IT! 🏒💰**
