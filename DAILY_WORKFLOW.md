# 📅 NHL MINIMUM SYSTEM - DAILY WORKFLOW

**Your complete guide to running the system every day**

cd ~/Documents/nhl_minimum_system
source venv/bin/activate

# Update everything
python data_collection/nhl_stats_collector.py
python data_collection/goalie_stats_collector.py
python data_collection/game_results_collector.py

---

## ⏰ **WHEN TO RUN**

**Best time:** 2-3 hours before first game of the night

Example: If games start at 7pm ET, run between 4pm-5pm ET

**Why?** Starting goalies are typically announced 2-3 hours before puck drop.

---

## 📝 **DAILY ROUTINE (5-7 MINUTES)**

### **Step 1: Update Team & Goalie Stats (Weekly - Every Monday)**

```bash
# Navigate to project
cd nhl_minimum_system

# Activate environment
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows

# Update team stats
python data_collection/nhl_stats_collector.py

# Update goalie stats
python data_collection/goalie_stats_collector.py
```

**What this does:**
- Scrapes latest team stats from NHL API
- Updates goals per game, shots, defensive stats
- Collects goalie save percentages and GAA
- Saves to `data/nhl_team_stats_2024_2025.csv` and `data/nhl_goalie_stats_2024_2025.csv`

**When to run:** Monday mornings (once per week)

---

### **Step 2: Get Today's Picks**

```bash
# Run master workflow
python master_workflow.py
```

**What this does:**
1. ✅ Loads current team stats
2. ✅ Loads goalie stats
3. ✅ Collects completed games (for form/rest analysis)
4. ✅ Fetches today's games from Odds API
5. ✅ Gets minimum alternate totals
6. ✅ Checks for elite goalie performances
7. ✅ Runs predictions for each game
8. ✅ Makes YES/NO decisions with goalie flags
9. ✅ Saves results to `output_archive/decisions/`

**Output:** You'll see a summary like this:

```
✅ WORKFLOW COMPLETE!

📊 Ready to bet: 3 YES decisions (1 with elite goalie flag)
📁 Results saved to: output_archive/decisions/2024-11-11_17-30_decisions.csv

✅ YES BETS (85%+ confidence):

TOR @ BOS
  Minimum: Over 4.5 at -850
  Confidence: 88%
  ⚠️ ELITE GOALIE WARNING: Swayman (93.2% Sv%, 2.15 GAA)
  Reasoning: Elite offense | Fast pace | Strong buffer
  Action: BET IT (monitor goalie impact - consider half stake)

EDM @ VAN
  Minimum: Over 5.0 at -700
  Confidence: 91%
  ✅ No goalie concerns
  Reasoning: Both teams hot | Fast pace | Rested
  Action: BET IT (3% bankroll)

COL @ DAL
  Minimum: Over 5.5 at -600
  Confidence: 86%
  ✅ No goalie concerns
  Reasoning: Elite offense | Good buffer | Both rested
  Action: BET IT (3% bankroll)
```

---

### **Step 3: Review Your Picks**

Open the CSV file:

```bash
# Location
open output_archive/decisions/[TODAY'S DATE]_decisions.csv
```

**CSV Columns:**
- `game` - Teams playing
- `minimum_total` - The line you're betting
- `decision` - YES/NO/MAYBE
- `confidence` - System confidence %
- `elite_goalie_flag` - TRUE/FALSE
- `goalie_warning` - Description if flagged
- `action` - BET IT or SKIP
- `stake` - Recommended % of bankroll
- `reasoning` - Why this decision

**What to look for:**
- ✅ YES decisions with 85%+ confidence
- ⚠️ Elite goalie flags - decide your strategy
- ⚠️ MAYBE decisions (75-84%) - your choice
- ❌ NO decisions - never bet these

---

### **Step 4: Elite Goalie Decision**

**When you see a goalie flag:**

```
⚠️ ELITE GOALIE WARNING: Vasilevskiy (94.1% Sv%, 2.05 GAA)
```

**Your options:**

1. **Full Bet (3%)** - Trust the system, goalie can't stop everything
2. **Half Bet (1.5%)** - Respect the risk, reduce exposure
3. **Skip** - Too much uncertainty, wait for cleaner opportunities

**Track these separately!** You're building data on whether elite goalies really matter.

---

### **Step 5: Place Your Bets**

1. Open DraftKings
2. Navigate to NHL
3. Find "Alternate Totals"
4. Place bets on YES decisions
5. Stake based on your goalie flag strategy

**Example:**
- Bankroll: $1,000
- Per bet: $30 (3%)
- If 3 YES bets (1 flagged):
  - Game 1: $30 (no flag)
  - Game 2: $30 (no flag)
  - Game 3: $15 (elite goalie flag - half stake)
  - Total risk: $75

---

### **Step 6: Track Results (Next Day)**

After games finish, update your tracking:

```bash
# Collect yesterday's results
python data_collection/game_results_collector.py
```

**What this does:**
- Collects completed game scores from NHL API
- Updates `data/nhl_completed_games_2024_2025.csv`
- Used for form/rest analysis in future predictions

**Manual tracking (CRITICAL):**

Create a spreadsheet with TWO sections:

**Section 1: All Bets**
| Date | Game | Min Total | Pred | Actual | Result | P/L |
|------|------|-----------|------|--------|--------|-----|
| 11/11 | TOR@BOS | 4.5 | OVER | 5 | WIN | +$3.53 |
| 11/11 | EDM@VAN | 5.0 | OVER | 7 | WIN | +$4.29 |

**Section 2: Elite Goalie Flagged Games**
| Date | Game | Goalie | Sv% | Min | Actual | Result | Notes |
|------|------|--------|-----|-----|--------|--------|-------|
| 11/11 | TOR@BOS | Swayman | 93.2% | 4.5 | 5 | WIN | Half stake paid off |

**After 20+ flagged games, analyze:**
- Win rate on flagged vs non-flagged
- Should we skip elite goalies entirely?
- Or is the system robust enough?

---

## 📊 **WEEKLY VALIDATION (Every Monday)**

```bash
# Run backtest to revalidate system
python run_backtest.py
```

**What this does:**
- Tests system against all completed games
- Calculates current win rate
- Validates 85%+ threshold still holds
- Shows elite goalie impact on results

**Expected output:**

```
✅ SYSTEM VALIDATED!

Overall Win rate: 87.3% (exceeds 85% threshold)
Elite goalie flagged games: 81.2% win rate
Non-flagged games: 91.5% win rate

Analysis: Elite goalie flags do correlate with lower win rate.
Recommendation: Consider half-staking or skipping flagged games.
```

---

## 🔄 **COMPLETE WEEKLY SCHEDULE**

### **Monday Morning (15 minutes)**
```bash
# Update all data
python data_collection/nhl_stats_collector.py
python data_collection/goalie_stats_collector.py
python data_collection/game_results_collector.py
python run_backtest.py
```

### **Every Game Day (5-7 minutes)**
```bash
# 2-3 hours before first game
python master_workflow.py

# Review picks
# Decide on elite goalie flags
# Place bets
```

### **Next Morning (2 minutes)**
```bash
# Update results
python data_collection/game_results_collector.py

# Update tracking spreadsheet
```

---

## 📋 **CHECKING DATA FRESHNESS**

### **Team Stats Age**

```bash
# Check when team stats were last updated
ls -lh data/nhl_team_stats_2024_2025.csv
```

**If older than 7 days:** Run team stats collector

### **Goalie Stats Age**

```bash
# Check goalie stats freshness
ls -lh data/nhl_goalie_stats_2024_2025.csv
```

**If older than 7 days:** Run goalie stats collector

### **Completed Games Count**

```bash
# Check how many games you have
wc -l data/nhl_completed_games_2024_2025.csv
```

**Expected:** ~150+ games as of mid-November

---

## 📁 **FILE STRUCTURE & WHAT EACH FILE DOES**

```
data/
├── nhl_team_stats_2024_2025.csv         # Current season stats (update weekly)
├── nhl_goalie_stats_2024_2025.csv       # Goalie performance (update weekly)
├── nhl_completed_games_2024_2025.csv    # All finished games (update daily)
└── upcoming_games.csv                    # Today's games (auto-generated)

output_archive/
├── decisions/
│   └── 2024-11-11_17-30_decisions.csv   # Today's picks with goalie flags
└── backtests/
    └── 2024-11-11_10-00_backtest.csv    # Validation results
```

---

## 🚨 **TROUBLESHOOTING**

### **"No games found"**

**Causes:**
- No games today (off day)
- Running too early (lines not posted)
- API issue

**Solution:** Wait 2-3 hours, try again

---

### **"No starting goalie data"**

**Cause:** Goalies not yet announced

**Solution:**
1. Check NHL.com for official starters
2. Run system 2 hours before game
3. System will flag "Unknown goalie" if not confirmed

---

### **"API Error 401"**

**Cause:** API key issue

**Solution:**
1. Check `config/api_config.py`
2. Verify key at https://the-odds-api.com/account/
3. Ensure key has NHL access

---

### **"Elite goalie detected but system says YES"**

**This is correct!** System flags but doesn't skip. You decide.

**Action:**
1. Review the confidence level
2. Check the buffer (how far above minimum)
3. Decide: full bet, half bet, or skip
4. Track the result for future learning

---

## 📊 **WHAT TO EXPECT**

### **NHL Schedule:**

- **Weeknights:** 3-8 games
- **Weekends:** 6-12 games
- **Off days:** Mondays/Thursdays sometimes

### **Typical Opportunities:**

- **1-2 YES bets per night** on weeknights
- **2-4 YES bets per night** on weekends
- **Elite goalie flags:** ~20-30% of games

### **Win Rate Expectations:**

- **Overall:** 85-90%
- **Non-flagged:** 90-95%
- **Elite goalie flagged:** 75-85% (TBD from your data)

---

## 🎯 **KEY METRICS TO TRACK**

1. **Overall win rate**
2. **Flagged game win rate** (learn goalie impact)
3. **Non-flagged game win rate**
4. **ROI** (return on investment)
5. **False negative rate** (games you skipped that would've won)

---

## ✅ **SUCCESS CHECKLIST**

**Daily:**
- [ ] Run master_workflow.py 2-3 hours before games
- [ ] Review all YES decisions
- [ ] Evaluate elite goalie flags
- [ ] Place bets (3% or adjusted)
- [ ] Track results next day

**Weekly:**
- [ ] Update team stats (Monday)
- [ ] Update goalie stats (Monday)
- [ ] Run backtest validation
- [ ] Analyze elite goalie impact
- [ ] Adjust strategy if needed

**Monthly:**
- [ ] Review overall win rate (target: 85%+)
- [ ] Analyze goalie flag correlation
- [ ] Decide: keep flags, or auto-skip?
- [ ] Adjust confidence thresholds if needed

---

## 🏒 **YOU'RE READY!**

**Same discipline as NBA. Lower scoring. Goalie awareness.**

**Trust the process. Track the data. Learn and profit.**

---

**Built:** November 2024  
**Season:** 2024-2025 NHL  
**Version:** 1.0  
**Status:** ✅ Ready for Daily Use
