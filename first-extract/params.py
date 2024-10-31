from random import randint


class NBAParams:
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
    }

    TIMEOUT_REQUEST = 10

    DELAY = randint(0, 1)

    @classmethod
    def build_url(cls, endpoint):
        return cls.BASE_URL + endpoint["url"]
