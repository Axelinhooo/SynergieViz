import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts
import plotly.graph_objects as go
from datetime import datetime

def create_histogram(data):
    # Vérifier la présence des colonnes 'jump_type' et 'jump_success' (tableau incomplet)
    if 'jump_type' not in data.columns or 'jump_success' not in data.columns:
        st.error("Cet entraînement ne contient pas les informations nécessaires.")
        return
    
    # Compter le nombre de réussites et d'échecs par type de saut (réussite : jump_success = 'true', échec : jump_success = 'false')
    jump_stats = data.groupby(['jump_type', 'jump_success']).size().unstack(fill_value=0)

    # Vérifier la présence des colonnes True et False
    if True not in jump_stats.columns:
        jump_stats[True] = 0
    if False not in jump_stats.columns:
        jump_stats[False] = 0

    # Préparer les données pour le graphique
    x_axis = jump_stats.index.tolist()
    success_data = jump_stats[True].tolist()
    fail_data = jump_stats[False].tolist()


    options = {
        "title": {"text": "Répartition des sauts par type"},
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
        "xAxis": {"type": "category", "data": x_axis},
        "yAxis": {"type": "value"},
        "series": [
            {
                "name": "Réussi",
                "type": "bar",
                "stack": "total",
                "label": {"show": True},
                "emphasis": {"focus": "series"},
                "data": success_data,
                "color": "green"
            },
            {
                "name": "Chute",
                "type": "bar",
                "stack": "total",
                "label": {"show": True},
                "emphasis": {"focus": "series"},
                "data": fail_data,
                "color": "red"
            }
        ]
    }
    # add an on click event to the chart
    options["events"] = [{"click": "function(params) {alert('You clicked on ' + params.value)}"}]

    st_echarts(options, height="500px")
    


        
def create_timeline(df):
    # Conversion des timestamps en objets datetime
    df['jump_time'] = df['jump_time'].apply(lambda x: datetime.strptime(x, '%M:%S'))

    # Création du graphique Plotly
    fig = go.Figure()

    # Dictionnaire pour les couleurs des sauts
    colors = {
        'TOE_LOOP': '#1b9e77',
        'SALCHOW': '#d95f02',
        'LOOP': '#7570b3',
        'FLIP': '#e7298a',
        'LUTZ': '#66a61e',
        'AXEL': '#e6ab02'
    }

    for jump_type, color in colors.items():
        filtered_df = df[df['jump_type'] == jump_type]
        fig.add_trace(go.Scatter(
            x=filtered_df['jump_time'],
            y=filtered_df['jump_rotations'],
            mode='markers',
            marker=dict(
                color=color,
                symbol=filtered_df['jump_success'].map({False: 'x', True: 'circle'}),
                size=10
            ),
            text=filtered_df.apply(lambda row: f"Type de saut: {row['jump_type']}<br>Réussi: {row['jump_success']}<br>Rotations: {row['jump_rotations']}<br>Timestamp: {row['jump_time']}", axis=1),
            hoverinfo='text',
            name=jump_type,  # Nom de la trace pour la légende
            showlegend=True
        ))

    # Conversion de l'axe des abscisses en format de temps
    fig.update_xaxes(tickformat="%M:%S")

    fig.update_layout(
        xaxis_title='Timestamp (min:sec)',
        yaxis_title='Rotations',
        title='Timeline de l\'entrainement'
    )

    # Affichage du graphique dans Streamlit
    st.plotly_chart(fig)



if st.session_state.logged_in:
    if st.session_state.user['role'] == 'COACH':
        # Create the Streamlit selectbox
        selected_skater = st.sidebar.selectbox("Selectionnez un athlète", st.session_state.skater_names)
        if not selected_skater:
            st.error("Aucun athlète sélectionné.")
            st.stop()

    elif st.session_state.user['role'] == 'ATHLETE':
        selected_skater = st.session_state.user['name']

    for i in st.session_state.jumps:
        if selected_skater == i["skater_name"][0]:
            jumps = i
            break
    # convert the timestamps in the column to datetime objects
    jumps["training_date"] = pd.to_datetime(jumps["training_date"], unit="s")

    training_dates = jumps["training_date"].unique().tolist()
    # Selectbox to choose the date of the training
    selected_date = st.sidebar.selectbox("Selectionnez un entraînement", training_dates)
    selected_jumps = jumps[jumps["training_date"] == selected_date]
    create_histogram(selected_jumps)
    create_timeline(selected_jumps)

    

        


    
else:
    st.error("Vous devez être connecté pour accéder à cette page.")
    st.stop()