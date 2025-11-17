"""
API Configuration
=================
Settings for The Odds API and NHL API
"""

# ========================
# ODDS API (Paid Plan)
# ========================
ODDS_API_KEY = "a03349ac7178eb60a825d19bd27014ce"

# API settings
BASE_URL = "https://api.the-odds-api.com/v4"
SPORT = "icehockey_nhl"
BOOKMAKER = "draftkings"  # Focus on DraftKings only
REGION = "us"
MARKET = "alternate_totals"
ODDS_FORMAT = "american"

# Rate limiting (be nice to API)
REQUESTS_PER_SECOND = 1
API_TIMEOUT = 10  # seconds

# ========================
# NHL API (Free)
# ========================
NHL_API_BASE = "https://api-web.nhle.com/v1"
NHL_STATS_BASE = "https://api.nhle.com/stats/rest/en"

# Hockey Reference (backup for stats scraping)
HOCKEY_REF_BASE_URL = "https://www.hockey-reference.com"
