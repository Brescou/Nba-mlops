import streamlit as st
import psycopg2
import pandas as pd
import altair as alt


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


def get_stats(player_id, season_year=None, selected_stats=None):
    try:
        conn = psycopg2.connect(
            dbname="nba_db",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        selected_columns = ", ".join([f"AVG(pb_base.{stat}) AS \"{stat}\"" for stat in selected_stats])
        if season_year:
            query = f"""
                SELECT DATE_TRUNC('month', pb.game_date) AS month,
                       {selected_columns}
                FROM public.player_boxscore pb
                JOIN public.player_boxscore_base pb_base ON pb.boxscore_id = pb_base.boxscore_id
                WHERE pb.player_id = %s AND pb.season_year = %s
                GROUP BY month
                ORDER BY month;
            """
            cursor.execute(query, (player_id, season_year))
            columns = ["Month"] + selected_stats
        else:
            query = f"""
                SELECT pb.season_year AS season,
                       {selected_columns}
                FROM public.player_boxscore pb
                JOIN public.player_boxscore_base pb_base ON pb.boxscore_id = pb_base.boxscore_id
                WHERE pb.player_id = %s
                GROUP BY pb.season_year
                ORDER BY pb.season_year;
            """
            cursor.execute(query, (player_id,))
            columns = ["Season"] + selected_stats
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        df = pd.DataFrame(data, columns=columns)
        for stat in selected_stats:
            df[stat] = df[stat].astype(float)
        return df
    except Exception as e:
        st.error(f"Error fetching stats: {e}")
        return pd.DataFrame()


def get_stat_columns():
    try:
        conn = psycopg2.connect(
            dbname="nba_db",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        query = "SELECT column_name FROM information_schema.columns WHERE table_name = 'player_boxscore_base';"
        cursor.execute(query)
        columns = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        count_stats = [col for col in columns if not col.endswith('_pct') and col != 'boxscore_id']
        percent_stats = [col for col in columns if col.endswith('_pct')]
        return count_stats, percent_stats
    except Exception as e:
        st.error(f"Error fetching column names: {e}")
        return [], []


st.title("Player Page")
count_stats, percent_stats = get_stat_columns()

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        player_names = get_players()
        selected_player_id = st.selectbox("Select a player:", list(player_names.keys()),
                                          format_func=lambda x: player_names[x])
    with col2:
        seasons = get_player_seasons(selected_player_id)
        selected_season = st.selectbox("Select a season:", seasons)

if selected_player_id:
    player = get_player_details(selected_player_id)
    if player:
        firstname, lastname, position, team_name, team_city, jersey_number, height, weight, college, country, draft_year, draft_number, from_year, to_year = player
        image_url = f"https://cdn.nba.com/headshots/nba/latest/260x190/{selected_player_id}.png"
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(
                f"""
                <div style='text-align: center;'>
                    <img src="{image_url}" alt="{firstname} {lastname}" style='width: 150px; height: 150px; border-radius: 50%; object-fit: cover; margin-bottom: 1rem;'/>
                    <h2>{firstname} {lastname}</h2>
                    <p><strong>Position:</strong> {position}</p>
                    <p><strong>Team:</strong> {team_city} {team_name}</p>
                    <p><strong>Jersey Number:</strong> {jersey_number}</p>
                    <p><strong>Height:</strong> {int(height // 12)} ft {int(height % 12)} in</p>
                    <p><strong>Weight:</strong> {weight} lbs</p>
                    <p><strong>College:</strong> {college}</p>
                    <p><strong>Country:</strong> {country}</p>
                    <p><strong>Draft Year:</strong> {draft_year}</p>
                    <p><strong>Draft Number:</strong> {draft_number}</p>
                    <p><strong>From Year:</strong> {from_year}</p>
                    <p><strong>To Year:</strong> {to_year}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col2:
            selected_counting_stats = st.multiselect("Select counting statistics to plot", count_stats,
                                                     default=["pts", "reb", "ast"])
            selected_percentage_stats = st.multiselect("Select percentage statistics to plot", percent_stats,
                                                       default=["fg_pct"])

            if selected_counting_stats or selected_percentage_stats:
                points_df = get_stats(selected_player_id, selected_season,
                                      selected_counting_stats + selected_percentage_stats)
                if not points_df.empty:
                    points_df['Month'] = points_df['Month'].dt.strftime('%b-%Y') if selected_season else points_df[
                        'Season']
                    points_df = points_df.reset_index(drop=True)

                    if selected_counting_stats:
                        chart_data_counting = points_df.melt(id_vars=['Month' if selected_season else 'Season'],
                                                             value_vars=selected_counting_stats, var_name='Statistic',
                                                             value_name='Value')
                        # stats in float

                        line_chart_counting = alt.Chart(chart_data_counting).mark_line().encode(
                            x=alt.X(
                                'Month' if selected_season else 'Season',
                                title='Month-Year' if selected_season else 'Season',
                                sort=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov',
                                      'Dec']
                            ),
                            y=alt.Y('Value', title="Counting Values"),
                            color='Statistic'
                        ).properties(title="Counting Statistics")
                        st.altair_chart(line_chart_counting, use_container_width=True)

                    if selected_percentage_stats:
                        chart_data_percentage = points_df.melt(id_vars=['Month' if selected_season else 'Season'],
                                                               value_vars=selected_percentage_stats,
                                                               var_name='Statistic', value_name='Value')
                        line_chart_percentage = alt.Chart(chart_data_percentage).mark_line().encode(
                            x=alt.X(
                                'Month' if selected_season else 'Season',
                                title='Month-Year' if selected_season else 'Season',
                                sort=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov',
                                      'Dec']
                            ),
                            y=alt.Y('Value', title="Percentage Values", scale=alt.Scale(domain=[0, 1])),
                            color='Statistic'
                        ).properties(title="Percentage Statistics")
                        st.altair_chart(line_chart_percentage, use_container_width=True)
