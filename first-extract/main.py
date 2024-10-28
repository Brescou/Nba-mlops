import os

import pandas as pd

from NBADataExtractor import NBADataExtractor
from dict_endpoint import nba_endpoints_games


def initialize_dataframe(file_path):
    df = pd.read_csv(file_path, dtype={'GAME_ID': str})
    df['processed'] = False
    df.to_csv(file_path, index=False)


def main():
    extractor = NBADataExtractor(
        nba_endpoints_games,
        season_start=1996,
        season_end=2023,
        output_dir="./data/game/"
    )

    regular_season_path = "./data/game/regular_season_game_logs.csv"
    playoffs_path = "./data/game/playoffs_game_logs.csv"

    # if not os.path.exists(regular_season_path) and not os.path.exists(playoffs_path):
    #     extractor.extract_seasons()
    #     extractor.change_season_type("Playoffs")
    #     extractor.extract_seasons()
    #     initialize_dataframe(playoffs_path)
    #     initialize_dataframe(regular_season_path)

    extractor.extract_all_play_by_play()
    extractor.close_session()


if __name__ == "__main__":
    main()
