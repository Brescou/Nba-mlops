import os
import time

import pandas as pd

from NBADataExtractor import NBADataExtractor
from dict_endpoint import nba_endpoints_games, nba_endpoints_player, nba_endpoints_teams


def initialize_dataframe(file_path):
    df = pd.read_csv(file_path, dtype={'GAME_ID': str})
    df['processed'] = False
    df.to_csv(file_path, index=False)


def main():
    extractor = NBADataExtractor(
        nba_endpoints_games,
        season_start=2024,
        season_end=2025,
        output_dir="./data/game/"
    )

    regular_season_path = "./data/game/regular_season_game_logs.csv"
    playoffs_path = "./data/game/playoffs_game_logs.csv"

    if not os.path.exists(regular_season_path) and not os.path.exists(playoffs_path):
        extractor.extract_seasons()
        # extractor.change_season_type("Playoffs")
        # extractor.extract_seasons()
        # initialize_dataframe(playoffs_path)
        initialize_dataframe(regular_season_path)

    # extractor.update_processed_status("Regular Season")
    # extractor.update_processed_status("Playoffs")

    # extractor.extract_all_play_by_play()

    # extractor = NBADataExtractor(
    #     nba_endpoints_player,
    #     output_dir="./data/"
    # )
    # extractor.fetch_player_bios()
    # extractor = NBADataExtractor(nba_endpoints_player, season_start=2020, season_end=2023)
    # extractor.fetch_stats_for_multiple_seasons(
    #     endpoint="general",
    #     sub_endpoint="traditional",
    #     season_types=["Regular Season", "Playoffs"]
    # )
    # extractor.fetch_player_boxscore_for_multiple_seasons()
    # extractor.change_season_type("Playoffs")
    # extractor.fetch_player_boxscore_for_multiple_seasons()

    # extractor_team = NBADataExtractor(nba_endpoints_teams, season_start=2022, season_end=2024)
    # # extractor_team.fetch_team_boxscore_for_multiple_seasons()
    # extractor_team.change_season_type("Playoffs")
    # time.sleep(2)
    # extractor_team.fetch_team_boxscore_for_multiple_seasons()


    extractor.close_session()


if __name__ == "__main__":
    main()
