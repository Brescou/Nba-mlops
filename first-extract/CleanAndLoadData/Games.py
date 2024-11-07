import pandas as pd
import psycopg2
from psycopg2.extras import execute_values 

# Fonction de nettoyage pour un fichier CSV
def clean_csv(file_path):
    df = pd.read_csv(file_path)

    df = df[df.columns.drop(list(df.filter(regex='rank|fantasy')))]

    print("\nNombre de valeurs manquantes par colonne :")
    print(df.isna().sum())
    
    df = df.where(pd.notnull(df), None)

    print("\nNombre de doublons dans le DataFrame :")
    print(df.duplicated().sum())

    df = df.drop_duplicates()
    
    df['RESULT'] = df.apply(lambda row: 'HOME' if row['HOME_WL'] == 'W' else 'AWAY', axis=1)

    print("Types de données avant conversion :")
    print(df.dtypes)

    print(df['GAME_ID'].is_unique)  

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

# Insertion des données games
def load_game_data(data):
    print(data.describe())
    conn = connect_db()
    cursor = conn.cursor()
    
    games_df = data[['GAME_ID', 'SEASON_YEAR', 'GAME_DATE', 'HOME_TEAM_ID','AWAY_TEAM_ID', 'RESULT']]

    num_games = data['GAME_ID'].nunique()

    print(f"Nombre de matchs dans le DataFrame : {num_games}")

    insert_query = """
        INSERT INTO game (game_id, season_year, date, home_team_id, away_team_id, result)
        VALUES %s
        ON CONFLICT (game_id) DO NOTHING
    """
 
    games_to_insert = [(row['GAME_ID'], row['SEASON_YEAR'], row['GAME_DATE'], row['HOME_TEAM_ID'], row['AWAY_TEAM_ID'], row['RESULT']) for index, row in games_df.iterrows()]

    try:
        execute_values(cursor, insert_query, games_to_insert)
        print("Les informations des matchs ont été insérées avec succès")
        conn.commit()
    except Exception as e:
        print(f"Erreur lors de l'insertion des informations des matchs : {e}")

    try:
        cursor.execute("SELECT COUNT(*) FROM game")
        game_count = cursor.fetchone()[0]
        print(f"Nombre de matchs dans la base de données : {game_count}")
    except Exception as e:
        print(f"Erreur lors de la récupération du nombre de matchs : {e}")

    cursor.close()
    conn.close()

game = clean_csv("./first-extract/data/game/playoffs_game_logs.csv")
regularGame = clean_csv("./first-extract/data/game/regular_season_game_logs.csv")

resultat  = pd.concat([game, regularGame], ignore_index=True)

load_game_data(resultat) 