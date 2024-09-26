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
    # Dégradé : 100% -> #00d900, 0% -> #d90000, 50% -> #d9d900 : faire le dégradé entre les couleurs
    r = int(217 - (217 * val) / 100)
    g = int(217 * val / 100)
    b = 0
    return f"background-color: #{r:02x}{g:02x}{b:02x}"

def test_color_background():
    # Faire un tableau avec des valeurs de 0 à 100 par pas de 10
    test_df = pd.DataFrame(
        {
            "0": [f"{i}%" for i in range(0, 101, 10)],
            "1": [f"{i}%" for i in range(0, 101, 10)],
            "2": [f"{i}%" for i in range(0, 101, 10)],
            "3": [f"{i}%" for i in range(0, 101, 10)],
        }
    )
    # Appliquer la fonction color_background à chaque cellule du DataFrame
    styled_test_df = test_df.style.applymap(color_background)
    return styled_test_df


def create_recap_frame(data):
    # Création du DataFrame récapitulatif : une colonne par type de saut, une ligne par nombre de rotations (Simple, Double, Triple, Quad)
    recap = pd.DataFrame(index=["Simple", "Double", "Triple", "Quad"], columns=data["jump_type"].unique())
    
    # Arrondir les jump_rotations à l'entier inférieur (pour les jump_type == AXEL)
    data["jump_rotations"] = data.apply(
        lambda row: (
            math.floor(row["jump_rotations"])
            if row["jump_type"] == "AXEL" and str(row["jump_rotations"]).endswith(".5")
            else row["jump_rotations"]
        ),
        axis=1,
    )
    
    # Dictionnaire pour mapper les noms des rotations
    rotation_mapping = {1: "Simple", 2: "Double", 3: "Triple", 4: "Quad"}

    for jump_type in data["jump_type"].unique():
        for rotations in [1, 2, 3, 4]:
            # Calcul du pourcentage de réussite
            success_rate = data[
                (data["jump_type"] == jump_type) & (data["jump_rotations"] == rotations)
            ]["jump_success"].mean()
            # Laisser la case vide si aucune donnée n'est disponible
            if pd.isna(success_rate):
                success_rate = ""
            # Remplir la case du DataFrame récapitulatif en pourcentage (bien écrire le signe %)
            recap.loc[rotation_mapping[rotations], jump_type] = (
                f"{success_rate:.0%}" if success_rate != "" else ""
            )

    # Classer les colonnes : Axel, Salchow, Toe Loop, Loop, Flip, Lutz
    recap = recap[
        [
            "AXEL",
            "SALCHOW",
            "TOE_LOOP",
            "LOOP",
            "FLIP",
            "LUTZ",
        ]
    ]
    
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
