import csv
import logging
import os
import time

import requests
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)


class NBADataExtractor:
    BASE_URL = "https://stats.nba.com/stats/"

    HEADERS = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "fr,en-US;q=0.9,en;q=0.8,fr-FR;q=0.7",
        "connection": "keep-alive",
        "dnt": "1",
        "host": "stats.nba.com",
        "origin": "https://www.nba.com",
        "referer": "https://www.nba.com/",
        "sec-ch-ua": "\"Google Chrome\";v=\"129\", \"Not=A?Brand\";v=\"8\", \"Chromium\";v=\"129\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Linux\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    }

    def __init__(self, endpoints, season_start=1996, season_end=None, delay=1, output_dir="./data/game/"):
        self.endpoints = endpoints
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self.season_start = season_start
        self.season_end = season_end if season_end else season_start  # Si season_end n'est pas spécifié, on le met égal à season_start
        self.output_dir = output_dir
        self.season_type = "Regular Season"

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def change_season_type(self, season_type):
        if season_type not in ["Regular Season", "Playoffs"]:
            raise ValueError("Invalid season type. Must be 'Regular Season' or 'Playoffs'.")
        self.season_type = season_type
        print(f"Season type changed to {self.season_type}")

    def fetch_data(self, endpoint, params):
        url = self.endpoints[endpoint]["url"]
        response = self.session.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Failed to fetch data from {url} with status {response.status_code}")
            return None

    def fetch_game_logs(self, season):
        endpoint = "game_log"
        params = self.endpoints[endpoint]["params"].copy()
        params["Season"] = season
        params["SeasonType"] = self.season_type
        return self.fetch_data(endpoint, params)

    def save_game_logs_to_csv(self, season):
        game_logs = self.fetch_game_logs(season)
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
                    game_id = row[4]  # GAME_ID
                    if game_id not in games_dict:
                        games_dict[game_id] = {}
                    matchup = row[6]
                    if "vs." in matchup:  # Home team
                        games_dict[game_id]['home'] = {
                            'team_id': row[1],
                            'team_abbr': row[2],
                            'team_name': row[3],
                            'wl': row[7]  # Win/Loss
                        }
                    elif "@" in matchup:  # Away team
                        games_dict[game_id]['away'] = {
                            'team_id': row[1],
                            'team_abbr': row[2],
                            'team_name': row[3],
                            'wl': row[7]  # Win/Loss
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
        filename = f"{self.season_type.lower().replace(' ', '_')}_game_logs_head.csv"
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

    def close_session(self):
        self.session.close()


class ForbiddenError(Exception):
    pass


class TooManyRequestsError(Exception):
    pass
