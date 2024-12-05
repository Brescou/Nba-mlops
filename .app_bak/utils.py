import logging

import pandas as pd

logging.basicConfig(level=logging.INFO)


def fetch_seasons(db):
    query = "select distinct season_year from game order by season_year desc;"
    try:
        return db.fetch_dataframe(query)
    except Exception as e:
        logging.error(f"Error fetching seasons: {e}")
        return []


def fetch_games_by_season(db, season):
    query = f"""select g.game_id,
                       g.date,
                       t1.name  AS home_team_name,
                       t2.name  AS away_team_name,
                       tbb1.pts AS home_team_score,
                       tbb2.pts AS away_team_score
                from game g
                join team t1 ON g.home_team_id = t1.team_id
                join team t2 ON g.away_team_id = t2.team_id
                join team_boxscore tb1 ON g.game_id = tb1.game_id AND tb1.team_id = g.home_team_id
                join team_boxscore tb2 ON g.game_id = tb2.game_id AND tb2.team_id = g.away_team_id
                join team_boxscore_base tbb1 ON tb1.boxscore_id = tbb1.boxscore_id
                join team_boxscore_base tbb2 ON tb2.boxscore_id = tbb2.boxscore_id
                where g.season_year = '2021-22'
                order by g.date;
"""
    try:
        return db.fetch_dataframe(query)
    except Exception as e:
        logging.error(f"Error fetching games: {e}")
        return []


def fetch_game_details(db, game_id):
    query = f"""
        SELECT 
            g.date,
            t1.name AS home_team_name,
            t2.name AS away_team_name,
            tbb1.pts AS home_team_score,
            tbb2.pts AS away_team_score
        FROM 
            game g
        JOIN 
            team t1 ON g.home_team_id = t1.team_id
        JOIN 
            team t2 ON g.away_team_id = t2.team_id
        JOIN 
            team_boxscore tb1 ON g.game_id = tb1.game_id AND tb1.team_id = g.home_team_id
        JOIN 
            team_boxscore_base tbb1 ON tb1.boxscore_id = tbb1.boxscore_id
        JOIN 
            team_boxscore tb2 ON g.game_id = tb2.game_id AND tb2.team_id = g.away_team_id
        JOIN 
            team_boxscore_base tbb2 ON tb2.boxscore_id = tbb2.boxscore_id
        WHERE 
            g.game_id = '{game_id}';
    """
    try:
        return db.fetch_dataframe(query)
    except Exception as e:
        logging.error(f"Error fetching game details: {e}")
        return pd.DataFrame()
