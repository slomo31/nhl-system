# 🛠️ NHL MINIMUM SYSTEM - INSTALLATION GUIDE

**Complete setup instructions from scratch**

---

## 📋 **PREREQUISITES**

- Python 3.8+ installed
- macOS, Linux, or Windows
- Internet connection
- Paid Odds API subscription (same key as NBA system)

---

## ⚡ **QUICK INSTALL**

### **1. Download & Extract**

```bash
# Navigate to where you want the project
cd ~/Documents

# Extract the ZIP file
unzip nhl_minimum_system.zip
cd nhl_minimum_system
```

### **2. Set Up Virtual Environment**

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### **3. Install Dependencies**

```bash
# Install all required packages
pip install -r requirements.txt
```

This will install:
- pandas
- numpy
- requests
- beautifulsoup4
- lxml
- and other dependencies

### **4. Verify Installation**

```bash
# Check Python version
python --version

# Check packages
pip list
```

---

## ⚙️ **CONFIGURATION**

### **Update API Key** (already configured)

Verify `config/api_config.py`:

```python
ODDS_API_KEY = "a03349ac7178eb60a825d19bd27014ce"
SPORT = "icehockey_nhl"
```

Your NBA API key works for NHL too!

---

## 🎯 **RUNNING THE SYSTEM**

### **Option 1: Daily Predictions (Live)**

```bash
# Run complete workflow for today's games
python master_workflow.py
```

This will:
1. ✅ Collect team stats
2. ✅ Collect goalie stats
3. ✅ Fetch today's games
4. ✅ Get minimum alternates
5. ✅ Check for elite goalies
6. ✅ Run predictions
7. ✅ Output YES/NO decisions with goalie flags
8. ✅ Save results to `output_archive/decisions/`

### **Option 2: Backtest (Validate System)**

```bash
# Test system against completed games
python run_backtest.py
```

This will:
1. ✅ Load all completed 2024-2025 games
2. ✅ Run predictions on each
3. ✅ Calculate accuracy
4. ✅ Validate 85%+ threshold
5. ✅ Analyze elite goalie impact
6. ✅ Save results to `output_archive/backtests/`

---

## 📂 **PROJECT STRUCTURE**

```
nhl_minimum_system/
├── venv/                    # Virtual environment (created by you)
├── config/                  # Configuration files
├── data_collection/         # Data scrapers
├── analyzers/              # Factor analyzers
├── core/                   # Main prediction engine
├── decision/               # YES/NO decision maker
├── backtesting/            # Backtest system
├── output/                 # Output generators
├── data/                   # Input data (auto-created)
├── output_archive/         # All results (auto-created)
│   ├── decisions/         # Daily decisions
│   └── backtests/         # Backtest results
├── master_workflow.py      # Main command (daily)
├── run_backtest.py         # Backtest command
└── requirements.txt        # Dependencies
```

---

## 🛠️ **TROUBLESHOOTING**

### **Issue: "python: command not found"**
```bash
# Try python3 instead
python3 -m venv venv
python3 master_workflow.py
```

### **Issue: "Module not found"**
```bash
# Ensure venv is activated (you should see (venv) in terminal)
# Then reinstall:
pip install -r requirements.txt
```

### **Issue: "API Error 401"**
- Check API key in `config/api_config.py`
- Verify paid plan at https://the-odds-api.com
- Check API quota

### **Issue: "No games found"**
- System only works on NHL game days (Oct-April)
- Check date (season is October to June)
- Verify time zone

### **Issue: "No starting goalie data"**
- Goalies announced ~2 hours before game
- Run system closer to game time
- Check NHL.com for official starters

---

## 📈 **WORKFLOW DIAGRAM**

```
1. MORNING (2-3 hours before games)
   ↓
2. Run: python master_workflow.py
   ↓
3. Review YES decisions
   ↓
4. Check for elite goalie flags (⚠️)
   ↓
5. Check DraftKings for exact lines
   ↓
6. Decide on flagged games (full bet / half bet / skip)
   ↓
7. Place bets (3% bankroll per game)
   ↓
8. EVENING (After Games)
   ↓
9. Track results (separate tracking for flagged games)
   ↓
10. Update betting log
   ↓
11. Calculate running win rate
   ↓
12. WEEKLY: python run_backtest.py (revalidate)
```

---

## 🎯 **BANKROLL MANAGEMENT**

### **Example with $1,000 Bankroll:**

YES bet: 3% = $30 per game

If 2 YES bets today:
- Total risk: $60
- Potential win at -800: ~$7.50
- One loss: -$30
- Net if 2-0: +$7.50
- Net if 1-1: -$22.50

**The key:** Your 85%+ accuracy means more 2-0 nights than 1-1.

**Elite Goalie Strategy:**
- Full bet (3%): High confidence, ignore flag
- Half bet (1.5%): Moderate confidence, respect flag
- Skip: Low confidence, elite goalie present

---

## ⚠️ **CRITICAL REMINDERS**

### **DO:**
✅ Run backtest first to validate  
✅ Respect all NO decisions  
✅ Bet exactly 3% per YES (or less for flagged)  
✅ Track elite goalie games separately  
✅ Revalidate weekly

### **DON'T:**
❌ Bet more than 3% per game  
❌ Chase losses  
❌ Ignore NO decisions  
❌ Skip the backtest  
❌ Ignore elite goalie flags entirely

---

## 🎉 **YOU'RE READY!**

### **Next Steps:**

1. ✅ Download the project folder
2. ✅ Set up venv
3. ✅ Install dependencies
4. ✅ Run backtest (validate 85%+)
5. ✅ Run daily workflow
6. ✅ Track elite goalie impact
7. ✅ Adjust strategy based on data
8. ✅ Profit responsibly

---

## 📞 **QUESTIONS?**

- Read `README.md` for full documentation
- Check `DAILY_WORKFLOW.md` for daily routine
- Review code comments for technical details

---

## 🏒 **GOOD LUCK!**

You now have a complete NHL betting system focused on **identifying the safest minimum alternate totals** while **flagging elite goalie risks**.

**Trust the process. Track the data. Learn and adjust.**

**Time to see if NHL can print like NBA! 🚀**

---

**Built:** November 2024  
**Season:** 2024-2025 NHL  
**Version:** 1.0  
**Status:** ✅ Complete & Ready
