import os

from NBADataExtractor import NBADataExtractor
from dict_endpoint import nba_endpoints_player, nba_endpoints_teams, nba_endpoints_lineups

if not os.path.exists("./data"):
    os.makedirs("data")

seasons = [f"{year}-{year + 1}" for year in range(2000, 2024)]

nba_endpoints = {
    "player": nba_endpoints_player,
    "teams": nba_endpoints_teams,
    "lineups": nba_endpoints_lineups
}

extractor = NBADataExtractor(nba_endpoints, delay=1)
