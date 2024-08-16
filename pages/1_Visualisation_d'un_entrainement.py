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
    fig.add_trace(go.Scatter(
        x=df['jump_time'],
        y=df['jump_rotations'],
        mode='markers',
        marker=dict(
            color=df['jump_success'].map({False: 'red', True: 'green'}),
            size=10
        ),
        text=df.apply(lambda row: f"Type de saut: {row['jump_type']}<br>Réussi: {row['jump_success']}<br>Rotations: {row['jump_rotations']}<br>Timestamp: {row['jump_time']}", axis=1),
        hoverinfo='text'
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
        selected_skater = st.sidebar.selectbox("Select a skater", st.session_state.skater_names)
        if selected_skater:
            # Find the corresponding skater ID based on the selected name
            selected_skater_id = st.session_state.skater_ids[st.session_state.skater_names.index(selected_skater)]
        else:
            st.error("Aucun athlète sélectionné.")
            st.stop()
        
        skater_index = st.session_state.skater_ids.index(selected_skater_id)
        
    elif st.session_state.user['role'] == 'ATHLETE':
        skater_index = 0

    trainings = st.session_state.trainings[skater_index]
    for date in trainings["training_date"]:
        date = datetime.fromtimestamp(date)
    training_dates = [datetime.fromtimestamp(date) for date in trainings["training_date"]]
    # Selectbox to choose the date of the training
    selected_date = st.sidebar.selectbox("Select a training", training_dates)
    # Get the training_id of the selected training
    selected_training = trainings[trainings["training_date"] == selected_date.timestamp()]
    selected_training_id = selected_training["training_id"].values[0]
    
    # Create a DataFrame for the jumps of the selected training with data inside (from st.session_state.jumps) to create the histogram and the timeline
    jumps = st.session_state.jumps[skater_index]
    selected_jumps = jumps[jumps["training_id"] == selected_training_id]
    create_histogram(selected_jumps)
    create_timeline(selected_jumps)

    

        


    
else:
    st.error("Vous devez être connecté pour accéder à cette page.")
    st.stop()