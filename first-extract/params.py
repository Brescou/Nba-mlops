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
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/"
                      "129.0.0.0 Safari/537.36"
    }

    TIMEOUT_REQUEST = 10

    DELAY = randint(1, 5)

    @classmethod
    def build_url(cls, endpoint):
        return cls.BASE_URL + endpoint["url"]
