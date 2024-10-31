import csv
import logging
import os
import sys
import time

import pandas as pd
import requests
from numpy.distutils.conv_template import header
from tqdm import tqdm

from params import NBAParams

logging.basicConfig(level=logging.INFO)


class NBADataExtractor:

    def __init__(self, endpoints, season_start=1996, season_end=None,
                 delay=None, output_dir="./data/game/"):
        self.endpoints = endpoints
        self.params = NBAParams()
        self.delay = delay if delay else self.params.DELAY
        self.session = requests.Session()
        self.session.headers.update(self.params.HEADERS)
        self.season_start = season_start
        self.season_end = season_end if season_end else season_start
        self.output_dir = output_dir
        self.season_type = "Regular Season"
        self.timeout = self.params.TIMEOUT_REQUEST

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def change_season_type(self, season_type):
        if season_type not in ["Regular Season", "Playoffs"]:
            raise ValueError("Invalid season type.'Regular Season' or 'Playoffs'.")
        self.season_type = season_type
        print(f"Season type changed to {self.season_type}")

    def fetch_data(self, endpoint, params):
        url = NBAParams.build_url(self.endpoints[endpoint])
        response = None
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            logging.error(f"Timeout occurred for GameID {params['GameID']}. Terminating program.")
            sys.exit(1)

        except requests.exceptions.HTTPError as e:
            if response.status_code == 503:
                logging.error(f"503 Server Error for GameID {params['GameID']}. Terminating program.")
                sys.exit(1)
            else:
                logging.error(f"HTTP Error occurred: {e}")
                return None

        except requests.exceptions.RequestException as e:
            logging.error(f"Error occurred: {e}")
            return None

    def save_game_logs_to_csv(self, season):
        endpoint = "game_log"
        params = self.endpoints[endpoint]["params"].copy()
        params["Season"] = season
        params["SeasonType"] = self.season_type
        game_logs = self.fetch_data(endpoint, params)
        if game_logs:
            file_path = os.path.join(
                self.output_dir, f"{self.season_type.lower().replace(' ', '_')}_game_logs.csv")
            headers = [
                'SEASON_ID', 'GAME_ID', 'GAME_DATE', 'MATCHUP',
                'HOME_TEAM_ID', 'HOME_TEAM_ABBREVIATION', 'HOME_TEAM_NAME', 'HOME_WL',
                'AWAY_TEAM_ID', 'AWAY_TEAM_ABBREVIATION', 'AWAY_TEAM_NAME', 'AWAY_WL',
                'SEASON_YEAR'
            ]
            with open(file_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                if file.tell() == 0:
                    writer.writerow(headers)
                games_dict = {}
                for row in game_logs["resultSets"][0]["rowSet"]:
                    game_id = row[4]
                    if game_id not in games_dict:
                        games_dict[game_id] = {}
                    matchup = row[6]
                    if "vs." in matchup:
                        games_dict[game_id]['home'] = {
                            'team_id': row[1],
                            'team_abbr': row[2],
                            'team_name': row[3],
                            'wl': row[7]
                        }
                    elif "@" in matchup:
                        games_dict[game_id]['away'] = {
                            'team_id': row[1],
                            'team_abbr': row[2],
                            'team_name': row[3],
                            'wl': row[7]
                        }
                    games_dict[game_id]['season_id'] = row[0]
                    games_dict[game_id]['game_date'] = row[5]
                    games_dict[game_id]['matchup'] = row[6]
                    games_dict[game_id]['season_year'] = season
                for game_id, data in games_dict.items():
                    if 'home' in data and 'away' in data:
                        merged_row = [
                            data['season_id'],
                            game_id,
                            data['game_date'],
                            data['matchup'],
                            data['home']['team_id'], data['home']['team_abbr'], data['home']['team_name'],
                            data['home']['wl'],
                            data['away']['team_id'], data['away']['team_abbr'], data['away']['team_name'],
                            data['away']['wl'],
                            data['season_year']
                        ]
                        writer.writerow(merged_row)
        else:
            logging.error(f"No game logs found for season {season}.")

    def extract_seasons(self):
        seasons_range = range(self.season_start, self.season_end + 1)
        with tqdm(total=len(seasons_range), desc=f"Extracting {self.season_type} data") as pbar:
            for year in seasons_range:
                season = f"{year}-{str(year + 1)[-2:]}"
                pbar.set_postfix({'season': season})
                for attempt in range(3):
                    try:
                        self.save_game_logs_to_csv(season)
                        time.sleep(self.delay)
                        break
                    except ForbiddenError:
                        logging.error(f"Access forbidden for season {season}. Retrying...")
                        time.sleep(60)
                    except TooManyRequestsError:
                        logging.error(f"Too many requests for season {season}. Waiting 1 minute before retrying...")
                        time.sleep(60)
                    except Exception as e:
                        logging.error(f"An error occurred: {e}")
                        time.sleep(60)
                pbar.update(1)
        logging.info(f"Data extraction completed. Data saved to {self.output_dir}")

    def save_play_by_play_to_csv(self, season, game_id, season_type):
        params = self.endpoints["play_by_play"]["params"].copy()
        params["GameID"] = game_id
        play_by_play_data = self.fetch_data("play_by_play", params)
        if play_by_play_data:
            folder_path = os.path.join(self.output_dir, season, season_type)
            os.makedirs(folder_path, exist_ok=True)
            file_path = os.path.join(folder_path, f"{game_id}.csv")
            headers = [
                "actionId", "actionNumber", "clock", "period", "teamId", "teamTricode", "personId", "playerName",
                "playerNameI", "xLegacy", "yLegacy", "shotDistance", "shotResult", "isFieldGoal", "scoreHome",
                "scoreAway", "pointsTotal", "location", "description", "actionType", "subType", "videoAvailable",
                "shotValue"
            ]
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                for row in play_by_play_data["game"]["actions"]:
                    writer.writerow([
                        row.get("actionId"), row.get("actionNumber"), row.get("clock"), row.get("period"),
                        row.get("teamId"), row.get("teamTricode"), row.get("personId"), row.get("playerName"),
                        row.get("playerNameI"), row.get("xLegacy"), row.get("yLegacy"), row.get("shotDistance"),
                        row.get("shotResult"), row.get("isFieldGoal"), row.get("scoreHome"), row.get("scoreAway"),
                        row.get("pointsTotal"), row.get("location"), row.get("description"), row.get("actionType"),
                        row.get("subType"), row.get("videoAvailable"), row.get("shotValue")
                    ])
        else:
            logging.error(f"No play-by-play data found for game {game_id}.")

    def extract_all_play_by_play(self):
        regular_season_df = pd.read_csv("data/game/regular_season_game_logs.csv", dtype={'GAME_ID': str})
        playoffs_df = pd.read_csv("data/game/playoffs_game_logs.csv", dtype={'GAME_ID': str})
        if 'processed' not in regular_season_df.columns:
            regular_season_df['processed'] = False
        if 'processed' not in playoffs_df.columns:
            playoffs_df['processed'] = False
        not_processed_regular_season_df = regular_season_df[~regular_season_df['processed']]
        not_processed_playoffs_df = playoffs_df[~playoffs_df['processed']]
        logging.info("Starting play-by-play extraction for regular season games...")
        logging.info(f"Total regular season games to process: {len(not_processed_regular_season_df)}")
        with tqdm(total=len(not_processed_regular_season_df), desc="Regular Season Extraction") as pbar:
            for index, row in not_processed_regular_season_df.iterrows():
                game_id = row['GAME_ID']
                season = row['SEASON_YEAR']
                pbar.set_postfix({'game_id': game_id})
                self.save_play_by_play_to_csv(season, game_id, 'regular_season')
                pbar.update(1)
                regular_season_df.loc[regular_season_df['GAME_ID'] == game_id, 'processed'] = True
                regular_season_df.to_csv("data/game/regular_season_game_logs.csv", index=False)
                time.sleep(self.delay)
        logging.info("Finished extracting regular season play-by-play.")
        logging.info("Starting play-by-play extraction for playoff games...")
        logging.info(f"Total playoff games to process: {len(not_processed_playoffs_df)}")
        with tqdm(total=len(not_processed_playoffs_df), desc="Playoff Extraction") as pbar:
            for index, row in not_processed_playoffs_df.iterrows():
                game_id = row['GAME_ID']
                season = row['SEASON_YEAR']
                pbar.set_postfix({'game_id': game_id})
                self.save_play_by_play_to_csv(season, game_id, 'playoffs')
                pbar.update(1)
                playoffs_df.loc[playoffs_df['GAME_ID'] == game_id, 'processed'] = True
                playoffs_df.to_csv("data/game/playoffs_game_logs.csv", index=False)
                time.sleep(self.delay)
        logging.info("Finished extracting playoff play-by-play.")

    def fetch_player_bios(self):
        endpoint = "player_bios"
        params = self.endpoints[endpoint]["params"].copy()
        player_data = self.fetch_data(endpoint, params)

        if player_data and "resultSets" in player_data:
            headers = player_data["resultSets"][0]["headers"]
            rows = player_data["resultSets"][0]["rowSet"]
            df_player_bios = pd.DataFrame(rows, columns=headers)
            df_player_bios.to_csv("data/player_bios.csv", index=False)
            logging.info("Player bios saved to data/player_bios.csv")
        else:
            logging.error("No player bios found.")

    def fetch_endpoint_data(self, endpoint, sub_endpoint, params):
        if endpoint not in self.endpoints or sub_endpoint not in self.endpoints[endpoint]:
            logging.error(f"Endpoint {endpoint}/{sub_endpoint} not found in endpoints.")
            return None
        url = NBAParams.build_url(self.endpoints[endpoint][sub_endpoint])
        response = None
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logging.error(f"Timeout occurred with parameters {params}. Terminating program.")
            sys.exit(1)
        except requests.exceptions.HTTPError as e:
            if response and response.status_code == 503:
                logging.error(f"503 Server Error for parameters {params}. Terminating program.")
                sys.exit(1)
            else:
                logging.error(f"HTTP Error occurred: {e}")
                return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Request Error occurred: {e}")
            return None

    def fetch_player_stats(self, endpoint, sub_endpoint, season, season_type=None, **kwargs):
        params = self.endpoints[endpoint][sub_endpoint]["params"].copy()
        params["Season"] = season
        params["SeasonType"] = season_type if season_type else self.season_type
        for key, value in kwargs.items():
            params[key] = value
        player_stats = self.fetch_endpoint_data(endpoint, sub_endpoint, params)
        if player_stats and "resultSets" in player_stats:
            headers = player_stats["resultSets"][0]["headers"]
            rows = player_stats["resultSets"][0]["rowSet"]
            season_folder = f"data/player/{endpoint}/{sub_endpoint}/{season}/{season_type.lower().replace(' ', '_')}"
            os.makedirs(season_folder, exist_ok=True)
            for row in rows:
                player_id = row[0]
                player_file_path = os.path.join(season_folder, f"{player_id}.csv")
                player_data = pd.DataFrame([row], columns=headers)
                player_data.to_csv(player_file_path, index=False)
                logging.info(f"Saved stats for player {player_id} in {player_file_path}")
        else:
            logging.error(f"No player stats found for {season}.")

    def fetch_stats_for_multiple_seasons(self, endpoint, sub_endpoint, start_season, end_season, season_types,
                                         **kwargs):
        for season_year in tqdm(range(start_season, end_season + 1), desc="Processing Seasons"):
            season = f"{season_year}-{str(season_year + 1)[-2:]}"
            for season_type in season_types:
                self.fetch_player_stats(endpoint, sub_endpoint, season, season_type, **kwargs)

    def close_session(self):
        self.session.close()

    @staticmethod
    def update_processed_status(season_type="Regular Season"):
        log_file = f"data/game/{season_type.lower().replace(' ', '_')}_game_logs.csv"
        if os.path.exists(log_file):
            df = pd.read_csv(log_file, dtype={'GAME_ID': str})
            total_games = len(df)
            logging.info(f"Starting to update 'processed' status for {total_games} games in {season_type}.")
            with tqdm(total=total_games, desc="Updating processed status") as pbar:
                for index, row in df.iterrows():
                    game_id = row['GAME_ID']
                    season_year = row['SEASON_YEAR']
                    season_folder = f"data/game/{season_year}/{season_type.lower().replace(' ', '_')}"
                    expected_file_path = os.path.join(season_folder, f"{game_id}.csv")
                    if os.path.exists(expected_file_path):
                        df.at[index, 'processed'] = True
                        logging.debug(f"Game {game_id} marked as processed.")
                    else:
                        df.at[index, 'processed'] = False
                        logging.debug(f"Game {game_id} marked as not processed (file missing).")
                    pbar.update(1)
            df.to_csv(log_file, index=False)
            logging.info(f"Updated processed status for all games in {log_file}")
        else:
            logging.error(f"File {log_file} not found.")


class ForbiddenError(Exception):
    pass


class TooManyRequestsError(Exception):
    pass
