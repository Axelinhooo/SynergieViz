import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="SynergieViz - Welcome",
    page_icon=":bar_chart:",
)

st.title("Welcome to SynergieViz")
st.write("This is the landing page of your SynergieViz application.")


