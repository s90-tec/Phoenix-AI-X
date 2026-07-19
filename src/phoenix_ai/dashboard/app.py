"""Streamlit presentation entry point; intentionally contains no market logic."""

import streamlit as st

st.set_page_config(page_title="Phoenix AI X", page_icon=":material/insights:", layout="wide")
st.title("Phoenix AI X")
st.caption("Autonomous quantitative research platform — foundation environment")
with st.container(border=True):
    st.subheader("Platform status")
    st.info("No research, backtesting, paper-trading, or live-trading workflow is enabled yet.")

