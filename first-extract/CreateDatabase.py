
import psycopg2

# Configuration de la connexion
db_params = {
    "host": "localhost",
    "port": "5432",
    "dbname": "nba_db",
    "user": "postgres",
    "password": "postgres"
}

# Connexion à PostgreSQL
try:
    conn = psycopg2.connect(**db_params)
    conn.autocommit = True
    cursor = conn.cursor()
    print("Connexion réussie à PostgreSQL")
except Exception as e:
    print(f"Erreur de connexion: {e}")

# Option 1 : Supprimer le schéma si nécessaire avant de le recréer
try:
    cursor.execute("DROP SCHEMA IF EXISTS public CASCADE;")
    cursor.execute("CREATE SCHEMA public;")
    print("Schéma supprimé et va etre recréé")
except Exception as e:
    print(f"Erreur lors de la suppression du schéma: {e}")

# Charger le schéma SQL
try:
    with open("./first-extract/NbaBD.sql", "r") as file:
        schema_sql = file.read()
    cursor.execute(schema_sql)
    print("Schéma chargé avec succès")
except Exception as e:
    print(f"Erreur lors du chargement du schéma: {e}")


# Fermer la connexion
cursor.close()
conn.close()
