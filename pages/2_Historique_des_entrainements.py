import math
from datetime import datetime

import pandas as pd
import streamlit as st

from database.DatabaseManager import DatabaseManager

db_manager = DatabaseManager()


def color_background(val):
    if val == "":
        return ""
    val = float(val.strip("%"))  # Convertir le pourcentage en nombre flottant
    if val >= 85:
        color = "#1a9641"
    elif val >= 60:
        color = "#ffff5f"
    else:
        color = "#d7191c"
    return f"background-color: {color}"


def create_recap_frame(data):
    # Création du DataFrame récapitulatif : une colonne par type de saut, une ligne par nombre de rotations (1, 2, 3 et 4). Dans les cases, le pourcentage de réussite d'un tel saut (type + rotations)
    recap = pd.DataFrame(index=[1, 2, 3, 4], columns=data["jump_type"].unique())
    # Arrondir les jump_rotations à l'entier inférieur (pour les jump_type == AXEL)
    data["jump_rotations"] = data.apply(
        lambda row: (
            math.floor(row["jump_rotations"])
            if row["jump_type"] == "AXEL" and str(row["jump_rotations"]).endswith(".5")
            else row["jump_rotations"]
        ),
        axis=1,
    )
    for jump_type in data["jump_type"].unique():
        for rotations in [1, 2, 3, 4]:
            # Calcul du pourcentage de réussite
            success_rate = data[
                (data["jump_type"] == jump_type) & (data["jump_rotations"] == rotations)
            ]["jump_success"].mean()
            # Laisser la case vide si aucune donnée n'est disponible
            if pd.isna(success_rate):
                success_rate = ""
            # Remplir la case du DataFrame récapitulatif en pourcentage (bien ecrire le signe %)
            recap.loc[rotations, jump_type] = (
                f"{success_rate:.0%}" if success_rate != "" else ""
            )
    # Affichage du DataFrame récapitulatif
    styled_recap = recap.style.applymap(color_background)

    st.markdown(
        "### Pourcentage de réussite par type de saut et par nombre de rotations"
    )
    st.write(styled_recap)


if "logged_in" in st.session_state:
    if st.session_state.logged_in:
        if st.session_state.user["role"] == "COACH":
            selected_skater = st.sidebar.selectbox(
                "Sélectionner un athlète", st.session_state.skater_names
            )
            if not selected_skater:
                st.error("Aucun athlète sélectionné.")
                st.stop()

        elif st.session_state.user["role"] == "ATHLETE":
            selected_skater = st.session_state.user["name"]

        for i in st.session_state.jumps:
            if selected_skater == i["skater_name"][0]:
                jumps = i
                break
        create_recap_frame(jumps)
    else:
        st.error("Vous devez être connecté pour accéder à cette page.")
        st.stop()
else:
    st.error("Vous devez être connecté pour accéder à cette page.")
    st.stop()
