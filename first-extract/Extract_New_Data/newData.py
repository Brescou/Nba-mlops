import os
import sys
import time

import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from NBADataExtractor import NBADataExtractor

from dict_endpoint import nba_endpoints_games, nba_endpoints_player, nba_endpoints_teams


def initialize_dataframe(file_path):
    df = pd.read_csv(file_path, dtype={'GAME_ID': str})
    df['processed'] = False
    df.to_csv(file_path, index=False)


def refresh():
    extractor = NBADataExtractor(
        nba_endpoints_games,
        season_start=2024,
        season_end=2025,
        output_dir="./first-extract/data/game/"
    )

    regular_season_path = "./first-extract/data/game/regular_season_game_logs_2024-25.csv"

    if not os.path.exists(regular_season_path):
        extractor.extract_seasons()
        initialize_dataframe(regular_season_path)

    extractor.update_processed_status("Regular Season")

    extractor.extract_all_play_by_play()

    extractor = NBADataExtractor(
        nba_endpoints_player,
        output_dir="./data/"
    )
    extractor.fetch_player_bios()
    extractor = NBADataExtractor(nba_endpoints_player, season_start=2024, season_end=2025)
    extractor.fetch_stats_for_multiple_seasons(
        endpoint="general",
        sub_endpoint="traditional",
        season_types=["Regular Season", "Playoffs"]
    )
    extractor.fetch_player_boxscore_for_multiple_seasons()
    extractor.change_season_type("Playoffs")
    extractor.fetch_player_boxscore_for_multiple_seasons()

    extractor_team = NBADataExtractor(nba_endpoints_teams, season_start=2024, season_end=2025)
    extractor_team.fetch_team_boxscore_for_multiple_seasons()
    extractor_team.change_season_type("Playoffs")
    time.sleep(2)
    extractor_team.fetch_team_boxscore_for_multiple_seasons()


    extractor.close_session()


if __name__ == "__main__":
    refresh()
