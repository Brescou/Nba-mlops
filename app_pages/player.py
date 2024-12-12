import streamlit as st
import pandas as pd
import plotly.express as px
import logging
from utils.utils import fetch_seasons

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.title("NBA Player Stats")

db = st.session_state["db_instance"]

st.title("Recherche de Joueur")

search_container, main_container = st.columns([1, 4])

with search_container:
    st.markdown("### Recherches")

    seasons = fetch_seasons(db)
    selected_season = st.selectbox("Saison", seasons, index=0, key="saison")

    players_query = """
        SELECT DISTINCT p.player_id, p.firstname, p.lastname 
        FROM player p
        JOIN player_boxscore pb ON p.player_id = pb.player_id
        WHERE pb.season_year = %s
        ORDER BY p.lastname, p.firstname
    """
    players = db.fetch_dataframe(players_query, (selected_season,))

    players_names = {
        f"{row['firstname']} {row['lastname']}": row["player_id"]
        for _, row in players.iterrows()
    }
    selected_player = st.selectbox(
        "Joueur", players_names.keys(), index=0, key="player"
    )

    if selected_player:
        player_id = players_names[selected_player]

        player_profile_query = """
            SELECT p.player_id, p.firstname, p.lastname, p.position, p.weight,
            p.height, p.country, p.draft_year, p.draft_number, t.name AS current_team,
            ARRAY_AGG(DISTINCT t_hist.name) AS teams_played
            FROM player p
            LEFT JOIN team t ON p.team_id = t.team_id
            LEFT JOIN player_boxscore pb ON p.player_id = pb.player_id
            LEFT JOIN team t_hist ON pb.team_id = t_hist.team_id
            WHERE p.player_id = %s
            GROUP BY p.player_id, t.name
        """

        player_profile = db.fetch_dataframe(player_profile_query, (player_id,))

        # Get season-by-season base stats
        season_stats_query = """
            SELECT 
                pb.season_year,
                t.name AS team_name,
                COUNT(pb.game_id) as games_played,
                ROUND(AVG(pbb.pts)::numeric, 1) as ppg,
                ROUND(AVG(pbb.reb)::numeric, 1) as rpg, 
                ROUND(AVG(pbb.ast)::numeric, 1) as apg,
                ROUND(AVG(pbb.stl)::numeric, 1) as spg,
                ROUND(AVG(pbb.blk)::numeric, 1) as bpg,
                ROUND(AVG(pbb.fgm)::numeric, 1) as fgm,
                ROUND(AVG(pbb.fga)::numeric, 1) as fga,
                ROUND(AVG(pbb.fg_pct)::numeric, 3) as fg_pct,
                ROUND(AVG(pbb.fg3m)::numeric, 1) as fg3m,
                ROUND(AVG(pbb.fg3a)::numeric, 1) as fg3a,
                ROUND(AVG(pbb.fg3_pct)::numeric, 3) as fg3_pct,
                ROUND(AVG(pbb.ftm)::numeric, 1) as ftm,
                ROUND(AVG(pbb.fta)::numeric, 1) as fta,
                ROUND(AVG(pbb.ft_pct)::numeric, 3) as ft_pct
            FROM player_boxscore pb
            JOIN player_boxscore_base pbb ON pb.boxscore_id = pbb.boxscore_id
            JOIN team t ON pb.team_id = t.team_id
            WHERE pb.player_id = %s
            GROUP BY pb.season_year, t.name
            ORDER BY pb.season_year DESC
        """

        season_stats = db.fetch_dataframe(season_stats_query, (player_id,))

        monthly_stats_query = """
            SELECT 
                EXTRACT(MONTH FROM pb.game_date) AS month,
                t.name AS team_name,
                COUNT(pb.game_id) as games_played,
                ROUND(AVG(pbb.pts)::numeric, 1) as ppg,
                ROUND(AVG(pbb.reb)::numeric, 1) as rpg,
                ROUND(AVG(pbb.ast)::numeric, 1) as apg,
                ROUND(AVG(pbb.stl)::numeric, 1) as spg,
                ROUND(AVG(pbb.blk)::numeric, 1) as bpg,
                ROUND(AVG(pbb.fgm)::numeric, 1) as fgm,
                ROUND(AVG(pbb.fga)::numeric, 1) as fga,
                ROUND(AVG(pbb.fg_pct)::numeric, 3) as fg_pct,
                ROUND(AVG(pbb.fg3m)::numeric, 1) as fg3m,
                ROUND(AVG(pbb.fg3a)::numeric, 1) as fg3a,
                ROUND(AVG(pbb.fg3_pct)::numeric, 3) as fg3_pct,
                ROUND(AVG(pbb.ftm)::numeric, 1) as ftm,
                ROUND(AVG(pbb.fta)::numeric, 1) as fta,
                ROUND(AVG(pbb.ft_pct)::numeric, 3) as ft_pct
            FROM player_boxscore pb
            JOIN player_boxscore_base pbb ON pb.boxscore_id = pbb.boxscore_id
            JOIN team t ON pb.team_id = t.team_id
            WHERE pb.player_id = %s AND pb.season_year = %s
            GROUP BY month, t.name
            ORDER BY month
        """

        monthly_stats = db.fetch_dataframe(
            monthly_stats_query, (player_id, selected_season)
        )

        # Créer un dictionnaire pour mapper les numéros de mois aux noms
        mois_dict = {
            1: "Janvier",
            2: "Février",
            3: "Mars",
            4: "Avril",
            5: "Mai",
            6: "Juin",
            7: "Juillet",
            8: "Août",
            9: "Septembre",
            10: "Octobre",
            11: "Novembre",
            12: "Décembre",
        }

        # Convertir la colonne month en noms de mois
        monthly_stats["month_name"] = monthly_stats["month"].map(mois_dict)

        if not player_profile.empty and not season_stats.empty:
            player_info = player_profile.iloc[0]
            teams_played = ", ".join(player_info["teams_played"])
            image_url = f"https://cdn.nba.com/headshots/nba/latest/260x190/{player_info['player_id']}.png"

            with main_container:
                col_profile, col_stats = st.columns([1, 3])
                with col_profile:
                    st.markdown("### **Carte de Profil du Joueur**")
                    st.markdown(
                        f"""
                        <div style="
                            border: 1px solid #ddd; 
                            padding: 15px; 
                            border-radius: 8px; 
                            background-color: #f9f9f9;
                            text-align: center;
                        ">
                            <img src="{image_url}" 
                                alt="Player Image" 
                                style="
                                    width: 100px; 
                                    height: 100px;
                                    object-fit: cover;
                                    border-radius: 8px;
                                    margin-bottom: 15px;
                            ">
                            <div style="text-align: left;">
                                <strong>Nom :</strong> {player_info["firstname"]} {player_info["lastname"]}
                                <br><strong>Position :</strong> {player_info["position"]}
                                <br><strong>Poids :</strong> {player_info["weight"]} lbs ( {(player_info["weight"] * 0.453592).round(1)} kg )
                                <br><strong>Taille :</strong> {int(player_info["height"] // 12)} ft {int(player_info["height"] % 12)} in ({int(player_info["height"] * 2.54)} cm)
                                <br><strong>Pays :</strong> {player_info["country"]}
                                <br><strong>Draft :</strong> {player_info["draft_year"]}, Rang : {player_info["draft_number"]}
                                <br><strong>Équipe actuelle :</strong> {player_info["current_team"]}
                                <br><strong>Équipes jouées :</strong> {teams_played}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with col_stats:
                    st.markdown("### **Statistiques Saison par Saison**")
                    if not season_stats.empty:
                        for col in [
                            "ppg",
                            "rpg",
                            "apg",
                            "spg",
                            "bpg",
                            "fg_pct",
                            "fg3_pct",
                            "ft_pct",
                            "fgm",
                            "fga",
                            "ftm",
                            "fg3m",
                            "fg3a",
                            "fta",
                        ]:
                            if col in season_stats.columns:
                                season_stats[col] = pd.to_numeric(
                                    season_stats[col], errors="coerce"
                                ).fillna(0)

                        selected_season_stats = st.multiselect(
                            "Statistiques à afficher",
                            [
                                "ppg",
                                "rpg",
                                "apg",
                                "spg",
                                "bpg",
                                "fg_pct",
                                "fg3_pct",
                                "ft_pct",
                                "fgm",
                                "fga",
                                "ftm",
                                "fg3m",
                                "fg3a",
                                "fta",
                            ],
                            default=["ppg", "rpg", "apg"],
                        )

                        if selected_season_stats:
                            fig_career = px.bar(
                                season_stats.melt(
                                    id_vars=["season_year"],
                                    value_vars=selected_season_stats,
                                ),
                                x="season_year",
                                y="value",
                                color="variable",
                                barmode="group",
                            )
                            st.plotly_chart(fig_career, use_container_width=True)
                        else:
                            st.warning(
                                "Veuillez sélectionner au moins une statistique à afficher."
                            )

                    else:
                        st.warning(
                            "Aucune donnée de statistiques saison par saison disponible pour ce joueur."
                        )

                col_monthly_stats, col_monthly_percentages = st.columns(2)

                with col_monthly_stats:
                    st.markdown("### **Sélectionnez les Statistiques Mensuelles**")
                    selected_monthly_stats = st.multiselect(
                        "Statistiques à afficher",
                        monthly_stats.columns.difference(["month"]),
                        default=["ppg", "rpg", "apg"],
                    )
                    if selected_monthly_stats:
                        fig_monthly_stats = px.line(
                            monthly_stats,
                            x="month_name",
                            y=selected_monthly_stats,
                            title="Statistiques Mensuelles Moyennes",
                            labels={"month_name": "Mois", "value": "Moyenne"},
                        )
                        fig_monthly_stats.update_xaxes(tickangle=45)
                        st.plotly_chart(fig_monthly_stats, use_container_width=True)
                    else:
                        st.warning(
                            "Veuillez sélectionner au moins une statistique à afficher."
                        )

                with col_monthly_percentages:
                    st.markdown("### **Sélectionnez les Pourcentages Mensuels**")
                    selected_monthly_percentages = st.multiselect(
                        "Pourcentages à afficher",
                        ["fg_pct", "fg3_pct", "ft_pct"],
                        default=["fg_pct", "fg3_pct"],
                    )
                    if selected_monthly_percentages:
                        fig_monthly_percentages = px.line(
                            monthly_stats,
                            x="month_name",
                            y=selected_monthly_percentages,
                            title="Pourcentages Mensuels Moyens",
                            labels={"month_name": "Mois", "value": "Moyenne"},
                        )
                        fig_monthly_percentages.update_xaxes(tickangle=45)
                        st.plotly_chart(
                            fig_monthly_percentages, use_container_width=True
                        )
