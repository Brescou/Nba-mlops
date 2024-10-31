from nordvpn_connect import initialize_vpn, rotate_VPN, close_vpn_connection
import requests
import logging

class NordVPNManager:
    def __init__(self, country="United_States"):
        self.country = country
        self.settings = None
        self.session = requests.Session()

    def connect(self):
        try:
            self.settings = initialize_vpn(self.country)
            rotate_VPN(self.settings)
            logging.info(f"Connecté à NordVPN via le serveur : {self.country}")
        except Exception as e:
            logging.error("Erreur lors de la connexion à NordVPN :", e)

    def disconnect(self):
        if self.settings:
            close_vpn_connection(self.settings)
            logging.info("Déconnecté de NordVPN.")
        else:
            logging.warning("Pas de connexion VPN active à fermer.")

    def get(self, url, params=None, headers=None):
        try:
            response = self.session.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error("Erreur lors de la requête :", e)
            return None

    def close(self):
        self.session.close()
        self.disconnect()


if __name__ == "__main__":
    vpn = NordVPNManager(country="United_States")
    vpn.connect()
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    response = vpn.get("https://stats.nba.com/stats/leaguedashplayerstats", params={"Season": "2024-25"},
                       headers=headers)
    if response:
        print("Réponse de la requête :", response)
    else:
        print("La requête a échoué.")
    vpn.disconnect()
