import pandas as pd
import sys
import os

# Ajouter le chemin de 'db' au chemin de recherche des modules
current_dir = os.path.dirname(os.path.abspath(__file__))  
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))  
sys.path.append(os.path.join(parent_dir, 'db'))

from db.DB import DB 

def Get_all_csv(directory,keyword):
    csv_files = [
        os.path.join(directory, file)
        for file in os.listdir(directory)
        if file.endswith(".csv") and keyword in file.lower() and "2024-25" not in file
    ]

    print(f"Fichiers CSV identifiés : {csv_files}")

    return csv_files

# Fonction de nettoyage pour un fichier CSV
def clean_csv(file_path):
    df = pd.read_csv(file_path)

    df = df[df.columns.drop(list(df.filter(regex='RANK|FANTASY')))]

    print("\nNombre de valeurs manquantes par colonne :")
    print(df.isna().sum())
    
    df = df.where(pd.notnull(df), None)

    print("\nNombre de doublons dans le DataFrame :")
    print(df.duplicated().sum())

    df = df.drop_duplicates() 

    df['BOXSCORE_ID'] = df['TEAM_ID'].astype(str) + '-' + df['GAME_ID'].astype(str)

    print(df.describe())

    return df

boxscoreBaseCSV = Get_all_csv("./first-extract/data/teams/boxscores/", "base")


for csv_file in boxscoreBaseCSV:
        print(f"Traitement du fichier : {csv_file}")
                
        data = clean_csv(csv_file)

        columns_boxscore = [
            "BOXSCORE_ID", "SEASON_YEAR", "TEAM_ID", "GAME_ID", "GAME_DATE",
            "MATCHUP", "WL", "MIN"
            ]
        df_boxscore = data[columns_boxscore]

        columns_boxscoreBase = [
            "BOXSCORE_ID", "FGM", "FGA", "FG_PCT", "FG3M", "FG3A", "FG3_PCT",
            "FTM", "FTA", "FT_PCT", "OREB", "DREB", "REB", "AST", "TOV", "STL",
            "BLK", "BLKA", "PF", "PFD", "PTS", "PLUS_MINUS"
        ]
        df_boxscore_base = data[columns_boxscoreBase]


        # Charger les données dans la base de données
        with DB() as db:
            db.load_data_from_dataframe("team_boxscore", df_boxscore)
            db.load_data_from_dataframe("team_boxscore_base", df_boxscore_base)

boxscoreFour_FactorsCSV = Get_all_csv("./first-extract/data/teams/boxscores/", "four factors")

for csv_file in boxscoreFour_FactorsCSV:
        print(f"Traitement du fichier : {csv_file}")
                
        data = clean_csv(csv_file)

        columns_boxscoreFour_Factors = [
            "BOXSCORE_ID", "EFG_PCT", "FTA_RATE", "TM_TOV_PCT", "OREB_PCT",
            "OPP_EFG_PCT", "OPP_FTA_RATE", "OPP_TOV_PCT", "OPP_OREB_PCT"
        ]
        df_boxscore_Four_Factors = data[columns_boxscoreFour_Factors]

        # Charger les données dans la Four_Factors de données
        with DB() as db:
            db.load_data_from_dataframe("team_boxscore_four_factors", df_boxscore_Four_Factors)

boxscoreMiscCSV = Get_all_csv("./first-extract/data/teams/boxscores/", "misc")

for csv_file in boxscoreMiscCSV:
        print(f"Traitement du fichier : {csv_file}")
                
        data = clean_csv(csv_file)

        columns_boxscoreMisc = [
            "BOXSCORE_ID", "PTS_OFF_TOV", "PTS_2ND_CHANCE", "PTS_FB", "PTS_PAINT",
            "OPP_PTS_OFF_TOV", "OPP_PTS_2ND_CHANCE", "OPP_PTS_FB", "OPP_PTS_PAINT"
        ]
        df_boxscore_misc = data[columns_boxscoreMisc]

        # Charger les données dans la misc de données
        with DB() as db:
            db.load_data_from_dataframe("team_boxscore_misc", df_boxscore_misc)

boxscoreScoringCSV = Get_all_csv("./first-extract/data/teams/boxscores/", "scoring")

for csv_file in boxscoreScoringCSV:
        print(f"Traitement du fichier : {csv_file}")
                
        data = clean_csv(csv_file)

        columns_boxscoreScoring = [
            "BOXSCORE_ID", "PCT_FGA_2PT", "PCT_FGA_3PT", "PCT_PTS_2PT", "PCT_PTS_2PT_MR",
            "PCT_PTS_3PT", "PCT_PTS_FB", "PCT_PTS_FT", "PCT_PTS_OFF_TOV", "PCT_PTS_PAINT",
            "PCT_AST_2PM", "PCT_UAST_2PM", "PCT_AST_3PM", "PCT_UAST_3PM", 
            "PCT_AST_FGM", "PCT_UAST_FGM"
        ]
        df_boxscore_scoring = data[columns_boxscoreScoring]

        # Charger les données dans la scoring de données
        with DB() as db:
            db.load_data_from_dataframe("team_boxscore_scoring", df_boxscore_scoring)

boxscoreAdvancedCSV = Get_all_csv("./first-extract/data/teams/boxscores/", "advanced")

for csv_file in boxscoreAdvancedCSV:
        print(f"Traitement du fichier : {csv_file}")
                
        data = clean_csv(csv_file)

        columns_boxscoreAdvanced = [
            "BOXSCORE_ID", "OFF_RATING", "DEF_RATING", "NET_RATING", "AST_PCT",
            "AST_TO", "AST_RATIO", "OREB_PCT", "DREB_PCT", "REB_PCT", "TM_TOV_PCT",
            "EFG_PCT", "TS_PCT", "PACE", "PIE"
        ]
        df_boxscore_advanced = data[columns_boxscoreAdvanced]

        # Charger les données dans la advanced de données
        with DB() as db:
            db.load_data_from_dataframe("team_boxscore_advanced", df_boxscore_advanced)