# DATASET: https://www.kaggle.com/datasets/imdevskp/corona-virus-report

import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px


# ---------------- Functions ----------------
def formateo(lista):
    newformat=[]
    for elemento in lista: 
        newformat.append(elemento[0])
    return newformat

def listToCSV(lista):
    string=""
    for element in lista:
        string = string + element + ", "
    string = string[:-2]
    return string

# Page init config
st.set_page_config(page_title="Covid Statistics Worldwide",
                    page_icon=":bar_chart:",
                    layout="wide")

# ---------------- SQL CONNECTION ----------------
# Initialize connection.
# Uses st.experimental_singleton to only run once.
@st.experimental_singleton
def init_connection():
    return mysql.connector.connect(**st.secrets["mysql"])

conn = init_connection()

# Perform query.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
@st.experimental_memo(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

# ---------------- Running Web app below ----------------
rows = run_query("SELECT * from covid2;")

regiones = run_query("SELECT DISTINCT Region from covid2;")
# [('Eastern Mediterranean',), ('Europe',), ('Africa',), ('Americas',), ('Western Pacific',), ('South-East Asia',)]

regionesf = formateo(regiones)

st.header("Please filter here:")
row13_spacer1, row13_1, row13_spacer2, row13_2, row13_spacer3, row13_3, row13_spacer4   = st.columns((.2, 2.3, .2, 2.3, .2, 2.3, .2))
with row13_1:
    continent = st.selectbox(
    "Select the continent:",
    options=sorted(regionesf),
    index=5
    )
with row13_2:
    filtering = st.multiselect(
    "Select the information:",
    options=["confirmed", "deaths", "recovered"],
    default=["confirmed", "deaths", "recovered"]
    )
with row13_3:
    chart_type = st.selectbox(
    'Pick your type of chart', 
    options=['Horizontal chart', 'Vertical chart 1', 'Vertical chart 2']
    )

paises = run_query(f"SELECT `Country/Region` from covid2 where Region = '{continent}';")

if filtering != []:
    info = run_query(f"SELECT {listToCSV(filtering)} from covid2 where Region = '{continent}';")
    paises = formateo(paises)
    chart_data = pd.DataFrame(
                info,
                index=paises,
                columns=filtering           
    )

    queries = listToCSV(filtering)
    df = pd.read_sql_query(f"SELECT `Country/Region`, {queries} from covid2 where Region = '{continent}';",conn)
    
    if chart_type=="Horizontal chart":
        fig = px.bar(df, y="Country/Region", x=filtering, title="Covid Cases", width=1400, height=700)
        st.plotly_chart(fig)
    elif chart_type=="Vertical chart 1":
        fig = px.bar(df, x="Country/Region", y=filtering, title="Covid Cases", width=1400, height=600)
        st.plotly_chart(fig)
    elif chart_type=="Vertical chart 2":
        st.title("Covid Cases")
        st.bar_chart(chart_data, height=650) 
else:
    st.write("Select some information to be displayed!")
    info=[]
