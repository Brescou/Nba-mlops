import streamlit as st

games_page = st.Page("app_pages/games.py", title="Games", default=True)
player_page = st.Page("app_pages/player.py", title="Player")
team_page = st.Page("app_pages/team.py", title="Team")
game_page = st.Page("app_pages/game.py", title="Game")

def navigate_to_page(pages):
    """Handle page navigation through sidebar selection."""
    # Si une page spécifique est passée, l'utiliser directement
    if isinstance(pages, list) and len(pages) == 1:
        selected_page = pages[0]
        # Mettre à jour le selectbox pour refléter la page active
        st.session_state["page"] = selected_page.title
    else:
        # Sinon utiliser le selectbox pour la navigation
        page_titles = [page.title for page in pages]
        current_page = st.session_state.get("page", "Games")
        selected_page_title = st.sidebar.selectbox("Choose a page", page_titles, 
                                                 index=page_titles.index(current_page))
        selected_page = next(page for page in pages if page.title == selected_page_title)
        st.session_state["page"] = selected_page_title
    
    pg = st.navigation([selected_page])
    pg.run()
    
    
def navigate_to_game_page(game_id):
    st.session_state["selected_game_id"] = game_id
    navigate_to_page([game_page])
    
