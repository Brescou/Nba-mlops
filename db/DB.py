import os

import psycopg2

import logging

from psycopg2.extras import execute_values

logging.basicConfig(level=logging.INFO)


class DB:
    def __init__(self):
        self.dbname = os.getenv("DB_NAME", "nba_db")
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "postgres")
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "5432")
        self.connection = None

    def connect(self):
        if self.connection is None or self.connection.closed:
            try:
                self.connection = psycopg2.connect(
                    dbname=self.dbname,
                    user=self.user,
                    password=self.password,
                    host=self.host,
                    port=self.port
                )
                logging.info("Database connection established.")
            except Exception as e:
                logging.error(f"Error connecting to database: {e}")

    def close(self):
        if self.connection and not self.connection.closed:
            self.connection.close()
            logging.info("Database connection closed.")

    def execute_query(self, query, params=None):
        if self.connection is None or self.connection.closed:
           raise ConnectionError("Database connection is not established.")
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                self.connection.commit()
                logging.info("Query executed successfully.")
        except Exception as e:
            logging.error(f"Error executing query: {e}")

    def fetch_data(self, query):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Error fetching data: {e}")
            return None

    def fetch_data_with_params(self, query, params):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Error fetching data: {e}")
            return None


    def insert_bulk_data(self, table, columns, data):
        if self.connection is None or self.connection.closed:
           raise ConnectionError("Database connection is not established.")
        try:
            with self.connection.cursor() as cursor:
                query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES %s"
                execute_values(cursor, query, data)
                self.connection.commit()
                logging.info("Data inserted successfully.")
        except Exception as e:
            self.connection.rollback()
            logging.error(f"Error inserting data: {e}")

    def load_data_from_dataframe(self,table,dataframe):
        columns = list(dataframe.columns)
        data = [tuple(x) for x in dataframe.to_numpy()]
        self.insert_bulk_data(table, columns, data)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


