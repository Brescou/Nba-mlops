import streamlit as st
import psycopg2
import pandas as pd

def get_players():
    try:
        conn = psycopg2.connect(
            dbname="nba_db",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        query = "SELECT player_id, firstname, lastname FROM public.player ORDER BY lastname;"
        cursor.execute(query)
        players = cursor.fetchall()
        player_names = {player_id: f"{first} {last}" for player_id, first, last in players}
        cursor.close()
        conn.close()
        return player_names
    except Exception as e:
        st.error(f"Error fetching players: {e}")
        return {}

def get_player_details(player_id):
    try:
        conn = psycopg2.connect(
            dbname="nba_db",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        query = """
            SELECT p.firstname, p.lastname, p.position, t.name AS team_name, t.city AS team_city, 
                   p.jersey_number, p.height, p.weight, p.college, p.country, 
                   p.draft_year, p.draft_number, p.from_year, p.to_year
            FROM public.player p
            JOIN public.team t ON p.team_id = t.team_id
            WHERE p.player_id = %s;
        """
        cursor.execute(query, (player_id,))
        player = cursor.fetchone()
        cursor.close()
        conn.close()
        return player
    except Exception as e:
        st.error(f"Error fetching player details: {e}")
        return None

def get_player_seasons(player_id):
    try:
        conn = psycopg2.connect(
            dbname="nba_db",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        query = """
            SELECT DISTINCT season_year
            FROM public.player_boxscore
            WHERE player_id = %s
            ORDER BY season_year;
        """
        cursor.execute(query, (player_id,))
        seasons = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return seasons
    except Exception as e:
        st.error(f"Error fetching seasons: {e}")
        return []

def get_monthly_points(player_id, season_year):
    try:
        conn = psycopg2.connect(
            dbname="nba_db",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        query = """
            SELECT DATE_TRUNC('month', pb.game_date) AS month, AVG(pb_base.pts) AS avg_points
            FROM public.player_boxscore pb
            JOIN public.player_boxscore_base pb_base ON pb.boxscore_id = pb_base.boxscore_id
            WHERE pb.player_id = %s AND pb.season_year = %s
            GROUP BY month
            ORDER BY month;
        """
        cursor.execute(query, (player_id, season_year))
        monthly_data = cursor.fetchall()
        cursor.close()
        conn.close()
        return pd.DataFrame(monthly_data, columns=['Month', 'Average Points'])
    except Exception as e:
        st.error(f"Error fetching monthly points: {e}")
        return pd.DataFrame(columns=['Month', 'Average Points'])

st.title("Player Page")

player_names = get_players()
selected_player_id = st.selectbox("Select a player:", list(player_names.keys()), format_func=lambda x: player_names[x])

if selected_player_id:
    player = get_player_details(selected_player_id)
    if player:
        firstname, lastname, position, team_name, team_city, jersey_number, height, weight, college, country, draft_year, draft_number, from_year, to_year = player

        st.markdown(f"### {firstname} {lastname}")
        st.write(f"**Position:** {position}")
        st.write(f"**Team:** {team_city} {team_name}")
        st.write(f"**Jersey Number:** {jersey_number}")
        st.write(f"**Height:** {int(height // 12)} ft {int(height % 12)} in")
        st.write(f"**Weight:** {weight} lbs")
        st.write(f"**College:** {college}")
        st.write(f"**Country:** {country}")
        st.write(f"**Draft Year:** {draft_year}")
        st.write(f"**Draft Number:** {draft_number}")
        st.write(f"**From Year:** {from_year}")
        st.write(f"**To Year:** {to_year}")

        seasons = get_player_seasons(selected_player_id)
        selected_season = st.selectbox("Select a season:", seasons)

        if selected_season:
            monthly_points_df = get_monthly_points(selected_player_id, selected_season)
            st.line_chart(monthly_points_df.set_index('Month'), use_container_width=True)
