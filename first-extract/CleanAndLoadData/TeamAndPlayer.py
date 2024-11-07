import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

def clean_jersey_number(jersey_number):
    if isinstance(jersey_number, str) and '-' in jersey_number:
        return int(jersey_number.split('-')[0])
    elif str(jersey_number).isdigit():
        return int(jersey_number)
    return None  

def convert_roster_status(value):
    if value == 'NaN' or pd.isna(value):  
        return None  
    elif value == 1.0 or value == 1:  
        return True
    elif value == 0.0 or value == 0:  
        return False
    return None  

def convert_height_to_inches(height_str):
    if isinstance(height_str, str) and '-' in height_str:
        feet, inches = height_str.split('-')
        try:
            feet = int(feet)
            inches = int(inches)
            
            total_inches = feet * 12 + inches
            return total_inches
        except ValueError:
            return None  
    return None  


# Fonction de nettoyage pour un fichier CSV
def clean_csv(file_path):
    df = pd.read_csv(file_path)

    df = df[df.columns.drop(list(df.filter(regex='rank|fantasy')))]

    df = df.where(pd.notnull(df), None)

    df['IS_DEFUNCT'] = df['IS_DEFUNCT'].apply(lambda x: True if x == 1 else (False if x == 0 else None))

    print("\nNombre de valeurs manquantes par colonne :")
    print(df.isna().sum())

    print("\nNombre de doublons dans le DataFrame :")
    print(df.duplicated().sum())

    df = df.drop_duplicates()

    df['HEIGHT'] = df['HEIGHT'].apply(convert_height_to_inches)

    df['ROSTER_STATUS'] = df['ROSTER_STATUS'].apply(convert_roster_status)

    df['JERSEY_NUMBER'] = df['JERSEY_NUMBER'].apply(clean_jersey_number)

    df.to_csv("./first-extract/data/player_nettoye.csv")

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

# Insertion des données teams
def load_team_data(data):
    conn = connect_db()
    cursor = conn.cursor()
    
    teams_df = data[['TEAM_ID', 'TEAM_NAME', 'TEAM_CITY', 'TEAM_ABBREVIATION', 'TEAM_SLUG']].drop_duplicates()

    teams_df = teams_df.where(pd.notnull(teams_df), None)

    print("Équipes uniques extraites :")
    print(teams_df)

    num_teams = data['TEAM_ID'].nunique()

    print(f"Nombre d'équipes uniques dans le DataFrame : {num_teams}")
    insert_query = """
        INSERT INTO team (team_id, name, city, abbreviation, slug)
        VALUES %s
        ON CONFLICT (team_id) DO NOTHING
    """
 
    teams_to_insert = [(row['TEAM_ID'], row['TEAM_NAME'], row['TEAM_CITY'], row['TEAM_ABBREVIATION'], row['TEAM_SLUG']) for index, row in teams_df.iterrows()]

    try:
        execute_values(cursor, insert_query, teams_to_insert)
        print("Les informations des équipes ont été insérées avec succès")
        conn.commit()
    except Exception as e:
        print(f"Erreur lors de l'insertion des informations des équipes : {e}")

    try:
        cursor.execute("SELECT * FROM team")
        rows = cursor.fetchall()
        print("\nÉquipes :")
        for row in rows:
            print(row)
    except Exception as e:
        print(f"Erreur lors de la récupération du nombre d'équipes : {e}")

    cursor.close()
    conn.close()

# Insertion des données players
def load_player_data(data):
    conn = connect_db()
    cursor = conn.cursor()
    
    df_player = data[[
        'PERSON_ID', 'PLAYER_FIRST_NAME', 'PLAYER_LAST_NAME', 'PLAYER_SLUG', 'TEAM_ID',
        'IS_DEFUNCT', 'JERSEY_NUMBER', 'POSITION', 'HEIGHT', 'WEIGHT', 'COLLEGE', 'COUNTRY',
        'DRAFT_YEAR', 'DRAFT_ROUND', 'DRAFT_NUMBER', 'ROSTER_STATUS', 'PTS', 'REB', 'AST',
        'STATS_TIMEFRAME', 'FROM_YEAR', 'TO_YEAR'
    ]]

    num_players = data['PERSON_ID'].nunique()

    print(f"Nombre de joueurs dans le DataFrame : {num_players}")

    insert_query = """
        INSERT INTO player (
            player_id, firstname, lastname,player_slug,team_id,is_defunct,jersey_number,position,height,weight,college,country
            ,draft_year,draft_round,draft_number,roster_status,points,rebounds,assists,stats_timeframe,from_year,to_year
        ) VALUES %s
        ON CONFLICT (player_id) DO NOTHING
    """
    
    players_to_insert = [(row['PERSON_ID'], row['PLAYER_FIRST_NAME'], row['PLAYER_LAST_NAME'], row['PLAYER_SLUG'], 
                        row['TEAM_ID'], row['IS_DEFUNCT'], int(row['JERSEY_NUMBER']) if pd.notna(row['JERSEY_NUMBER']) else None, row['POSITION'], row['HEIGHT'], 
                        row['WEIGHT'], row['COLLEGE'], row['COUNTRY'], int(row['DRAFT_YEAR']) if pd.notna(row['DRAFT_YEAR']) else None, 
                        int(row['DRAFT_ROUND']) if pd.notna(row['DRAFT_ROUND']) else None,
                        int(row['DRAFT_NUMBER']) if pd.notna(row['DRAFT_NUMBER']) else None, row['ROSTER_STATUS'], row['PTS'], row['REB'], row['AST'], 
                        row['STATS_TIMEFRAME'], int(row['FROM_YEAR']) if pd.notna(row['FROM_YEAR']) else None,
                        int(row['TO_YEAR']) if pd.notna(row['TO_YEAR']) else None) for index, row in df_player.iterrows()]

    try:
        execute_values(cursor, insert_query, players_to_insert)
        print("Les informations des joueurs ont été insérées avec succès")
        conn.commit()
    except Exception as e:
        print(f"Erreur lors de l'insertion des informations des joueurs : {e}")

    try:
        cursor.execute("SELECT COUNT(*) FROM player")
        player_count = cursor.fetchone()[0]
        print(f"Nombre de joueurs dans la base de données : {player_count}")
    except Exception as e:
        print(f"Erreur lors de la récupération du nombre de joueurs : {e}")

    cursor.close()
    conn.close()

data = clean_csv("./first-extract/data/player_bios.csv")
load_team_data(data)
load_player_data(data)





