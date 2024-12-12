import subprocess
import os
from datetime import datetime

DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "nba_db"
DB_USER = "postgres"
DB_PASSWORD = "postgres"

BACKUP_DIR = "/db_backups"
DDL_FILE = "./NbaBD.sql"


def backup_database():
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{BACKUP_DIR}/nba_db_backup_{timestamp}.sql"
        with open(backup_file, "w") as f:
            subprocess.run(
                [
                    "docker", "exec", "-t", "postgres_db",
                    "pg_dump", 
                    "-U", DB_USER,
                    "-d", DB_NAME,
                    "--create",      
                    "--if-exists",   
                    "--no-owner"     
                ],
                stdout=f
            )
        print(f"Backup completed and saved to {backup_file}")
    except Exception as e:
        print(f"Error during backup: {e}")


def get_latest_backup_file():
    try:
        files = [f for f in os.listdir(BACKUP_DIR) if f.startswith("nba_db_backup_") and f.endswith(".sql")]
        if not files:
            print("No backup files found.")
            return None
        latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(BACKUP_DIR, x)))
        return os.path.join(BACKUP_DIR, latest_file)
    except Exception as e:
        print(f"Error finding the latest backup file: {e}")
        return None


def restore_database():
    latest_backup = get_latest_backup_file()
    if latest_backup is None:
        print("No backup file available for restoration.")
        return
    try:
        with open(latest_backup, "r") as f:
            subprocess.run(
                [
                    "docker", "exec", "-i", "postgres_db",
                    "psql", "-U", DB_USER, "-d", DB_NAME
                ],
                stdin=f
            )
        print(f"Database restored from the latest backup: {latest_backup}")
    except Exception as e:
        print(f"Error during restoration: {e}")


def run_ddl_script():
    if not os.path.exists(DDL_FILE):
        print(f"DDL file '{DDL_FILE}' not found.")
        return
    try:
        with open(DDL_FILE, "r") as f:
            subprocess.run(
                [
                    "docker", "exec", "-i", "postgres_db",
                    "psql", "-U", DB_USER, "-d", DB_NAME
                ],
                stdin=f
            )
        print(f"Database structure created successfully from '{DDL_FILE}'")
    except Exception as e:
        print(f"Error executing DDL script: {e}")


def reset_database():
    try:
        subprocess.run(
            [
                "docker", "exec", "-i", "postgres_db",
                "psql", "-U", DB_USER, "-c", f"DROP DATABASE IF EXISTS {DB_NAME};"
            ]
        )
        print(f"Database '{DB_NAME}' dropped successfully.")

        subprocess.run(
            [
                "docker", "exec", "-i", "postgres_db",
                "psql", "-U", DB_USER, " - c", f"CREATE DATABASE {DB_NAME};"]
        )
        print(f"Database '{DB_NAME}' recreated successfully.")

        run_ddl_script()
        print("Database structure recreated successfully.")
    except Exception as e:
        print(f"Error resetting the database: {e}")


if __name__ == "__main__":
    print("Options:")
    print("1. Backup the database")
    print("2. Restore the database from the latest backup")
    print("3. Run DDL script to create database structure")
    print("4. Reset the database")
    choice = input("Choose an option (1/2/3/4): ")

    if choice == "1":
        backup_database()
    elif choice == "2":
        restore_database()
    elif choice == "3":
        run_ddl_script()
    elif choice == "4":
        reset_database()
    else:
        print("Invalid option.")
