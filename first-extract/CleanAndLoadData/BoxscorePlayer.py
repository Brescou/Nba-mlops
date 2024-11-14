import pandas as pd
import psycopg2
from psycopg2.extras import execute_values 

# Fonction de nettoyage pour un fichier CSV
def clean_csv(file_path):
    df = pd.read_csv(file_path)

    df = df[df.columns.drop(list(df.filter(regex='RANK|FANTASY')))]

    print("\nNombre de valeurs manquantes par colonne :")
    print(df.isna().sum())
    
    df = df.where(pd.notnull(df), None)

    df['DD2'] = df['DD2'].apply(lambda x: True if x == 1 else (False if x == 0 else None))

    df['TD3'] = df['TD3'].apply(lambda x: True if x == 1 else (False if x == 0 else None))

    print("\nNombre de doublons dans le DataFrame :")
    print(df.duplicated().sum())

    df = df.drop_duplicates() 

    df['BOXSCORE_ID'] = df['PLAYER_ID'].astype(str) + df['GAME_ID'].astype(str)

    print(df.describe())

    return df

# Connexion à PostgreSQL
def connect_db():
    conn = psycopg2.connect(
        host="localhost",
        database="nba_db",
        user="postgres",
        password="postgres"
    )
    return conn

# Insertion des données boxscores
def load_boxscore_data(data):

    conn = connect_db()
    cursor = conn.cursor()
    
    boxscore_df = data[['BOXSCORE_ID','SEASON_YEAR', 'PLAYER_ID', 'TEAM_ID', 'GAME_ID', 'GAME_DATE', 
                      'MATCHUP', 'WL', 'MIN']]

    num_boxscores = data['BOXSCORE_ID'].nunique()

    print(f"Nombre de boxscore dans le DataFrame : {num_boxscores}")

    insertBoxscore_query = """
        INSERT INTO player_boxscore (boxscore_id, season_year, player_id, team_id, game_id, game_date, matchup, wl, min)
        VALUES %s
        ON CONFLICT (boxscore_id) DO NOTHING
    """
 
    values_boxscore = [( row['BOXSCORE_ID'], row['SEASON_YEAR'], row['PLAYER_ID'], row['TEAM_ID'], row['GAME_ID'], row['GAME_DATE'], 
    row['MATCHUP'], row['WL'], row['MIN']
    ) for index, row in boxscore_df.iterrows()]

    try:
        execute_values(cursor, insertBoxscore_query, values_boxscore)
        print("Les informations des boxscores ont été insérées avec succès")
        conn.commit()
    except Exception as e:
        print(f"Erreur lors de l'insertion des informations des boxscores : {e}")

    try:
        cursor.execute("SELECT COUNT(*) FROM player_boxscore")
        game_count = cursor.fetchone()[0]
        print(f"Nombre de boxscores dans la base de données : {game_count}")
    except Exception as e:
        print(f"Erreur lors de la récupération du nombre de boxscores : {e}")

    cursor.close()
    conn.close()

# Insertion des données boxscores base
def load_boxscoreBase_data(data):

    conn = connect_db()
    cursor = conn.cursor()
    
    boxscoreBase_df = data[["BOXSCORE_ID", "FGM", "FGA", "FG_PCT", "FG3M", "FG3A", "FG3_PCT", 
    "FTM", "FTA", "FT_PCT", "OREB", "DREB", "REB", "AST", "TOV","STL", "BLK", "BLKA", "PF", "PFD",
    "PTS", "PLUS_MINUS", "DD2","TD3", "MIN_SEC"]]

    insertBoxscoreBase_query = """
        INSERT INTO player_boxscore_base (boxscore_id, fgm, fga, fg_pct, fg3m, fg3a, fg3_pct, ftm, fta, ft_pct, oreb, 
        dreb, reb, ast, tov, stl, blk, blka, pf, pfd, pts, plus_minus, dd2, td3, min_sec)
        VALUES %s
        ON CONFLICT (boxscore_id) DO NOTHING
    """
 
    values_boxscoreBase = [( row['BOXSCORE_ID'], row['FGM'], row['FGA'], row['FG_PCT'], row['FG3M'], row['FG3A'], row['FG3_PCT'], 
        row['FTM'], row['FTA'], row['FT_PCT'], row['OREB'], row['DREB'], row['REB'],
        row['AST'], row['TOV'], row['STL'], row['BLK'], row['BLKA'], row['PF'], row['PFD'],
        row['PTS'], row['PLUS_MINUS'], row['DD2'], row['TD3'], row['MIN_SEC']
    ) for index, row in boxscoreBase_df.iterrows()]

    try:
        execute_values(cursor, insertBoxscoreBase_query, values_boxscoreBase)
        print("Les informations des boxscores Base ont été insérées avec succès")
        conn.commit()
    except Exception as e:
        print(f"Erreur lors de l'insertion des informations des boxscores Base : {e}")

    try:
        cursor.execute("SELECT COUNT(*) FROM player_boxscore_base")
        base_count = cursor.fetchone()[0]
        print(f"Nombre de boxscores bases dans la base de données : {base_count}")
    except Exception as e:
        print(f"Erreur lors de la récupération du nombre de boxscores bases : {e}")

    cursor.close()
    conn.close()


data = clean_csv("./first-extract/data/player/boxscores/2023-24_regular_season_base.csv")
load_boxscore_data(data)
load_boxscoreBase_data(data)