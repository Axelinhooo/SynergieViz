import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts
import plotly.graph_objects as go
from datetime import datetime

def data_import():
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        st.write(data)
        return data

def create_histogram(data):
    # Create the hstacked vertical bar chart using streamlit_echarts
    # Compter le nombre de réussites et d'échecs par type de saut
    jump_stats = data.groupby('type')['success'].value_counts().unstack(fill_value=0)

    # Préparer les données pour le graphique
    x_axis = list(jump_stats.index)
    success_data = jump_stats[1].tolist()
    fail_data = jump_stats[0].tolist()

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
    df['videoTimestamp'] = df['videoTimeStamp'].apply(lambda x: datetime.strptime(x, '%M:%S'))

    # Création du graphique Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['videoTimestamp'],
        y=df['rotations'],
        mode='markers',
        marker=dict(
            color=df['success'].map({0: 'red', 1: 'green'}),
            size=10
        ),
        text=df.apply(lambda row: f"Patineur: {row['skater_name']}<br>Type de saut: {row['type']}<br>Réussi: {row['success']}<br>Rotations: {row['rotations']}<br>Timestamp: {row['videoTimeStamp']}", axis=1),
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

data = data_import()
if data is not None:
    create_histogram(data)
    create_timeline(data)