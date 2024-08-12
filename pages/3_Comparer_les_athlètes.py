import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts
from features.dataImport import data_import_multiple

# Choisir les datasets
datasets = data_import_multiple()

# Récupérer les types de sauts communs à tous les datasets
common_types = set(datasets[0]['type'].unique())
for data in datasets[1:]:
    common_types = common_types.intersection(set(data['type'].unique()))
common_types = list(common_types)

# Afficher la selectbox avec les types communs
selected_type = st.sidebar.selectbox("Type de saut", common_types)

# Filtrer les données sur le type de saut sélectionné
filtered_datasets = [data[data['type'] == selected_type] for data in datasets]

# Créer le graphique radar
def create_radar(filtered_datasets):
    option = {
        "legend": {"data": [str(data['skater_name'].unique()[0]) for data in filtered_datasets]},
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
        "series": [
            {
                "name": "Athlètes",
                "type": "radar",
                "data": [
                    {
                        "value": [
                            int(data.shape[0]),
                            round(float(data['success'].mean()),1)*100,
                            3.2,
                            0.5,
                            42,
                        ],
                        "name": str(data['skater_name'].unique()[0]),
                    }
                    for data in filtered_datasets
                ],
            }
        ],
    }
    st_echarts(option, height="500px")

create_radar(filtered_datasets)