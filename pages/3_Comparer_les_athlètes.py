import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts
from datetime import datetime
from database.DatabaseManager import DatabaseManager 


def create_radar(filtered_datasets):
    option = {
        "legend": {"data": []},
        "tooltip": {
            "trigger": "item",
        },
        "radar": {
            "indicator": [
                {"name": "Total jumps", "max": 50, "axisLabel": {"show": True}},
                {"name": "Success rate (%)", "max": 100, "min": 50, "axisLabel": {"show": True}},
                {"name": "Average angular velocity (turns/s)", "max": 4, "axisLabel": {"show": True}},
                {"name": "Average flight time (s)", "max": 2, "min": 0, "axisLabel": {"show": True}},
                {"name": "Jumps/hr", "max": 50, "axisLabel": {"show": True}},
            ]
        },
        "series": []
    }

    for data in filtered_datasets:
        if data.shape[0] > 0:
            option["legend"]["data"].append(str(data['skater_name'].unique()[0]))
            option["series"].append({
                "name": str(data['skater_name'].unique()[0]),
                "type": "radar",
                "data": [{
                    "value": [
                        int(data.shape[0]),
                        round(float(data['jump_success'].mean()),1)*100,
                        3.2,
                        0.5,
                        42,
                    ],
                    "name": str(data['skater_name'].unique()[0]),
                }]
            })

    if option["series"]:
        st_echarts(option, height="500px")
    else:
        st.write("Désolé, il n'y a pas de données à afficher.")

if st.session_state.logged_in:
    access = st.session_state.user['access']
    role = st.session_state.user['role']
    jumps = st.session_state.jumps

    # Add a jump_type filter
    jump_types = []
    for jump in jumps:
        jump_types.extend(jump['jump_type'].unique())
    jump_types = list(set(jump_types))
    selected_jump_type = st.sidebar.selectbox("Sélectionner un type de saut", jump_types)

    # Add a jump_rotations filter
    jump_rotations = []
    for jump in jumps:
        jump_rotations.extend(jump['jump_rotations'].unique())
    jump_rotations = list(set(jump_rotations))
    selected_jump_rotations = st.sidebar.selectbox("Sélectionner un nombre de rotations", jump_rotations)

    # Filter the datasets
    filtered_datasets = []
    for jump in jumps:
        filtered_jump = jump[(jump['jump_type'] == selected_jump_type) & (jump['jump_rotations'] == selected_jump_rotations)]
        filtered_datasets.append(filtered_jump)
       
    create_radar(filtered_datasets)