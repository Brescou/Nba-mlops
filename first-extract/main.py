from NBADataExtractor import NBADataExtractor
from dict_endpoint import nba_endpoints_games

extractor = NBADataExtractor(
    nba_endpoints_games,
    season_start=1996,
    season_end=2023,
    delay=2,
    output_dir="./data/game/"
)
extractor.extract_seasons()
extractor.change_season_type("Playoffs")
extractor.extract_seasons()
extractor.close_session()
