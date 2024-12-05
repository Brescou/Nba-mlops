import os

import pandas as pd
import psycopg2

import logging

from psycopg2.extras import execute_values
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO)


class DB:
    def __init__(self):
        self.dbname = os.getenv("DB_NAME", "nba_db")
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "postgres")
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "5432")
        self.connection = None
        self.engine = None
        self.Session = None

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
                db_url = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"
                self.engine = create_engine(db_url)
                self.Session = sessionmaker(bind=self.engine)
            except Exception as e:
                logging.error(f"Error connecting to database: {e}")

    def close(self):
        if self.connection and not self.connection.closed:
            self.connection.close()
            logging.info("Database connection closed.")
        if self.engine:
            self.engine.dispose()
            logging.info("Database engine disposed.")
        if self.Session:
            self.Session.close_all()
            logging.info("Database session closed.")

    def execute_query(self, query, params=None):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                self.connection.commit()
                logging.info("Query executed successfully.")
        except Exception as e:
            logging.error(f"Error executing query: {e}")
            logging.error(f"Query: {query}")
            logging.error(f"Params: {params}")
            

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

    def fetch_dataframe(self, query, params=None):
        try:
            if params:
                return pd.read_sql_query(query, self.engine, params=params)
            return pd.read_sql_query(query, self.engine)
        except Exception as e:
            logging.error(f"Error executing query: {e}")
            logging.error(f"Query: {query}")
            logging.error(f"Params: {params}")
            return pd.DataFrame()

    def insert_bulk_data(self, table, columns, data):
        try:
            with self.connection.cursor() as cursor:
                query = f"""
                    INSERT INTO {table} ({', '.join(columns)}) VALUES %s
                    ON CONFLICT (boxscore_id) DO UPDATE
                    SET {', '.join(f"{col} = EXCLUDED.{col}" for col in columns if col != 'boxscore_id')}
                """
                execute_values(cursor, query, data)
                self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            logging.error(f"Error inserting data: {e}")

    def insert_one_row(self, table, columns, data_row):
        try:
            with self.connection.cursor() as cursor:
                query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(data_row))})"
                cursor.execute(query, data_row)
                self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            logging.error(f"Error inserting row {data_row}: {e}")


    def load_data_from_dataframe(self, table, dataframe):
        columns = list(dataframe.columns)
        for data_row in dataframe.itertuples(index=False):
            data_row = [int(x) if isinstance(x, np.int64) else (x if pd.notna(x) else None) for x in data_row]
            self.insert_one_row(table, columns, data_row)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
