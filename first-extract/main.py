# import pandas as pd
#
# df1 = pd.read_csv('data/game/playoffs_game_logs.csv', dtype={'GAME_ID': str})
# df2 = pd.read_csv('data/game/regular_season_game_logs.csv', dtype={'GAME_ID': str})
#
# if 'processed' not in df1.columns:
#     df1['processed'] = False
# else:
#     df1['processed'] = False
#
# if 'processed' not in df2.columns:
#     df2['processed'] = False
# else:
#     df2['processed'] = False
#
# df1.to_csv('data/game/playoffs_game_logs.csv', index=False)
# df2.to_csv('data/game/regular_season_game_logs.csv', index=False)

from NBADataExtractor import NBADataExtractor
from dict_endpoint import nba_endpoints_games

extractor = NBADataExtractor(
    nba_endpoints_games,
    season_start=1996,
    season_end=2023,
    delay=3,
    output_dir="./data/game/"
)

# extractor.extract_seasons()
# extractor.change_season_type("Playoffs")
# extractor.extract_seasons()

extractor.extract_all_play_by_play()
extractor.close_session()
