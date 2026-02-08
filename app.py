import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit as st

import sqlite3

#@st.cache_resource
def get_db_connection():
    con = sqlite3.connect("WindTunnel.db")
    return con

con = get_db_connection()

@st.cache_data
def get_param_list(_con):
     query = """SELECT group_concat(name, '|') FROM pragma_table_info('TestDetailed');"""
     df = pd.read_sql_query(query, _con)
     paramList = df.iloc[0,0].split("|")
     return paramList

paramList = get_param_list(con)
paramList  = tuple(set(paramList) - set(['id']))


independentVars = ('FrontRideHeight', 'RearRideHeight', 'aFW', 'aRW', 'BGurney', 'FreeStreamVelocity', 'RoadSpeed', 'AmbientTemperature', 'AmbientPressure')
dependentVars  = tuple(set(paramList) - set(independentVars))

query = """SELECT DISTINCT RunId FROM TestDetailed;"""
df = pd.read_sql_query(query, con)
runList = df['RunId'].tolist()

st.sidebar.write("Select x and y variables")

xSelection = st.sidebar.selectbox(
    'Select x axis',
    paramList, index=0)

ySelection = st.sidebar.selectbox(
    'Select y axis',
    dependentVars, index=0)

overLayBy = st.sidebar.selectbox(
    'Select variable to overlay by',
    independentVars, index=0)

xyzSelection = (xSelection, ySelection, overLayBy)
allColumns = xyzSelection + independentVars
uniqueList = list(dict.fromkeys(allColumns))

query = f"""SELECT {', '.join(uniqueList)} FROM TestDetailed;"""
df = pd.read_sql_query(query, con)
df = df.round(1)

st.sidebar.write("Filter data")

for i in range(0, len(allColumns)):
    col = allColumns[i]
    if not col in xyzSelection and len(df[col].unique()) > 1:
        BFilter = st.sidebar.checkbox(
            f'Filter by {col}',
            value=False,
            key=f'filter_checkbox_{col}'
        )
        if BFilter:
            filterValue = st.sidebar.selectbox(
            f'Select {col} to filter by',
            options=df[col].unique(),
            key=f'filter_value_{col}'
            )
            df = df[df[col] == filterValue]

fig = px.line(
    df,
    x=xSelection,
    y=ySelection,
    color=overLayBy
)

st.plotly_chart(fig, use_container_width=True)

st.write(df)

con.close()