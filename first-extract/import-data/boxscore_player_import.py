import pandas as pd
import logging
from pathlib import Path
import os
import sys
from tqdm import tqdm

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
nba_mlops_root = os.path.join(project_root, "Nba-Mlops")
sys.path.append(nba_mlops_root)

try:
    from db.DB import DB
except ImportError as e:
    print(f"Error importing DB: {e}")
    print(f"Looking for DB.py in: {os.path.join(nba_mlops_root, 'db')}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BoxscorePlayerImporter:
    def __init__(self, db):
        self.db = db
        self.data_dir = Path(os.path.dirname(os.path.dirname(__file__))) / "data" / "player" / "boxscores"

    def get_missing_games(self):
        query = """
            SELECT DISTINCT pb.game_id, pb.is_playoff 
            FROM player_boxscore pb
            LEFT JOIN player_boxscore_advanced pba 
            ON pb.boxscore_id = pba.boxscore_id
            WHERE pba.boxscore_id IS NULL
            AND pb.season_year = '2023-24'
            ORDER BY pb.game_id;
        """
        return self.db.fetch_data(query)

    def process_advanced_stats(self, game_id, is_playoff, season_year):
        try:
            game_type = "playoffs" if is_playoff else "regular_season"
            file_path = self.data_dir / f"{season_year}_{game_type}_advanced.csv"
            
            if not file_path.exists():
                return None

            df = pd.read_csv(file_path, dtype={'GAME_ID': str, 'PLAYER_ID': str})
            df = df[df['GAME_ID'] == game_id]
            
            if df.empty:
                return None

            df['boxscore_id'] = df['PLAYER_ID'].astype(str) + '-' + df['GAME_ID'].astype(str)
            
            columns_mapping = {
                'E_OFF_RATING': 'e_off_rating',
                'OFF_RATING': 'off_rating',
                'sp_work_OFF_RATING': 'sp_work_off_rating',
                'E_DEF_RATING': 'e_def_rating',
                'DEF_RATING': 'def_rating',
                'sp_work_DEF_RATING': 'sp_work_def_rating',
                'E_NET_RATING': 'e_net_rating',
                'NET_RATING': 'net_rating',
                'sp_work_NET_RATING': 'sp_work_net_rating',
                'AST_PCT': 'ast_pct',
                'AST_TO': 'ast_to',
                'AST_RATIO': 'ast_ratio',
                'OREB_PCT': 'oreb_pct',
                'DREB_PCT': 'dreb_pct',
                'REB_PCT': 'reb_pct',
                'TM_TOV_PCT': 'tm_tov_pct',
                'E_TOV_PCT': 'e_tov_pct',
                'EFG_PCT': 'efg_pct',
                'TS_PCT': 'ts_pct',
                'USG_PCT': 'usg_pct',
                'PACE': 'pace',
                'PIE': 'pie'
            }
            
            df = df[['boxscore_id'] + list(columns_mapping.keys())]
            df.columns = ['boxscore_id'] + list(columns_mapping.values())

            return df

        except Exception as e:
            logger.error(f"Error processing advanced stats for game {game_id}: {str(e)}")
            return None

    def insert_advanced_stats(self, advanced_stats):
        if advanced_stats is None or advanced_stats.empty:
            return False

        try:
            numeric_columns = ['e_off_rating', 'off_rating', 'sp_work_off_rating', 
                             'e_def_rating', 'def_rating', 'sp_work_def_rating',
                             'e_net_rating', 'net_rating', 'sp_work_net_rating',
                             'ast_pct', 'ast_to', 'ast_ratio', 'oreb_pct', 'dreb_pct',
                             'reb_pct', 'tm_tov_pct', 'e_tov_pct', 'efg_pct',
                             'ts_pct', 'usg_pct', 'pace', 'pie']
            
            for col in numeric_columns:
                if col in advanced_stats.columns:
                    advanced_stats[col] = advanced_stats[col].round(4)
                    advanced_stats[col] = advanced_stats[col].clip(-999.9999, 999.9999)

            columns = advanced_stats.columns.tolist()
            data = [tuple(row) for row in advanced_stats.values]
            
            self.db.insert_bulk_data(
                table='player_boxscore_advanced',
                columns=columns,
                data=data
            )
            return True
            
        except Exception as e:
            tqdm.write(f"Error inserting data: {str(e)}")
            return False

    def has_missing_data_for_season(self, season_year):
        query = f"""
            SELECT COUNT(DISTINCT pb.game_id) 
            FROM player_boxscore pb
            LEFT JOIN player_boxscore_advanced pba 
            ON pb.boxscore_id = pba.boxscore_id
            WHERE pba.boxscore_id IS NULL
            AND pb.season_year = '{season_year}';
        """
        count = self.db.fetch_data(query)[0][0]
        return count > 0

    def run_import(self):
        self.db.connect()
        try:
            seasons = range(2015, 2025)
            with tqdm(seasons, desc="Processing seasons", position=0, dynamic_ncols=True) as season_bar:
                for season_start in season_bar:
                    season_year = f"{season_start}-{str(season_start + 1)[-2:]}"
                    
                    if not self.has_missing_data_for_season(season_year):
                        tqdm.write(f"No missing data for season {season_year}")
                        continue
                        
                    missing_games = self.get_missing_games_for_season(season_year)
                    tqdm.write(f"Processing {len(missing_games)} games for {season_year}")

                    with tqdm(missing_games, desc=f"Games for {season_year}", leave=False, position=1, dynamic_ncols=True) as game_bar:
                        for game_id, is_playoff in game_bar:
                            advanced_stats = self.process_advanced_stats(game_id, is_playoff, season_year)
                            if advanced_stats is not None:
                                if self.insert_advanced_stats(advanced_stats):
                                    tqdm.write(f"Imported game {game_id}")
                                else:
                                    tqdm.write(f"Failed to import game {game_id}")
        finally:
            self.db.close()

    def get_missing_games_for_season(self, season_year):
        query = f"""
            SELECT DISTINCT pb.game_id, pb.is_playoff 
            FROM player_boxscore pb
            LEFT JOIN player_boxscore_advanced pba 
            ON pb.boxscore_id = pba.boxscore_id
            WHERE pba.boxscore_id IS NULL
            AND pb.season_year = '{season_year}'
            ORDER BY pb.game_id;
        """
        return self.db.fetch_data(query)

if __name__ == "__main__":
    db = DB()
    db.connect()
    importer = BoxscorePlayerImporter(db)
    importer.run_import()
    db.close()