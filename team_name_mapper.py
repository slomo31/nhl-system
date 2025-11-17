"""
Team Name Mapper
================
Converts full team names from Odds API to NHL abbreviations
"""

# Full mapping of Odds API names to NHL abbreviations
TEAM_NAME_MAP = {
    # Atlantic Division
    "Boston Bruins": "BOS",
    "Buffalo Sabres": "BUF",
    "Detroit Red Wings": "DET",
    "Florida Panthers": "FLA",
    "Montréal Canadiens": "MTL",
    "Montreal Canadiens": "MTL",  # Handle both spellings
    "Ottawa Senators": "OTT",
    "Tampa Bay Lightning": "TBL",
    "Toronto Maple Leafs": "TOR",
    
    # Metropolitan Division
    "Carolina Hurricanes": "CAR",
    "Columbus Blue Jackets": "CBJ",
    "New Jersey Devils": "NJD",
    "New York Islanders": "NYI",
    "New York Rangers": "NYR",
    "Philadelphia Flyers": "PHI",
    "Pittsburgh Penguins": "PIT",
    "Washington Capitals": "WSH",
    
    # Central Division
    "Arizona Coyotes": "ARI",
    "Utah Hockey Club": "UTA",
    "Utah Mammoth": "UTA",  # Handle alternate names
    "Chicago Blackhawks": "CHI",
    "Colorado Avalanche": "COL",
    "Dallas Stars": "DAL",
    "Minnesota Wild": "MIN",
    "Nashville Predators": "NSH",
    "St Louis Blues": "STL",
    "St. Louis Blues": "STL",  # Handle both spellings
    "Winnipeg Jets": "WPG",
    
    # Pacific Division
    "Anaheim Ducks": "ANA",
    "Calgary Flames": "CGY",
    "Edmonton Oilers": "EDM",
    "Los Angeles Kings": "LAK",
    "San Jose Sharks": "SJS",
    "Seattle Kraken": "SEA",
    "Vancouver Canucks": "VAN",
    "Vegas Golden Knights": "VGK"
}


def map_team_name(full_name):
    """
    Convert full team name to abbreviation
    
    Args:
        full_name: Full team name from Odds API
        
    Returns:
        3-letter abbreviation, or original name if not found
    """
    return TEAM_NAME_MAP.get(full_name, full_name)


def map_team_names_in_df(df, away_col='away_team', home_col='home_team'):
    """
    Map team names in a DataFrame
    
    Args:
        df: DataFrame with team name columns
        away_col: Name of away team column
        home_col: Name of home team column
        
    Returns:
        DataFrame with mapped team names
    """
    df = df.copy()
    df[away_col] = df[away_col].map(map_team_name)
    df[home_col] = df[home_col].map(map_team_name)
    return df