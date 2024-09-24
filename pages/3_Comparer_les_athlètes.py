import math
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_echarts import st_echarts

from database.DatabaseManager import DatabaseManager


def create_radar_athletes(filtered_datasets):
    # Définir le nombre maximal de sauts pour l'axe radar
    max_jumps = max([data.shape[0] for data in filtered_datasets]) + 1
    # arrondir au nombre divisible par 5 supérieur
    for i in range(1, 6):
        if max_jumps % 5 == 0:
            break
        max_jumps += 1
    
    # Définir une liste de couleurs fixes
    colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#8c564b', '#64e572', '#fd8664', '#8a9899', '#e4c2d5']
    
    option = {
        "legend": {"data": []},
        "tooltip": {
            "trigger": "item",
        },
        "radar": {
            "indicator": [
                {"name": "Total de sauts", "max": max_jumps, "axisLabel": {"show": True}},
                {"name": "Taux de réussite (%)", "max": 100, "min": 0, "axisLabel": {"show": True}},
                {"name": "Vitesse angulaire max (tours/s)", "max": 6, "axisLabel": {"show": True}},
                {"name": "Durée de saut(s)", "max": 1, "min": 0, "axisLabel": {"show": True}},
                {"name": "Sauts par entraînement", "max": 50, "min": 0, "axisLabel": {"show": True}},
            ]
        },
        "series": [],
    }

    for index, data in enumerate(filtered_datasets):
        if data.shape[0] > 0:
            athlete_name = str(data["skater_name"].unique()[0])
            option["legend"]["data"].append(athlete_name)
            option["series"].append(
                {
                    "name": athlete_name,
                    "type": "radar",
                    "itemStyle": {"color": colors[index % len(colors)]},  # Attribuer une couleur fixe
                    "lineStyle": {"color": colors[index % len(colors)]},  # Assurer que la ligne a la même couleur
                    "data": [
                        {
                            "value": [
                                int(data.shape[0]),
                                round(float(data["jump_success"].mean()), 1) * 100,
                                round(float(data["jump_max_speed"].mean()), 1),
                                round(float(data["jump_length"].mean()), 2),
                                round(int(data.shape[0]) / int(data["training_date"].nunique()), 1),
                            ],
                            "name": athlete_name,
                        }
                    ],
                }
            )

    if option["series"]:
        st_echarts(option, height="500px")
    else:
        st.write("Désolé, il n'y a pas de données à afficher.")

def create_radar_types(filtered_datasets):
    # Définir le nombre maximal de sauts pour l'axe radar
    max_jumps = max([data.shape[0] for data in filtered_datasets]) + 1
    # arrondir au nombre divisible par 5 supérieur
    for i in range(1, 6):
        if max_jumps % 5 == 0:
            break
        max_jumps += 1
    
    # Définir une liste de couleurs fixes
    colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#8c564b', '#64e572', '#fd8664', '#8a9899', '#e4c2d5']
    
    option = {
        "legend": {"data": []},
        "tooltip": {
            "trigger": "item",
        },
        "radar": {
            "indicator": [
                {"name": "Total de sauts", "max": max_jumps, "axisLabel": {"show": True}},
                {"name": "Taux de réussite (%)", "max": 100, "min": 0, "axisLabel": {"show": True}},
                {"name": "Vitesse angulaire max (tours/s)", "max": 6, "axisLabel": {"show": True}},
                {"name": "Durée de saut(s)", "max": 1, "min": 0, "axisLabel": {"show": True}},
                {"name": "Sauts par entraînement", "max": 50, "min": 0, "axisLabel": {"show": True}},
            ]
        },
        "series": [],
    }

    for index, data in enumerate(filtered_datasets):
        if data.shape[0] > 0:
            jump_type = str(data["jump_type"].unique()[0])
            option["legend"]["data"].append(jump_type)
            option["series"].append(
                {
                    "name": jump_type,
                    "type": "radar",
                    "itemStyle": {"color": colors[index % len(colors)]},  # Attribuer une couleur fixe
                    "lineStyle": {"color": colors[index % len(colors)]},  # Assurer que la ligne a la même couleur
                    "data": [
                        {
                            "value": [
                                int(data.shape[0]),
                                round(float(data["jump_success"].mean()), 1) * 100,
                                round(float(data["jump_max_speed"].mean()), 1),
                                round(float(data["jump_length"].mean()), 2),
                                round(int(data.shape[0]) / int(data["training_date"].nunique()), 1),
                            ],
                            "name": jump_type,
                        }
                    ],
                }
            )

    if option["series"]:
        st_echarts(option, height="500px")
    

def create_line_chart(filtered_datasets):
    # Préparer les données pour le graphique en ligne
    line_data = []
    # Mettre la colonne 'training_date' au format datetime
    filtered_datasets = [data.assign(training_date=pd.to_datetime(data["training_date"])) for data in filtered_datasets]

    for data in filtered_datasets:
        if data.shape[0] > 0:
            data["month"] = data["training_date"].dt.to_period("M").astype(str)
            monthly_success_rate = (
                data.groupby("month")["jump_success"].mean().reset_index()
            )
            monthly_success_rate["skater_name"] = data["skater_name"].unique()[0]
            line_data.append(monthly_success_rate)

    if line_data:
        line_data = pd.concat(line_data)
        fig = px.line(
            line_data,
            x="month",
            y="jump_success",
            color="skater_name",
            title="Évolution du taux de réussite selon les mois",
        )
        st.plotly_chart(fig)
    else:
        st.write("Désolé, il n'y a pas de données à afficher.")


if "logged_in" in st.session_state:
    if st.session_state.logged_in:
        access = st.session_state.user["access"]
        role = st.session_state.user["role"]
        jumps = st.session_state.jumps

        # Add a jump_type filter
        jump_types = []
        for jump in jumps:
            jump_types.extend(jump["jump_type"].unique())
        jump_types = list(set(jump_types))
        selected_jump_type = st.sidebar.selectbox(
            "Sélectionner un type de saut", jump_types
        )

        # Add an angular_velocity column
        for jump in jumps:
            jump["angular_velocity"] = jump["jump_rotations"] / jump["jump_length"]

        for jump in jumps:
            jump["jump_rotations"] = jump.apply(
                lambda row: (
                    math.floor(row["jump_rotations"])
                    if row["jump_type"] == "AXEL"
                    and str(row["jump_rotations"]).endswith(".5")
                    else row["jump_rotations"]
                ),
                axis=1,
            )

        # Add a jump_rotations filter
        jump_rotations = []
        for jump in jumps:
            jump_rotations.extend(jump["jump_rotations"].unique())
        jump_rotations = list(set(jump_rotations))
        selected_jump_rotations = st.sidebar.selectbox(
            "Sélectionner un nombre de rotations", jump_rotations
        )

        # Filter the datasets
        filtered_datasets = []
        for jump in jumps:
            filtered_jump = jump[
                (jump["jump_type"] == selected_jump_type)
                & 
                (jump["jump_rotations"] == selected_jump_rotations)
            ]
            filtered_datasets.append(filtered_jump)
        
        create_radar_athletes(filtered_datasets)
        create_line_chart(filtered_datasets)
        # create_radar_types(filtered_datasets)

    else:
        st.error("Vous devez être connecté pour accéder à cette page.")
        st.stop()

else:
    st.error("Vous devez être connecté pour accéder à cette page.")
    st.stop()
