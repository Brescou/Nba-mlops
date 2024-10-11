import logging
import time

import requests

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

    def __init__(self, endpoints, delay=1):
        self.endpoints = endpoints
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def _fetch_data(self, category, stat_type, season, season_type, group_quantity=None, retries=3, delay_factor=5):
        endpoint_info = self.endpoints[category][stat_type]
        url = endpoint_info["url"]
        params = endpoint_info["params"].copy()
        params["Season"] = season
        params["SeasonType"] = season_type
        if "GroupQuantity" in params and group_quantity:
            params["GroupQuantity"] = group_quantity
        for attempt in range(retries):
            try:
                time.sleep(self.delay)
                response = self.session.get(url, params=params)

                if response.status_code == 403:
                    raise ForbiddenError("403 Error: Access denied. Your IP might be blocked.")
                if response.status_code == 429:
                    raise TooManyRequestsError("429 Error: Too many requests. Please try again later.")
                if response.status_code != 200:
                    response.raise_for_status()
                logging.info(f"Successfully fetched data for {stat_type} in season {season}.")
                return response.json()

            except requests.exceptions.HTTPError as errh:
                logging.error(f"HTTP Error: {errh}")
                raise

            except requests.exceptions.ConnectionError as errc:
                logging.error(f"Connection Error: {errc}")
                raise

            except requests.exceptions.Timeout as errt:
                logging.error(f"Timeout Error: {errt}")
                raise

            except ForbiddenError as err403:
                logging.error(f"{err403}")
                raise

            except TooManyRequestsError as err429:
                logging.warning(f"{err429}")
                if attempt < retries - 1:
                    time.sleep(delay_factor)
                    delay_factor *= 2
                else:
                    raise

            except requests.exceptions.RequestException as err:
                logging.error(f"Request Error: {err}")
                raise

    def fetch_player_stats(self, stat_type, season, season_type):
        return self._fetch_data("player", stat_type, season, season_type)

    def fetch_team_stats(self, stat_type, season, season_type):
        return self._fetch_data("teams", stat_type, season, season_type)

    def fetch_lineups_stats(self, stat_type, season, season_type, group_quantity=5):
        return self._fetch_data("lineups", stat_type, season, season_type, group_quantity=group_quantity)

    def close_session(self):
        self.session.close()


class ForbiddenError(Exception):
    pass


class TooManyRequestsError(Exception):
    pass
