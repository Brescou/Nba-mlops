import subprocess

def dump_database_from_docker(container_name, dbname, username, dump_file):
    try:
        subprocess.run([
            'docker', 'exec', '-t', container_name,
            'pg_dump', '-U', username, '-d', dbname, '-f', f'/tmp/{dump_file}'
        ], check=True)
        
        subprocess.run([
            'docker', 'cp', f'{container_name}:/tmp/{dump_file}', f'./{dump_file}'
        ], check=True)
        
        print(f"Le dump de la base de données {dbname} a été créé avec succès dans {dump_file}")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors du dump de la base de données : {e}")

# Exemple d'appel de la fonction
dump_database_from_docker('postgres_db', 'nba_db', 'postgres', 'dump.sql')
