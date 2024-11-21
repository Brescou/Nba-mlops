import pandas as pd

import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))  
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))  
sys.path.append(os.path.join(parent_dir, 'db'))

from db.DB import DB 

def Get_all_csv(directory,keyword):
    # Lister les fichiers CSV contenant "base" dans leur nom
    csv_files = [
        os.path.join(directory, file)
        for file in os.listdir(directory)
        if file.endswith(".csv") and keyword in file.lower() and "2024-25" not in file
    ]

    # Vérifier les fichiers identifiés
    print(f"Fichiers CSV identifiés : {csv_files}")

    return csv_files

# Fonction de nettoyage pour un fichier CSV
def clean_csv(file_path):
    df = pd.read_csv(file_path)

    df = df[df.columns.drop(list(df.filter(regex='RANK|FANTASY')))]
    
    df = df.where(pd.notnull(df), None)

    df = df.drop_duplicates() 

    df['BOXSCORE_ID'] = df['PLAYER_ID'].astype(str) + '-' + df['GAME_ID'].astype(str)

    return df

boxscoreBaseCSV = Get_all_csv("./first-extract/data/player/boxscores/", "base")

for csv_file in boxscoreBaseCSV:
        print(f"Traitement du fichier : {csv_file}")
                
        data = clean_csv(csv_file)

        data['DD2'] = data['DD2'].apply(lambda x: True if x == 1 else (False if x == 0 else None))

        data['TD3'] = data['TD3'].apply(lambda x: True if x == 1 else (False if x == 0 else None))

        columns_boxscore = [
            "BOXSCORE_ID", "SEASON_YEAR", "TEAM_ID", "GAME_ID", "GAME_DATE",
            "MATCHUP", "WL", "MIN"
            ]
        df_boxscore = data[columns_boxscore]

        columns_boxscoreBase = [
            "BOXSCORE_ID", "FGM", "FGA", "FG_PCT", "FG3M", "FG3A", "FG3_PCT", 
            "FTM", "FTA", "FT_PCT", "OREB", "DREB", "REB", "AST", "TOV","STL", "BLK", "BLKA", "PF", "PFD",
            "PTS", "PLUS_MINUS", "DD2","TD3", "MIN_SEC"
        ]
        df_boxscore_base = data[columns_boxscoreBase]

        # Charger les données dans la base de données
        with DB() as db:
            db.load_data_from_dataframe("player_boxscore", df_boxscore)
            db.load_data_from_dataframe("player_boxscore_base", df_boxscore_base)

boxscoreMiscCSV = Get_all_csv("./first-extract/data/player/boxscores/", "misc")

for csv_file in boxscoreMiscCSV:
        print(f"Traitement du fichier : {csv_file}")
                
        data = clean_csv(csv_file)

        columns_boxscoreMisc = [
            "BOXSCORE_ID","PTS_OFF_TOV","PTS_2ND_CHANCE","PTS_FB","PTS_PAINT","OPP_PTS_OFF_TOV",
            "OPP_PTS_2ND_CHANCE","OPP_PTS_FB","OPP_PTS_PAINT","BLK",
            "BLKA","PF","PFD","MIN_SEC"
        ]

        df_boxscore_misc = data[columns_boxscoreMisc]

        # Charger les données dans la misc de données
        with DB() as db:
            db.load_data_from_dataframe("player_boxscore_misc", df_boxscore_misc)

boxscoreScoringCSV = Get_all_csv("./first-extract/data/player/boxscores/", "scoring")

for csv_file in boxscoreScoringCSV:
        print(f"Traitement du fichier : {csv_file}")
                
        data = clean_csv(csv_file)

        columns_boxscoreScoring = [
            'BOXSCORE_ID', 'PCT_FGA_2PT', 'PCT_FGA_3PT', 'PCT_PTS_2PT', 'PCT_PTS_2PT_MR',
            'PCT_PTS_3PT', 'PCT_PTS_FB', 'PCT_PTS_FT', 'PCT_PTS_OFF_TOV', 'PCT_PTS_PAINT',
            'PCT_AST_2PM', 'PCT_UAST_2PM', 'PCT_AST_3PM', 'PCT_UAST_3PM', 'PCT_AST_FGM',
            'PCT_UAST_FGM', 'FGM', 'FGA', 'FG_PCT', 'MIN_SEC'
        ]

        df_boxscore_scoring = data[columns_boxscoreScoring]

        # Charger les données dans la scoring de données
        with DB() as db:
            db.load_data_from_dataframe("player_boxscore_scoring", df_boxscore_scoring)

boxscoreUsageCSV = Get_all_csv("./first-extract/data/player/boxscores/", "usage")

for csv_file in boxscoreUsageCSV:
        print(f"Traitement du fichier : {csv_file}")
                
        data = clean_csv(csv_file)

        columns_boxscoreUsage = [
            'BOXSCORE_ID', 'USG_PCT', 'PCT_FGM', 'PCT_FGA', 'PCT_FG3M', 'PCT_FG3A', 
            'PCT_FTM', 'PCT_FTA', 'PCT_OREB', 'PCT_DREB', 'PCT_REB', 'PCT_AST', 
            'PCT_TOV', 'PCT_STL', 'PCT_BLK', 'PCT_BLKA', 'PCT_PF', 'PCT_PFD', 'PCT_PTS', 'MIN_SEC'
        ]

        df_boxscore_usage = data[columns_boxscoreUsage]

        # Charger les données dans la usage de données
        with DB() as db:
            db.load_data_from_dataframe("player_boxscore_usage", df_boxscore_usage)