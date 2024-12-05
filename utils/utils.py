import logging
from random import randint
import time
import streamlit as st
from matplotlib.patches import Circle, Rectangle, Arc
import matplotlib.pyplot as plt

import pandas as pd

logging.basicConfig(level=logging.INFO)

def get_unique_key_id():
    return f"{int(time.time())}_{randint(0, 1000000)}"
def go_to_previous_page():
    st.session_state["current_page"] -= 1


def go_to_next_page():
    st.session_state["current_page"] += 1


def fetch_seasons(db):
    query = "select distinct season_year from game order by season_year desc;"
    try:
        return db.fetch_dataframe(query)
    except Exception as e:
        logging.error(f"Error fetching seasons: {e}")
        return []


def fetch_games_by_season(db, season):
    query = """
        select g.game_id,
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
        where g.season_year = %s
        order by g.date;
    """
    try:
        return db.fetch_dataframe(query, (season,))
    except Exception as e:
        logging.error(f"Error fetching games: {e}")
        return pd.DataFrame()


def fetch_game_details(db, game_id):
    query = """
        SELECT 
            g.date,
            t1.name AS home_team_name,
            t1.team_id AS home_team_id,  
            t2.name AS away_team_name,
            t2.team_id AS away_team_id,
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
            g.game_id = %s;
    """
    try:
        return db.fetch_dataframe(query, (game_id,))
    except Exception as e:
        logging.error(f"Error fetching game details: {e}")
        return pd.DataFrame()


def fetch_play_by_play(db, game_id):
    query = """
        SELECT 
            action_id,
            action_number,
            clock,
            elapsed,
            period,
            p.team_id,
            p.player_id,
            score_home,
            score_away,
            points_total,
            location,
            description,
            action_type,
            sub_type,
            t.name AS team_name,
            CONCAT(pl.firstname, ' ', pl.lastname) AS player_name
        FROM play_by_play p
        LEFT JOIN team t ON p.team_id = t.team_id
        LEFT JOIN player pl ON p.player_id = pl.player_id
        WHERE p.game_id = %s
        ORDER BY p.period, clock DESC
    """
    try:
        return db.fetch_dataframe(query, (game_id,))
    except Exception as e:
        logging.error(f"Error fetching play by play: {e}")
        return pd.DataFrame()
    
    
def draw_court(ax=None, color='black', lw=2,outer_lines=False):
    if ax is None:
        ax = plt.gca()
        
    hoop = Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False)

    backboard = Rectangle((-30, -7.5), 60, -1, linewidth=lw, color=color)

    outer_box = Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color,
                          fill=False)
    inner_box = Rectangle((-60, -47.5), 120, 190, linewidth=lw, color=color,
                          fill=False)

    top_free_throw = Arc((0, 142.5), 120, 120, theta1=0, theta2=180,
                         linewidth=lw, color=color, fill=False)
    bottom_free_throw = Arc((0, 142.5), 120, 120, theta1=180, theta2=0,
                            linewidth=lw, color=color, linestyle='dashed')
    restricted = Arc((0, 0), 80, 80, theta1=0, theta2=180, linewidth=lw,
                     color=color)

    corner_three_a = Rectangle((-220, -47.5), 0, 140, linewidth=lw,
                               color=color)
    corner_three_b = Rectangle((220, -47.5), 0, 140, linewidth=lw, color=color)
    three_arc = Arc((0, 0), 475, 475, theta1=22, theta2=158, linewidth=lw,
                    color=color)
    center_outer_arc = Arc((0, 422.5), 120, 120, theta1=180, theta2=0,
                           linewidth=lw, color=color)
    center_inner_arc = Arc((0, 422.5), 40, 40, theta1=180, theta2=0,
                           linewidth=lw, color=color)

    court_elements = [hoop, backboard, outer_box, inner_box, top_free_throw,
                      bottom_free_throw, restricted, corner_three_a,
                      corner_three_b, three_arc, center_outer_arc,
                      center_inner_arc]

    if outer_lines:
        outer_lines = Rectangle((-250, -47.5), 500, 470, linewidth=lw,
                                color=color, fill=False)
        court_elements.append(outer_lines)

    for element in court_elements:
        ax.add_patch(element)

    return ax
