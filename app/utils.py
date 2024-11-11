import streamlit as st


def colorize_multiselect_options(colors: list[str]) -> None:
    rules = ""
    n_colors = len(colors)

    for i, color in enumerate(colors):
        rules += f""".stMultiSelect div[data-baseweb="select"] span[data-baseweb="tag"]:nth-child({n_colors}n+{i + 1}){{background-color: {color};}}"""

    st.markdown(f"<style>{rules}</style>", unsafe_allow_html=True)
